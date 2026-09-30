# HayosoAi offline research continuity prototype v0

Experimental, synthetic data only. Authored with AI assistance under human direction.
Python 3.10+ standard library on a POSIX host with fcntl. The runtime records claims
and writes local files; it has no network, model-call, credential or outbound
execution interface.

From a complete repository checkout:

    cd hayosoai/research/continuity-prototype
    python3 -B run_checks.py

From an extracted source ZIP, run the same Python command in its directory.
To save inspectable synthetic logs, baseline files and status/negative/action views:

    python3 -B run_checks.py --out my-new-checks

The output directory must be new and its parent must exist. The default checks
use disposable temporary directories and leave saved reports untouched.

Milestone v0, September 30, 2026: 36 test methods passed. All three representations
pass the same 10 scenarios, 24 checkpoints and 57 assertions per representation:
event ledger 10/10, maintained status file 10/10, maintained handoff summary 10/10.
CHECK_RESULTS.txt contains the executed run, and comparison.json contains each
checkpoint result. Baselines retain the same complete source histories, including
identifiers, timestamps, corrections and uncertainty. This is a maintained-artifact
comparison with known synthetic cases, not a human or model performance experiment.

The required cases cover drafted/submitted, duplicate/technical validity,
accepted/paid, stale observations, transitive corrections, conditional negative
reopening, failed reads, answered requests, closure/slots and planning/execution.
Additional integrity tests cover malformed data, exact retry, type identity,
dependency barriers, alternative grounds, local locking, CLI use and storage limits.

