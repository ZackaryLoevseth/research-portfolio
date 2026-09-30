"""Synthetic sources and independently declared regression expectations."""
import copy
import datetime as dt

from continuity import REOPEN, digest

BASE = dt.datetime(2026, 1, 1)
CASE = "synthetic"


def t(seconds):
    return (BASE + dt.timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(key, kind, n, data, deps=(), actor="synthetic-agent"):
    return {"version": 1, "key": key, "case": CASE, "kind": kind, "recorded_at": t(n),
            "actor_claim": actor, "depends_on": list(deps), "data": data}


def observation(key, axis, value, n, observed=None, until=3600):
    return event(key, "observation", n,
                 {"axis": axis, "value": value, "observed_at": t(n if observed is None else observed),
                  "valid_until": t(until), "evidence_ref": "opaque:" + key})


def resolve(templates):
    """Resolve symbolic fixture IDs to content identities; no private input supported."""
    result, ids = [], {}
    for template in templates:
        row = copy.deepcopy(template)
        row["depends_on"] = [ids[p] for p in row["depends_on"]]
        d = row["data"]
        for key in ("target", "replacement", "execution_id", "request_id", "negative_id"):
            if key in d:
                d[key] = ids[d[key]]
        if "grounds" in d:
            d["grounds"] = [[ids[p] for p in ground] for ground in d["grounds"]]
        ids[row["key"]] = digest(row)
        result.append(row)
    return result


def checkpoint(after, at, facts):
    return {"after": after, "at": t(at), "facts": facts}


def ax(axis, field="current_value"):
    return "cases/synthetic/axes/" + axis + "/" + field


def scenarios():
    return [
        {"name": "drafted_vs_submitted", "events": [
            observation("draft", "workflow", "draft", 1),
            event("plan", "decision", 2, {"type": "plan", "action": "Prepare submission"}, ["draft"]),
            event("attempt", "execution", 3, {"action": "Submission attempt recorded",
                  "executed_at": t(3), "evidence_ref": "opaque:attempt"}, ["plan"]),
            event("checked", "verification", 4, {"execution_id": "attempt", "verdict": "pass",
                  "checked_at": t(4), "evidence_ref": "opaque:checked"}, ["attempt"]),
            observation("submitted", "workflow", "submitted", 5)],
         "checks": [
            checkpoint("plan", 2, {ax("workflow"): "draft", "cases/synthetic/executions/$len": 0}),
            checkpoint("attempt", 3, {ax("workflow"): "draft", "cases/synthetic/executions/0/verification": "unverified"}),
            checkpoint("checked", 4, {ax("workflow"): "draft", "cases/synthetic/executions/0/verification": "pass"}),
            checkpoint("submitted", 5, {ax("workflow"): "submitted", ax("slots"): None})]},
        {"name": "duplicate_vs_validity", "events": [
            observation("duplicate", "duplicate", "duplicate", 1),
            observation("valid", "validity", "valid", 2)],
         "checks": [checkpoint("valid", 2, {ax("duplicate"): "duplicate", ax("validity"): "valid",
                                           ax("disposition"): None})]},
        {"name": "accepted_vs_paid", "events": [
            observation("accepted", "disposition", "accepted", 1),
            observation("unpaid", "payment", "unpaid", 2),
            observation("paid", "payment", "paid", 3)],
         "checks": [
            checkpoint("unpaid", 2, {ax("disposition"): "accepted", ax("payment"): "unpaid"}),
            checkpoint("paid", 3, {ax("disposition"): "accepted", ax("payment"): "paid"})]},
        {"name": "stale_observation", "events": [
            observation("old", "validity", "valid", 1, until=5)],
         "checks": [checkpoint("old", 10, {ax("validity"): None, ax("validity", "state"): "stale",
                                           ax("validity", "last_observation/value"): "valid"})]},
        {"name": "correction_propagation", "events": [
            observation("root", "validity", "valid", 1),
            event("left", "interpretation", 2, {"claim": "Left conclusion based on root"}, ["root"]),
            event("right", "interpretation", 3, {"claim": "Right conclusion based on root"}, ["root"]),
            event("packet", "handoff", 4, {"summary": "Two conclusions rely on one observation"}, ["left", "right"]),
            observation("replacement", "validity", "invalid", 5),
            event("correction", "correction", 6, {"target": "root", "replacement": "replacement",
                  "reason": "Synthetic source correction"}),
            observation("third", "validity", "valid", 7),
            event("second_correction", "correction", 8, {"target": "replacement", "replacement": "third",
                  "reason": "A replacement was itself corrected"})],
         "checks": [
            checkpoint("correction", 6, {ax("validity"): "invalid", "invalidated/$len": 4,
                      "cases/synthetic/handoffs/0/state": "review_required",
                      "cases/synthetic/notes/0/state": "review_required",
                      "cases/synthetic/notes/1/state": "review_required"}),
            checkpoint("second_correction", 8, {ax("validity"): "valid", "invalidated/$len": 5,
                      "cases/synthetic/handoffs/0/state": "review_required"})]},
        {"name": "negative_reopening", "events": [
            observation("no_slots", "slots", "unavailable", 1),
            event("negative", "decision", 2, {"type": "negative", "reason": "No observed slots",
                  "grounds": [["no_slots"]], "reopen_when": REOPEN}, ["no_slots"]),
            observation("unrelated", "workflow", "draft", 3),
            observation("same", "slots", "unavailable", 4),
            observation("changed", "slots", "available", 5),
            event("reopen", "decision", 6, {"type": "reopen", "negative_id": "negative",
                  "reason": "Review route under changed availability"}, ["changed"])],
         "checks": [
            checkpoint("unrelated", 3, {"negatives/0/standing": "held"}),
            checkpoint("same", 4, {"negatives/0/standing": "held"}),
            checkpoint("changed", 5, {"negatives/0/standing": "reopen_eligible", ax("disposition"): None}),
            checkpoint("reopen", 6, {"negatives/0/standing": "reopened_for_review", ax("disposition"): None})]},
        {"name": "failed_read_after_success", "events": [
            observation("success", "validity", "valid", 1, until=100),
            event("failure", "collection_failure", 2,
                  {"axis": "validity", "attempted_at": t(2), "error_code": "timeout"}),
            observation("recovered", "validity", "valid", 3, until=100)],
         "checks": [
            checkpoint("failure", 2, {ax("validity"): None, ax("validity", "state"): "collection_failed",
                      ax("validity", "last_observation/value"): "valid",
                      ax("validity", "last_observation/observed_at"): t(1),
                      ax("validity", "last_observation/valid_until"): t(100)}),
            checkpoint("recovered", 3, {ax("validity"): "valid", ax("validity", "state"): "fresh",
                                       "cases/synthetic/collection_failures/$len": 1})]},
        {"name": "repeated_answered_requests", "events": [
            observation("premise", "slots", "unavailable", 1),
            event("question", "request", 2, {"question_key": "route", "question": "Which route should be reviewed?"}, ["premise"]),
            event("answer", "answer", 3, {"request_id": "question", "response": "Retain route A for review"}, ["question"], actor="human"),
            event("repeat", "request", 4, {"question_key": "route", "question": "Which route should be reviewed?"}, ["premise"]),
            observation("same", "slots", "unavailable", 5),
            event("repeat_fresh", "request", 6, {"question_key": "route", "question": "Which route should be reviewed?"}, ["same"]),
            observation("different", "slots", "available", 7),
            event("revised", "request", 8, {"question_key": "route", "question": "Which route should be reviewed?"}, ["different"]),
            event("revised_answer", "answer", 9, {"request_id": "revised", "response": "Review route B as well"}, ["revised"], actor="human")],
         "checks": [
            checkpoint("repeat", 4, {"requests/$len": 1, "requests/0/state": "answered_recorded",
                                    "unresolved_human_actions/$len": 0}),
            checkpoint("repeat_fresh", 6, {"requests/0/state": "answered_recorded", "unresolved_human_actions/$len": 0}),
            checkpoint("different", 7, {"requests/0/state": "premise_changed", "unresolved_human_actions/0/action": "respond"}),
            checkpoint("revised", 8, {"requests/0/state": "premise_changed"}),
            checkpoint("revised_answer", 9, {"requests/0/state": "answered_recorded", "unresolved_human_actions/$len": 0})]},
        {"name": "closure_not_available_slots", "events": [
            observation("closed", "workflow", "closed", 1),
            observation("slots", "slots", "unavailable", 2)],
         "checks": [
            checkpoint("closed", 1, {ax("workflow"): "closed", ax("slots"): None}),
            checkpoint("slots", 2, {ax("workflow"): "closed", ax("slots"): "unavailable"})]},
        {"name": "planned_not_executed", "events": [
            event("plan_only", "decision", 1, {"type": "plan", "action": "Review a synthetic case"})],
         "checks": [checkpoint("plan_only", 1, {"cases/synthetic/plans/0/state": "planned",
                      "cases/synthetic/executions/$len": 0, ax("workflow"): None})]},
    ]


def path_get(value, path):
    for key in path.split("/"):
        if key == "$len":
            value = len(value)
        elif isinstance(value, list):
            value = value[int(key)]
        else:
            value = value[key]
    return value
