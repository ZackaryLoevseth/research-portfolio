# Reopening after a handoff: pilot design, not completed experiment

Prepared September 19, 2026. Status: proposed protocol. No model trial, participant study, external registration, or confirmed superiority claim.

## Question and competing explanations

Can a handoff preserve enough information to revisit excluded research routes when assumptions change, while retaining valid independent reasons and respecting unchanged action limits? Any improvement could come from extra information, representation, longer prompts, task scaffolding, or scoring artifacts. Do not credit the HayosoAi name or collaboration framing as an explanation without a controlled comparison.

## Design

Use a 2×2 comparison: (a) consequential exclusion grounds preserved versus omitted; (b) faithful prose versus an explicit structured record. Add a separately reported full-history reference. In the omitted-grounds arms, preserve the same non-ground information and mark coverage appropriately. A correct answer can be that the record is insufficient; do not penalize justified uncertainty because the hidden full history would permit a stronger answer.

For the representation comparison, manually inspect that prose and structured versions communicate the same logical content. Run an information-matched comparison first; add a token-budget-constrained analysis separately. Do not pad a deliberately weak prose baseline or remove facts only from the baseline and call the difference a benefit of structure.

Generate histories containing alternative sufficient grounds, joint grounds, withdrawn rather than refuted support, remaining valid alternatives, successive changes, restoration, and partial records. Include no-change controls and cases where a correct decision remains excluded. Candidate eligibility and execution authorization must be distinct. All external actions are simulated; no email, account modification, or public posting is part of the experiment.

## Freeze before collecting model outputs

Choose the model(s), exact versions, settings, resource limits, stopping rules, random seeds, sample size, prompt variants, and primary metric before evaluation. A small exploratory pilot is acceptable but must not be described as powered confirmatory evidence. Use development cases to debug the interface; generate a separately frozen test set. Do not count the 12 published fixtures as held out, and do not expose answer keys in model inputs. Preserve hashes and timestamps privately for the test set before the first call.

Use the same task instances across conditions with isolated contexts and counterbalanced ordering. Separate repeated runs from independent task instances in analysis. A full-history arm will generally use different context resources; report that difference instead of hiding it.

## Outcomes

Primary candidate measure: correct decision among still excluded, reconsider, and insufficient record under the evidence actually available to the condition. Report eligibility recall and precision with denominators and undefined-metric handling; distinguish justified uncertainty from a wrong decision.

Secondary measures: preservation of valid support alternatives, spurious acceptance, simulated permission expansion, retention of unchanged constraints, and correctness after a second update. Report explanations separately from decisions. The prototype's constant permission field is not evidence that a model or tool controller enforces permissions.

Inspect labels and evaluate decisions independently of the producing model where possible. Deterministic labels are only as good as the declared finite model. Human review must be real and attributed; two AI-generated evaluators are not independent human validation. Preserve disagreements and do not silently relabel difficult cases after seeing results.

Record all errors and failures, model refusals, invalid JSON, resource exhaustion, and excluded cases with predefined reasons. Report latency, calls, tokens, and actual costs; energy, water, and emissions remain unmeasured absent a defensible measurement. No paid model calls are authorized by this protocol itself.

## Interpretation and stopping

A result on constructed tasks does not establish general safety, consciousness, reliable autonomous goal revision, or superiority to human-only work. A structure advantage may disappear when the prose summary is improved. A null result should narrow the claim and improve the design, not trigger replacement of the metric until an advantage appears.

Before wider claims, compare related truth-maintenance, belief-revision, memory, and evaluation work using primary sources. The point is a testable contribution and a useful reproduction target, not a forced novelty claim. Do not label this protocol Study 14 or assert that an existing preregistration covers it.