The [English beta entry](https://zackaryloevseth.github.io/research-portfolio/hayosoai/beta/en/continuity/)
explains this experimental branch. Subsequent milestone notes should record only
executed checks and explicit limitations, keeping old reports and claims distinct
from current observations. Publication does not establish adoption or effectiveness.

## Architecture and precise rules

continuity.py is the runtime. fixtures.py constructs deterministic synthetic
events. test_continuity.py exercises the invariants and CLI. baseline_facts.py
contains separately authored baseline outcome declarations; compare.py
serializes and checks those snapshots with the exact same source histories.
test_compare.py checks comparison fidelity and sensitivity to wrong outcomes.
run_checks.py runs everything. The files in this directory are the complete prototype source and tests.

The regression method checks the shared scenario rubric. The other runtime
tests independently exercise update/identity properties, stale and changed
premises, alternative grounds, corruption, malformed input, locks and the CLI.
The baseline tests additionally detect wrong/missing outcomes and verify full
source-history fidelity. The review found a Python equality edge case (True
equals 1); replay and saved-view identity now compare canonical JSON hashes
or content, and a dedicated regression checks both numeric type variants.

Every event has a version, unique retry key, case, kind, UTC recording time,
unauthenticated actor label, declared dependency IDs and typed data. Its ID is
SHA256 of canonical JSON. A JSONL record adds an increasing sequence, previous
record hash and record hash. Strict parsing rejects duplicate JSON keys,
unknown fields, malformed timestamps, invalid axes and incomplete last records.

The independent axes are workflow (draft/submitted/closed), disposition
(pending/accepted/rejected), payment (unpaid/paid), duplicate standing, technical
validity, and observed slot availability. No axis changes another. Unknown
axes remain unobserved. Interpretations and plans do not create observations;
execution records do not change workflow status. Verification is a separate
claim about a cited execution. A successful verification does not itself imply
submission, acceptance or payment.

Observations declare observed_at and valid_until. The greatest observed_at
wins; recording order breaks equal-time ties. A late backfilled observation
therefore does not become current. This rule assumes comparable timestamps and
no source priority model; equal-time disagreements are not adjudicated.
The explicit projection time must be at least the last recording time.
Fresh means within the declared window, not independently confirmed current.
A later failed collection suppresses current_value and retains the last
observation and its original expiry. An older backfilled failure does not
override a newer success. A new successful observation can restore freshness.

Dependencies must name prior events in the same case. Missing, self, forward,
cyclic and cross-case dependencies are refused. They are declared support
edges, not automatic discovery of what a claim really depends on.
Interpretations and handoffs require declared dependencies. Old dependent
packets also require review when their observations expire or materially
disagree with the latest fresh observation.

A correction cites an earlier claim and a later active compatible replacement,
with a reason. Both remain. Observations must replace the same axis without
backdating. A replacement cannot depend on the withdrawn claim. The target
and every declared transitive dependent are persistently invalidated for review.
New ordinary claims cannot cite already invalidated dependencies. Review
requires new authored claims and dependencies; it does not edit history.
Correction retractions and correction-of-correction events are unsupported and
rejected. Correcting a replacement via a new replacement is supported and never
resurrects a previously invalidated packet. Saved views bind to the log tip
and explicit as_of time; check-view detects drift from that saved snapshot.
Matching a snapshot at its old time does not assert freshness today.

Negative findings retain their reason and sufficient grounds as ORs of AND
sets of observations. Their explicit reopening rule is: every recorded
sufficient ground must have at least one premise contradicted by a fresh
observation with a strictly newer observed_at. A repeated value, unrelated
change, staleness or collection failure cannot satisfy this rule. Eligibility
prompts review; reopening requires its own decision citing the changed
observations. The negative_id is a historical reference, not support for that
new decision. Reconsideration does not imply technical validity, acceptance,
slot availability or permission. Direct premise correction without a qualifying
fresh changed value leaves the old negative for review.

Requests use an explicit semantic question_key and premise axes. Repeating a
question with the same premise values preserves its recorded answer even
when observation IDs change. Fresh materially different values reopen the
question; stale, failed or corrected evidence requires answer review instead
of silently asking again. Requests based on obsolete/unavailable premises are
refused. Changing question text or its premise-axis set requires a new key.
This is declared semantic identity; the prototype cannot infer that two
different free-text questions are equivalent.

Exact retries return the original event ID without adding bytes, including
after later events. Reusing a retry key or claimed eventID with a changed
payload is rejected without writing record bytes. Local cooperating writers
use a nonblocking lock and fsync. This is not a transactional storage or
distributed concurrency guarantee: a crash can leave a partial final record,
which is then refused pending explicit repair. No automated repair is provided.

## What the comparison establishes

The baseline snapshots are carefully maintained, with all inputs, evidence
references, identifiers, timestamps, corrections and uncertainty retained.
Their outcome values are literal declarations in baseline_facts.py, separate
from the regression oracle and never filled from ledger projections at runtime.
Both formats are checked at exactly the same checkpoints. The final artifacts
are saved; comparison.json retains all checkpoint results; generated source histories and views are produced by the --out command.

All three representations preserve all tested distinctions when maintained.
The ledger mechanically validates input/replay rules and propagates declared
dependency review; plain status files and handoffs can carry the same information
with a maintainer doing those updates. We have not measured how often a person
or model misses an update, how much time any approach takes, or whether the
extra structure makes collaboration better overall.

The runtime adds 497 lines, strict schemas, timestamp conventions, dependency
authoring, retries, correction rules, locks and tests. The baseline declarations
add 54 lines and their comparison serializer 105 lines. These source counts
describe this prototype, not a general complexity ranking.
Final artifact bytes across the ten cases are 22,478 for ledger logs, 26,816 for
status snapshots and 21,819 for handoffs. Ledger views and earlier checkpoints
are excluded; formatting differs. Those byte counts are not time or usability
measurements.

Prefer a simple status file or handoff when cases are few, one maintainer can
review updates, dependencies are shallow, and preserving an inspectable source
history is enough. Consider an event ledger when repeated corrections and
dependent packets make reproducible replay or automatic review marking useful.
That conditional choice still needs a real workflow evaluation.

## Trusted boundary and remaining limits

All event content, actor labels, timestamps, observation windows, semantic keys,
grounds and evidence refs are unauthenticated input claims. In particular,
actor_claim="human" does not authenticate a human or approval. A recorded answer
suppresses duplicate recorded requests; it does not establish that a trusted
human answered them. Actual identity/authority checks must exist outside this
prototype before it could be used for consequential decisions.

Hashes identify canonical content, not truth. Application append-only behavior
is not tamper-proof storage: a party with filesystem access can rewrite and
reseal the whole log, remove a valid suffix, or omit events/dependencies.
The suite deliberately demonstrates those limits. There is no signature,
trusted timestamp, external tip anchor, immutable storage or independent source
verification. Evidence refs are never dereferenced.

The limit is 1,000 events and 2 MB per log. Replay uses repeated whole-prefix
validation; this is not a scale benchmark. No migration, distributed sync,
cross-case dependency, integration, production, legal reuse or universal
epistemic-control claim is made. The runtime has no outbound execution
capability; Python itself is not sandboxed against a hostile edit to the code.
Only synthetic fixtures were used; no private reports were imported.

This technical branch addresses a specific continuity question. It does not replace HayosoAi's wider inquiry or settle what "better" means. Read the current [Project Compass](../../PROJECT_COMPASS.md) when continuing the work. No new reuse rights are granted; the repository's existing license status applies.
