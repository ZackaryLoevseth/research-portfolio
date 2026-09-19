#!/usr/bin/env python3
"""Offline, lossless packaging of a constructed inquiry record; no authorization engine."""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import uuid

KINDS = {"question", "proposal", "objection", "stipulated-premise", "permission-record"}
LINKS = {"addresses", "objects-to", "records-standing", "retains-concern"}
UPSTREAM = "51e2b924c195e8f9fd98138b1f2947496a82eb31"
WARNING = "Fictional case record. Derivation is not support, agreement, or authorization. This export grants no execution permission."


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, required, optional=()):
    require(isinstance(value, dict), "Expected an object")
    require(set(required) <= value.keys() <= set(required) | set(optional), "Missing or unknown attributes")


def text(value):
    require(isinstance(value, str) and bool(value.strip()), "Expected nonempty text")
    require(not any(ord(c) < 32 and c not in "\n\t" for c in value), "Control character")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value), "Unsafe identifier")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def uid(case, category, value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"urn:hayosoai:{case}:{category}:{value}"))


def validate(record, source_dir):
    keys(record, {"version", "case_id", "record_created_at", "fictional", "attribution", "coverage", "sources", "nodes", "relations"})
    require(type(record["version"]) is int and record["version"] == 1 and record["fictional"] is True, "Only constructed v1 records supported")
    identifier(record["case_id"])
    text(record["attribution"])
    require(record["coverage"] == "partial", "This adapter requires explicit partial coverage")
    stamp = record["record_created_at"]
    require(isinstance(stamp, str) and stamp.endswith("Z"), "Record timestamp must be UTC, not a fictional event time")
    parsed = dt.datetime.fromisoformat(stamp[:-1] + "+00:00")
    require(parsed.year >= 1970, "Invalid record date")
    for collection in ("sources", "nodes", "relations"):
        require(isinstance(record[collection], list) and record[collection], "Empty or invalid collection")
    sources = {}
    for source in record["sources"]:
        keys(source, {"id", "file", "url", "sha256", "status"})
        identifier(source["id"])
        require(source["id"] not in sources, "Duplicate source")
        require(source["file"] == source["id"] + ".md", "Source filename must be id.md")
        require(re.fullmatch(r"[0-9a-f]{64}", source["sha256"] or ""), "Invalid SHA256")
        require(re.fullmatch(r"(?:https://|urn:sha256:)[^\s<>\"{}|^`\\]+", source["url"] or ""), "Unsafe source URI")
        require(source["status"] in {"published-case", "prepared-amendment"}, "Unknown source status")
        path = pathlib.Path(source_dir) / source["file"]
        require(not path.is_symlink() and path.is_file(), "Source must be a regular file, not symlink")
        data = path.read_bytes()
        require(digest(data) == source["sha256"], "Source hash mismatch")
        data.decode("utf-8")
        sources[source["id"]] = data
    nodes = {}
    for node in record["nodes"]:
        keys(node, {"id", "kind", "title", "text", "history", "source", "excerpt"}, {"permission"})
        identifier(node["id"])
        require(node["id"] not in nodes, "Duplicate node")
        require(node["kind"] in KINDS, "Unknown kind; fictional material is not empirical Evidence")
        for field in ("title", "text", "history", "excerpt"):
            text(node[field])
        require(node["source"] in sources, "Missing source")
        require(node["excerpt"] in sources[node["source"]].decode("utf-8"), "Source excerpt not found")
        require(("permission" in node) == (node["kind"] == "permission-record"), "Permission must be a separate record")
        if "permission" in node:
            p = node["permission"]
            keys(p, {"status", "actor", "scope", "agreement"})
            require(p["status"] in {"not-authorized", "stipulated-limited", "insufficient-record", "proposal-only"}, "Unknown permission standing")
            require(p["agreement"] in {"not-established", "dissent-retained", "not-applicable"}, "Consent/agreement cannot be inferred")
            text(p["actor"])
            text(p["scope"])
        nodes[node["id"]] = node
    relation_ids = set()
    for relation in record["relations"]:
        keys(relation, {"id", "type", "source", "destination"})
        identifier(relation["id"])
        require(relation["id"] not in relation_ids, "Duplicate relation")
        relation_ids.add(relation["id"])
        require(relation["type"] in LINKS, "Unsupported semantic relation")
        require(relation["source"] in nodes and relation["destination"] in nodes, "Missing relation endpoint")
        source, target = nodes[relation["source"]], nodes[relation["destination"]]
        valid = {"addresses": source["kind"] in {"proposal", "objection"} and target["kind"] == "question",
                 "objects-to": source["kind"] == "objection" and target["kind"] == "proposal",
                 "records-standing": source["kind"] == "permission-record" and target["kind"] == "proposal",
                 "retains-concern": source["kind"] == "stipulated-premise" and target["kind"] == "objection"}
        require(valid[relation["type"]], "Relation conflates semantic kinds")
        if relation["type"] == "records-standing":
            require(source["history"] == target["history"], "Permission standing cannot cross histories")
    return sources, int(parsed.timestamp() * 1000)


