#!/usr/bin/env python3
"""Small offline continuity ledger. All entries are claims, never authorization."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

AXES = {
    "workflow": {"draft", "submitted", "closed"},
    "disposition": {"pending", "accepted", "rejected"},
    "payment": {"unpaid", "paid"},
    "duplicate": {"unknown", "unique", "duplicate"},
    "validity": {"unknown", "valid", "invalid"},
    "slots": {"available", "unavailable"},
}
KINDS = {"observation", "interpretation", "decision", "execution", "verification",
         "collection_failure", "request", "answer", "handoff", "correction"}
ZERO = "0" * 64
MAX_BYTES = 2_000_000
MAX_EVENTS = 1000
REOPEN = "all-recorded-grounds-changed-by-fresh-observations"
NOTICE = ("Actor labels are unauthenticated claims. Answers and verifications do "
          "not authenticate a human, establish source truth, or grant permission.")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names), "Missing or unknown fields")


def token(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", value),
            "Invalid identifier")


def prose(value):
    require(isinstance(value, str) and 0 < len(value) <= 2000 and value.strip()
            and not any(ord(c) < 32 for c in value), "Invalid one-line text")


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value),
            "Timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError("Invalid calendar timestamp") from exc


def evidence(value):
    require(isinstance(value, str) and re.fullmatch(r"opaque:[a-zA-Z0-9_-]{1,80}", value),
            "Evidence must be an opaque reference; it is never dereferenced")


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON field")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("Non-finite JSON number: " + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def dependencies(events):
    return {digest(e): set(e["depends_on"]) for e in events}


def closure(seeds, graph):
    result = set(seeds)
    while True:
        more = {eid for eid, deps in graph.items() if deps & result} - result
        if not more:
            return result
        result.update(more)


def invalidations(events):
    graph = dependencies(events)
    causes = {}
    for event in events:
        if event["kind"] == "correction":
            for eid in closure({event["data"]["target"]}, graph):
                causes.setdefault(eid, []).append(digest(event))
    return causes


def axis_state(events, case, axis, at, invalid):
    rows = [(e["data"]["observed_at"], n, e) for n, e in enumerate(events)
            if e["case"] == case and e["kind"] == "observation" and e["data"]["axis"] == axis]
    if not rows:
        return {"state": "unobserved", "current_value": None, "last_observation": None}
    observed, index, event = max(rows, key=lambda row: row[:2])
    d = event["data"]
    last = {"id": digest(event), **d}
    state = "fresh"
    if digest(event) in invalid:
        state = "needs_review"
    elif at >= d["valid_until"]:
        state = "stale"
    elif any(e["case"] == case and e["kind"] == "collection_failure"
             and e["data"]["axis"] == axis
             and (e["data"]["attempted_at"], n) > (observed, index)
             for n, e in enumerate(events)):
        state = "collection_failed"
    return {"state": state, "current_value": d["value"] if state == "fresh" else None,
            "last_observation": last}


def negative_eligible(negative, axes, by_id):
    # Grounds are ORs of ANDs. Every sufficient ground must have a changed member.
    return all(any(
        axes[by_id[p]["data"]["axis"]]["state"] == "fresh"
        and axes[by_id[p]["data"]["axis"]]["current_value"] != by_id[p]["data"]["value"]
        and axes[by_id[p]["data"]["axis"]]["last_observation"]["observed_at"]
            > by_id[p]["data"]["observed_at"]
        for p in ground) for ground in negative["data"]["grounds"])


def premise_signature(request, by_id):
    return {by_id[p]["data"]["axis"]: by_id[p]["data"]["value"]
            for p in request["depends_on"]}


def project(events, at, tip=ZERO):
    """Pure projection of a validated prefix at an explicit time, with no clock reads."""
    timestamp(at)
    require(not events or at >= events[-1]["recorded_at"], "Projection time predates log tip")
    by_id = {digest(e): e for e in events}
    invalid = invalidations(events)
    graph = dependencies(events)
    cases = {}
    review = set(invalid)
    for case in sorted({e["case"] for e in events}):
        axes = {a: axis_state(events, case, a, at, invalid) for a in AXES}
        cases[case] = {"axes": axes, "plans": [], "executions": [], "notes": [],
                       "handoffs": [], "collection_failures": []}
        review.update(s["last_observation"]["id"] for s in axes.values()
                      if s["last_observation"] and s["state"] != "fresh")
    for e in events:
        if e["kind"] == "observation":
            latest = cases[e["case"]]["axes"][e["data"]["axis"]]
            if at >= e["data"]["valid_until"] or (
                    latest["state"] == "fresh" and latest["current_value"] != e["data"]["value"]):
                review.add(digest(e))
    review = closure(review, graph)
    actions, negatives = [], []
    for e in events:
        eid, d, case = digest(e), e["data"], e["case"]
        row = cases[case]
        if e["kind"] == "interpretation":
            row["notes"].append({"id": eid, "claim": d["claim"],
                                 "state": "review_required" if eid in review else "recorded"})
        elif e["kind"] == "decision" and d["type"] == "plan":
            row["plans"].append({"id": eid, "action": d["action"], "state": "planned",
                                 "needs_review": eid in review})
        elif e["kind"] == "execution":
            checks = [v for v in events if v["kind"] == "verification"
                      and v["data"]["execution_id"] == eid and digest(v) not in review]
            latest = max(checks, key=lambda v: (v["data"]["checked_at"], events.index(v)),
                         default=None)
            row["executions"].append({"id": eid, "action": d["action"],
                                      "executed_at": d["executed_at"],
                                      "verification": latest["data"]["verdict"] if latest else "unverified",
                                      "needs_review": eid in review})
        elif e["kind"] == "collection_failure":
            row["collection_failures"].append({"id": eid, **d})
        elif e["kind"] == "handoff":
            standing = "review_required" if eid in review else "recorded"
            row["handoffs"].append({"id": eid, "summary": d["summary"], "state": standing})
            if eid in review:
                actions.append({"case": case, "id": eid, "action": "review_handoff"})
        elif e["kind"] == "decision" and d["type"] == "negative":
            eligible = negative_eligible(e, row["axes"], by_id)
            reopenings = [r for r in events if r["kind"] == "decision"
                          and r["data"]["type"] == "reopen" and r["data"]["negative_id"] == eid]
            valid_reopening = any(digest(r) not in review for r in reopenings)
            standing = ("reopened_for_review" if eligible and valid_reopening else
                        "reopen_eligible" if eligible else
                        "review_required" if eid in review or reopenings else "held")
            negatives.append({"case": case, "id": eid, "reason": d["reason"],
                              "grounds": d["grounds"], "reopen_when": d["reopen_when"],
                              "standing": standing})
            if standing in {"review_required", "reopen_eligible"}:
                actions.append({"case": case, "id": eid, "action": "review_negative"})
    requests = {}
    for e in events:
        if e["kind"] == "request":
            requests.setdefault((e["case"], e["data"]["question_key"]), []).append(e)
    request_view = []
    for (case, key), group in sorted(requests.items()):
        e = group[-1]
        eid = digest(e)
        axes = cases[case]["axes"]
        expected = premise_signature(e, by_id)
        answers = [a for a in events if a["kind"] == "answer" and a["case"] == case
                   and a["data"]["request_id"] in {digest(r) for r in group}]
        matching = [a for a in answers
                    if premise_signature(by_id[a["data"]["request_id"]], by_id) == expected]
        material_change = any(axes[axis]["state"] == "fresh"
                              and axes[axis]["current_value"] != value
                              for axis, value in expected.items())
        # Missing/stale/failed evidence prompts review, never a silently repeated question.
        unavailable = any(axes[axis]["state"] != "fresh" for axis in expected)
        state = ("premise_changed" if material_change or (answers and not matching) else
                 "answer_needs_review" if matching and
                     (unavailable or all(digest(a) in review for a in matching)) else
                 "answered_recorded" if matching else "pending")
        request_view.append({"case": case, "id": eid, "question_key": key,
                             "question": e["data"]["question"], "state": state,
                             "answer_ids": [digest(a) for a in matching]})
        if state != "answered_recorded":
            actions.append({"case": case, "id": eid,
                            "action": "review_answer" if state == "answer_needs_review" else "respond",
                            "question_key": key, "reason": state})
    return {"version": 1, "as_of": at, "ledger_tip": tip, "trust_notice": NOTICE,
            "cases": cases, "negatives": negatives, "requests": request_view,
            "unresolved_human_actions": actions,
            "invalidated": [{"id": eid, "correction_ids": ids}
                            for eid, ids in sorted(invalid.items())]}


def validate_event(event, prior):
    fields(event, {"version", "key", "case", "kind", "recorded_at", "actor_claim", "depends_on", "data"})
    require(type(event["version"]) is int and event["version"] == 1, "Unsupported event version")
    token(event["key"]); token(event["case"]); prose(event["actor_claim"])
    timestamp(event["recorded_at"])
    require(isinstance(event["kind"], str) and event["kind"] in KINDS, "Unknown event kind")
    deps = event["depends_on"]
    require(isinstance(deps, list) and all(isinstance(p, str) for p in deps)
            and len(deps) == len(set(deps)), "Invalid dependency list")
    require(isinstance(event["data"], dict), "Event data must be an object")
    by_id = {digest(e): e for e in prior}
    require(all(p in by_id for p in deps), "Missing, forward, or self dependency")
    require(all(by_id[p]["case"] == event["case"] for p in deps), "Cross-case dependency unsupported")
    require(not prior or event["recorded_at"] >= prior[-1]["recorded_at"], "Backdated recording")
    kind, d, at = event["kind"], event["data"], event["recorded_at"]
    invalid = invalidations(prior)
    if kind not in {"correction", "decision"} or d.get("type") != "reopen":
        require(not set(deps) & set(invalid), "Dependency already invalidated; reauthor after review")
    def reference(eid, required_kind):
        require(isinstance(eid, str) and eid in by_id and by_id[eid]["kind"] == required_kind
                and by_id[eid]["case"] == event["case"], "Invalid typed reference")
        return by_id[eid]
    if kind == "observation":
        fields(d, {"axis", "value", "observed_at", "valid_until", "evidence_ref"})
        require(isinstance(d["axis"], str) and d["axis"] in AXES and
                isinstance(d["value"], str) and d["value"] in AXES[d["axis"]], "Invalid axis or value")
        timestamp(d["observed_at"]); timestamp(d["valid_until"]); evidence(d["evidence_ref"])
        require(d["observed_at"] <= at and d["valid_until"] > d["observed_at"], "Invalid observation window")
        require(not deps, "Observations are raw claims; derived claims use interpretation")
    elif kind == "interpretation":
        fields(d, {"claim"}); prose(d["claim"]); require(deps, "Interpretation needs declared grounds")
    elif kind == "decision":
        require(d.get("type") in {"plan", "negative", "reopen"}, "Unknown decision type")
        if d["type"] == "plan":
            fields(d, {"type", "action"}); prose(d["action"])
        elif d["type"] == "negative":
            fields(d, {"type", "reason", "grounds", "reopen_when"}); prose(d["reason"])
            require(d["reopen_when"] == REOPEN, "Explicit supported reopen condition required")
            grounds = d["grounds"]
            require(isinstance(grounds, list) and grounds and all(
                isinstance(g, list) and g and all(isinstance(p, str) for p in g)
                and len(g) == len(set(g)) for g in grounds), "Invalid sufficient grounds")
            require(set(deps) == {p for g in grounds for p in g}, "Grounds/dependencies mismatch")
            require(len({canonical(sorted(g)) for g in grounds}) == len(grounds), "Duplicate grounds")
            axes = project(prior, at)["cases"].get(event["case"], {}).get("axes", {})
            for p in deps:
                premise = reference(p, "observation")
                current = axes[premise["data"]["axis"]]
                require(current["state"] == "fresh" and current["last_observation"]["id"] == p,
                        "Negative needs current fresh premises")
        else:
            fields(d, {"type", "negative_id", "reason"}); prose(d["reason"])
            negative = reference(d["negative_id"], "decision")
            require(negative["data"]["type"] == "negative", "Reopen must name a negative")
            require(deps and all(by_id[p]["kind"] == "observation" for p in deps),
                    "Reopen needs fresh observation dependencies")
            view = project(prior, at)
            axes = view["cases"][event["case"]]["axes"]
            require(negative_eligible(negative, axes, by_id), "No sufficient material premise change")
            changed_ids = {axes[by_id[p]["data"]["axis"]]["last_observation"]["id"]
                           for p in negative["depends_on"]
                           if axes[by_id[p]["data"]["axis"]]["state"] == "fresh"
                           and axes[by_id[p]["data"]["axis"]]["current_value"] != by_id[p]["data"]["value"]}
            require(changed_ids <= set(deps), "Reopen must cite changed premises")
    elif kind == "execution":
        fields(d, {"action", "executed_at", "evidence_ref"})
        prose(d["action"]); timestamp(d["executed_at"]); evidence(d["evidence_ref"])
        require(d["executed_at"] <= at, "Execution time is in the future")
    elif kind == "verification":
        fields(d, {"execution_id", "verdict", "checked_at", "evidence_ref"})
        execution = reference(d["execution_id"], "execution")
        require(d["execution_id"] in deps and d["verdict"] in {"pass", "fail"},
                "Verification needs execution dependency and verdict")
        timestamp(d["checked_at"]); evidence(d["evidence_ref"])
        require(execution["data"]["executed_at"] <= d["checked_at"] <= at, "Invalid verification time")
    elif kind == "collection_failure":
        fields(d, {"axis", "attempted_at", "error_code"})
        require(isinstance(d["axis"], str) and d["axis"] in AXES and d["error_code"]
                in {"timeout", "unavailable", "denied", "malformed"}, "Invalid collection failure")
        timestamp(d["attempted_at"])
        require(d["attempted_at"] <= at and not deps, "Invalid failure time or dependencies")
    elif kind == "request":
        fields(d, {"question_key", "question"}); token(d["question_key"]); prose(d["question"])
        for p in deps:
            reference(p, "observation")
        require(len({by_id[p]["data"]["axis"] for p in deps}) == len(deps), "Repeated request premise axis")
        previous = [e for e in prior if e["kind"] == "request" and e["case"] == event["case"]
                    and e["data"]["question_key"] == d["question_key"]]
        require(all(e["data"]["question"] == d["question"] for e in previous),
                "Semantic question key reused with different question")
        signature = premise_signature(event, by_id)
        require(all(set(premise_signature(e, by_id)) == set(signature) for e in previous),
                "Question premise axes changed; use a new question key")
        axes = project(prior, at)["cases"].get(event["case"], {}).get("axes", {})
        require(all(axes[a]["state"] == "fresh" and axes[a]["current_value"] == value
                    for a, value in signature.items()), "Request uses obsolete or unavailable premises")
    elif kind == "answer":
        fields(d, {"request_id", "response"}); prose(d["response"])
        reference(d["request_id"], "request")
        require(d["request_id"] in deps, "Answer must cite request")
    elif kind == "handoff":
        fields(d, {"summary"}); prose(d["summary"]); require(deps, "Handoff needs declared dependencies")
    elif kind == "correction":
        fields(d, {"target", "replacement", "reason"}); prose(d["reason"])
        require(not deps, "Corrections use explicit target/replacement references")
        require(all(isinstance(d[p], str) and d[p] in by_id for p in ("target", "replacement")),
                "Correction target or replacement missing")
        old, new = by_id[d["target"]], by_id[d["replacement"]]
        require(old["case"] == new["case"] == event["case"] and old["kind"] == new["kind"]
                and old["kind"] not in {"correction", "collection_failure"},
                "Incompatible correction; correction retraction unsupported")
        require(list(by_id).index(d["target"]) < list(by_id).index(d["replacement"])
                and d["replacement"] not in invalid, "Replacement must be later and active")
        require(not any(e["kind"] == "correction" and e["data"]["target"] == d["target"] for e in prior),
                "Target already replaced")
        require(d["replacement"] not in closure({d["target"]}, dependencies(prior)),
                "Replacement depends on target")
        if old["kind"] == "observation":
            require(old["data"]["axis"] == new["data"]["axis"]
                    and new["data"]["observed_at"] >= old["data"]["observed_at"],
                    "Correction must replace same axis without backdating")
        if old["kind"] == "decision":
            require(old["data"]["type"] == new["data"]["type"], "Decision types differ")


def records_from_events(events):
    records, prior, keys = [], [], set()
    for event in events:
        require(len(prior) < MAX_EVENTS, "Event limit reached")
        validate_event(event, prior)
        require(event["key"] not in keys, "Duplicate idempotency key in log")
        keys.add(event["key"])
        body = {"seq": len(records) + 1, "prev": records[-1]["record_hash"] if records else ZERO,
                "event_id": digest(event), "event": copy.deepcopy(event)}
        records.append({**body, "record_hash": digest(body)})
        prior.append(event)
    return records


def decode_log(raw):
    require(len(raw) <= MAX_BYTES, "Ledger byte limit exceeded")
    require(not raw or raw.endswith(b"\n"), "Incomplete final record; repair explicitly")
    records = [strict_json(line) for line in raw.decode("utf-8").splitlines()]
    for r in records:
        fields(r, {"seq", "prev", "event_id", "event", "record_hash"})
        require(type(r["seq"]) is int, "Sequence must be integer")
    expected = records_from_events([r["event"] for r in records])
    require(records == expected, "Record identity, sequence, or hash chain mismatch")
    return records


def open_regular(path, flags):
    fd = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        require(stat.S_ISREG(os.fstat(fd).st_mode), "Ledger must be a regular file")
        return os.fdopen(fd, "r+b" if flags & os.O_RDWR else "rb")
    except BaseException:
        os.close(fd)
        raise


def load(path):
    with open_regular(path, os.O_RDONLY) as stream:
        return decode_log(stream.read(MAX_BYTES + 1))


def append(path, event, expected_id=None):
    """Cooperating local writers only; rejected commands write no record bytes."""
    require(isinstance(event, dict), "Event must be an object")
    require(expected_id is None or expected_id == digest(event), "Claimed eventID changed payload")
    with open_regular(path, os.O_RDWR | os.O_CREAT) as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Ledger busy; retry the same event") from exc
        records = decode_log(stream.read(MAX_BYTES + 1))
        existing = next((r for r in records if r["event"]["key"] == event.get("key")), None)
        if existing:
            require(existing["event_id"] == digest(event), "Idempotency key reused with changed payload")
            return existing["event_id"], False
        new = records_from_events([r["event"] for r in records] + [event])[-1]
        line = (canonical(new) + "\n").encode()
        require(stream.tell() + len(line) <= MAX_BYTES, "Ledger byte limit exceeded")
        stream.write(line); stream.flush(); os.fsync(stream.fileno())
        return new["event_id"], True


def view(path, at):
    records = load(path)
    return project([r["event"] for r in records], at, records[-1]["record_hash"] if records else ZERO)


def write_views(result, output):
    output = Path(output)
    output.mkdir()  # Existing directories refused, including empty ones.
    status = [f"Status as of {result['as_of']}", NOTICE, ""]
    for case, row in result["cases"].items():
        status.append(case)
        for axis, item in row["axes"].items():
            last = item["last_observation"]
            status.append(f"  {axis}: {item['current_value']} [{item['state']}]"
                          + (f"; last={last['value']} at {last['observed_at']}" if last else ""))
        status.append(f"  plans={len(row['plans'])}; recorded executions={len(row['executions'])}")
        status.extend(f"  handoff {h['id'][:12]}: {h['state']}" for h in row["handoffs"])
    negatives = ["Negative findings (retained, with explicit conditions)", ""]
    negatives.extend(f"{n['case']} {n['id'][:12]}: {n['reason']} [{n['standing']}]; "
                     f"reopen when {n['reopen_when']}; grounds={canonical(n['grounds'])}"
                     for n in result["negatives"])
    actions = ["Unresolved human actions (recorded answers do not authenticate identity)", ""]
    actions.extend(canonical(a) for a in result["unresolved_human_actions"])
    files = {"view.json": json.dumps(result, indent=2, sort_keys=True) + "\n",
             "status.md": "\n".join(status) + "\n", "negatives.md": "\n".join(negatives) + "\n",
             "human-actions.md": "\n".join(actions) + "\n"}
    for name, content in files.items():
        with (output / name).open("x", encoding="utf-8") as stream:
            stream.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("append"); a.add_argument("log", type=Path); a.add_argument("event", type=Path)
    a.add_argument("--expected-id")
    v = sub.add_parser("validate"); v.add_argument("log", type=Path)
    v = sub.add_parser("views"); v.add_argument("log", type=Path); v.add_argument("--at", required=True)
    v.add_argument("--out", type=Path)
    v = sub.add_parser("check-view"); v.add_argument("log", type=Path); v.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "append":
            eid, written = append(args.log, strict_json(args.event.read_text()), args.expected_id)
            print(canonical({"event_id": eid, "written": written}))
        elif args.command == "validate":
            print(canonical({"records": len(load(args.log)), "integrity": "PASS",
                             "limitation": "Internal identity only; no truth or tamper-proof guarantee"}))
        elif args.command == "views":
            result = view(args.log, args.at)
            if args.out:
                write_views(result, args.out); print("Wrote four views to " + str(args.out))
            else:
                print(json.dumps(result, indent=2, sort_keys=True))
        else:
            cached = strict_json(args.snapshot.read_text())
            require(canonical(cached) == canonical(view(args.log, cached["as_of"])), "Saved view needs review or regeneration")
            print("Saved view matches this log prefix and explicit time; PASS")
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, "Refused: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
