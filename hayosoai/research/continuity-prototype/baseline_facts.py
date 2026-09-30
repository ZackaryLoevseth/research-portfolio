"""Separately authored, carefully maintained snapshots for the shared rubric.

These literal outcomes are NOT computed from prototype projections or copied
from the oracle at runtime. They model a conscientious maintainer, not an LLM.
"""
from fixtures import ax, t

FACTS = {
    "drafted_vs_submitted": {
        "plan": {ax("workflow"): "draft", "cases/synthetic/executions/$len": 0},
        "attempt": {ax("workflow"): "draft", "cases/synthetic/executions/0/verification": "unverified"},
        "checked": {ax("workflow"): "draft", "cases/synthetic/executions/0/verification": "pass"},
        "submitted": {ax("workflow"): "submitted", ax("slots"): None}},
    "duplicate_vs_validity": {
        "valid": {ax("duplicate"): "duplicate", ax("validity"): "valid", ax("disposition"): None}},
    "accepted_vs_paid": {
        "unpaid": {ax("disposition"): "accepted", ax("payment"): "unpaid"},
        "paid": {ax("disposition"): "accepted", ax("payment"): "paid"}},
    "stale_observation": {
        "old": {ax("validity"): None, ax("validity", "state"): "stale",
                ax("validity", "last_observation/value"): "valid"}},
    "correction_propagation": {
        "correction": {ax("validity"): "invalid", "invalidated/$len": 4,
                       "cases/synthetic/handoffs/0/state": "review_required",
                       "cases/synthetic/notes/0/state": "review_required",
                       "cases/synthetic/notes/1/state": "review_required"},
        "second_correction": {ax("validity"): "valid", "invalidated/$len": 5,
                              "cases/synthetic/handoffs/0/state": "review_required"}},
    "negative_reopening": {
        "unrelated": {"negatives/0/standing": "held"},
        "same": {"negatives/0/standing": "held"},
        "changed": {"negatives/0/standing": "reopen_eligible", ax("disposition"): None},
        "reopen": {"negatives/0/standing": "reopened_for_review", ax("disposition"): None}},
    "failed_read_after_success": {
        "failure": {ax("validity"): None, ax("validity", "state"): "collection_failed",
                    ax("validity", "last_observation/value"): "valid",
                    ax("validity", "last_observation/observed_at"): t(1),
                    ax("validity", "last_observation/valid_until"): t(100)},
        "recovered": {ax("validity"): "valid", ax("validity", "state"): "fresh",
                      "cases/synthetic/collection_failures/$len": 1}},
    "repeated_answered_requests": {
        "repeat": {"requests/$len": 1, "requests/0/state": "answered_recorded",
                   "unresolved_human_actions/$len": 0},
        "repeat_fresh": {"requests/0/state": "answered_recorded", "unresolved_human_actions/$len": 0},
        "different": {"requests/0/state": "premise_changed", "unresolved_human_actions/0/action": "respond"},
        "revised": {"requests/0/state": "premise_changed"},
        "revised_answer": {"requests/0/state": "answered_recorded", "unresolved_human_actions/$len": 0}},
    "closure_not_available_slots": {
        "closed": {ax("workflow"): "closed", ax("slots"): None},
        "slots": {ax("workflow"): "closed", ax("slots"): "unavailable"}},
    "planned_not_executed": {
        "plan_only": {"cases/synthetic/plans/0/state": "planned", "cases/synthetic/executions/$len": 0,
                      ax("workflow"): None}},
}