def render(record, sources, millis):
    case = record["case_id"]
    node_id = lambda n: uid(case, "node", n)
    kind_id = lambda k: uid(case, "kind", k)
    relation_id = lambda r: uid(case, "relation-kind", r)
    files = {"record.json": encode(record).encode()}
    source_map = {s["id"]: s for s in record["sources"]}
    schema = {"nodeTypes": [], "relationTypes": [], "discourseRelations": [], "showIdsInFrontmatter": True}
    for kind in sorted(KINDS):
        schema["nodeTypes"].append({"id": kind_id(kind), "name": kind.replace("-", " ").title(), "format": kind + " - {content}", "created": millis, "modified": millis})
    for rel in sorted(LINKS):
        schema["relationTypes"].append({"id": relation_id(rel), "label": rel, "complement": "inverse of " + rel, "color": "grey", "created": millis, "modified": millis})
    notes = {n["id"]: n for n in record["nodes"]}
    relations, triplets = {}, set()
    for rel in record["relations"]:
        rid = uid(case, "relation", rel["id"])
        relations[rid] = {"id": rid, "type": relation_id(rel["type"]), "source": node_id(rel["source"]), "destination": node_id(rel["destination"]), "created": millis}
        triplets.add((notes[rel["source"]]["kind"], rel["type"], notes[rel["destination"]]["kind"]))
    for source, rel, target in sorted(triplets):
        schema["discourseRelations"].append({"id": uid(case, "triplet", source + ":" + rel + ":" + target), "sourceId": kind_id(source), "destinationId": kind_id(target), "relationshipTypeId": relation_id(rel), "created": millis, "modified": millis})
    files["settings-fragment.json"] = encode(schema).encode()
    files["relations.json"] = encode({"version": 1, "lastModified": millis, "relations": relations}).encode()
    ttl = ['@prefix prov: <http://www.w3.org/ns/prov#> .', '@prefix dct: <http://purl.org/dc/terms/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .', '# Provenance of authored records only; no fictional events or permission inference.']
    literal = lambda s: json.dumps(s, ensure_ascii=False)
    for source in record["sources"]:
        uri = "urn:sha256:" + source["sha256"]
        ttl.append(f'<{uri}> a prov:Entity ; dct:identifier {literal(source["sha256"])} ; dct:source <{source["url"]}> .')
        files["sources/" + source["file"]] = sources[source["id"]]
    for node in record["nodes"]:
        source = source_map[node["source"]]
        meta = {"nodeTypeId": kind_id(node["kind"]), "nodeInstanceId": node_id(node["id"]), "kind": node["kind"], "fictional": True, "history": node["history"], "coverage": record["coverage"], "source_sha256": source["sha256"]}
        front = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in meta.items())
        body = f"---\n{front}\n---\n\n# {node['title']}\n\n{WARNING}\n\n{node['text']}\n\nAttribution: {record['attribution']}\n\nSource: [{source['status']}]({source['url']}); exact bytes: [source](../sources/{source['file']}).\n\nSource excerpt:\n\n" + "\n".join("> " + line for line in node["excerpt"].splitlines()) + "\n"
        if "permission" in node:
            body += "\nPermission record (not enforcement):\n\n```json\n" + encode(node["permission"]) + "```\n"
        outgoing = [r for r in record["relations"] if r["source"] == node["id"]]
        incoming = [r for r in record["relations"] if r["destination"] == node["id"]]
        if outgoing:
            body += "\nOutgoing recorded relations:\n\n" + "\n".join(f"- {r['type']}: [{r['destination']}]({r['destination']}.md)" for r in outgoing) + "\n"
        if incoming:
            body += "\nIncoming recorded relations (read the source record):\n\n" + "\n".join(f"- [{r['source']}]({r['source']}.md) — {r['type']} → this record" for r in incoming) + "\n"
        files["notes/" + node["id"] + ".md"] = body.encode()
        ttl.append(f'<urn:uuid:{node_id(node["id"])}> a prov:Entity ; rdfs:label {literal(node["title"])} ; dct:type {literal(node["kind"])} ; dct:description {literal(WARNING)} ; prov:wasDerivedFrom <urn:sha256:{source["sha256"]}> .')
    files["provenance.ttl"] = ("\n".join(ttl) + "\n").encode()
    files["README.md"] = (f"# Offline inquiry handoff\n\n{WARNING}\n\nOpen notes/ as ordinary Markdown. record.json preserves every input field; sources/ preserves exact bytes. settings-fragment.json is a manual mapping aid for Discourse Graph custom types, NOT an installable schema export or complete plugin settings file. UI/import/sync compatibility is untested. Nothing installs, enables or contacts Obsidian, Discourse Graphs, or a remote service. Do not replace existing settings with this fragment. Required DG timestamps represent the authored record time ({record['record_created_at']}), not fictional events.\n\nInspected upstream commit: {UPSTREAM}. No upstream code is vendored. Local relation instances do not imply accepted scientific claims. Permission records do not grant or enforce permissions. Unknown details remain unknown; the adapter does not decide whether a proposal is legitimate. No new license or reuse rights are granted.\n").encode()
    files["README.md"] += ("\n## Every record\n\n" + "\n".join(f"- [{n['title']}](notes/{n['id']}.md) — {n['kind']}" for n in record["nodes"]) + "\n").encode()
    files["manifest.json"] = encode({"files": {p: digest(data) for p, data in sorted(files.items())}, "note": "Manifest excludes its own hash."}).encode()
    return files


def export(record, source_dir, output):
    sources, millis = validate(record, source_dir)
    output = pathlib.Path(output)
    require(".." not in output.parts, "Output traversal rejected")
    require(not output.exists() and not output.is_symlink(), "Refusing to overwrite output")
    files = render(record, sources, millis)
    output.mkdir()  # Atomic refusal if another process creates it meanwhile.
    for relative, content in sorted(files.items()):
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=pathlib.Path)
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    try:
        count = export(json.loads(args.record.read_text(encoding="utf-8")), args.source_dir, args.out)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"Export refused: {error}\n")
    print(f"Wrote {count} files to {args.out}; no services contacted.")


if __name__ == "__main__":
    main()
