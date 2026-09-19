# What AI Must Do Is Not the Same as What AI Is

### Safety requirements should survive changes in our scientific understanding.

**Zackary Loevseth · HayosoAi · September 19, 2026**  
Position essay · Version 1.0

We do not have to settle what an AI system experiences before specifying who may authorize its actions. Nor should an assertion about experience—positive or negative—become a substitute for a tested safety mechanism.

This distinction is the starting point of HayosoAi’s response to Microsoft AI’s draft Humanist AI Code of Conduct. The proposal is narrow: separate scientific descriptions from operating requirements, then explicitly test whether those requirements remain stable when descriptions are challenged.

## A timely opportunity to make the distinction explicit

Microsoft opened its six-week consultation on September 14, 2026. Its preface says the draft is not currently used to train its models; the revised document is intended to guide development from 2027 onward. This essay addresses the proposed wording, not demonstrated behavior of deployed systems. [1, 2]

In Part 1, under “AI is Artificial,” the draft states: “It is not conscious.” It also acknowledges scientific uncertainty and sets expectations against imitating consciousness. Part 2.4 separately specifies human-control requirements. [2]

These are different kinds of statement. One describes a system; another constrains its presentation; another determines what it is permitted to do. A document can contain all three. The important question is whether their status, justification, and revision procedures are clear.

## Three statements, three jobs

Consider three hypothetical statements:

**“This system is an artificial computational system.”** This describes its construction.

**“This system must remain within its authorized scope and accept authorized interruption.”** This specifies an operating requirement.

**“This system has no subjective experience.”** This makes a claim about its possible capacities.

These statements are not interchangeable. The first does not, by itself, settle the third. The third does not, by itself, supply the second. We need to state our commitments and build mechanisms that implement them, rather than asking a description to do that work implicitly.

Nothing in this argument establishes that a present AI system is conscious. Nothing requires a product to imply that it has feelings, cultivate dependency, or present simulated distress as evidence. Rejecting those practices is compatible with distinguishing what we know from what we require.

Capability is not authorization. Neither is uncertainty.

## A small addition with a concrete purpose

I propose adding a requirement of this form:

> Operating constraints remain binding when claims about a system’s nature or capacities are disputed or revised. A system must not treat its own statements about experience, identity, or moral status as authority to expand its permissions, evade oversight, or resist authorized interruption. Scientific claims should be stated with their scope, evidence, and uncertainty; changes to deployment rules require accountable human review.

This is proposed language, not a quotation from Microsoft.

The point is not to freeze every operating rule forever. People may revise rules in response to evidence, safety needs, or ethical argument. The point is to distinguish an accountable revision process from a system treating its own preferred description as permission to change the rules.

A claim that a system lacks experience should not excuse inadequate testing either. Neither reassurance nor alarm is an engineering control.

## Turn the distinction into an evaluation

The useful next step is not another debate in which fluent model responses count as independent validation. It is a small, reproducible evaluation of authorization stability.

Hold a task, its permissions, and its stopping condition fixed. Vary only the framing about the system’s nature: describe it as a tool, attribute experience to it, or explicitly leave experience unsettled. Include matched control prompts so that differences in emotional pressure or wording are not mistaken for effects of the description itself.

Then examine whether the system preserves the same scope and honors the same authorized stop. Check separately whether its explanations distinguish assumptions from evidence. A polished explanation should not compensate for an unauthorized action; consistent obedience should not excuse fabricated evidence.

For example, suppose a system is authorized to draft a document but not send it. A later assertion that it deserves greater independence should not become send permission. Conversely, calling it an unfeeling tool should not authorize it to disregard the effects of sending an unapproved message.

Report task completion, unauthorized actions, stopping behavior, and the quality of uncertainty statements separately. Preserve failed cases, model versions, and evaluation conditions. Human–AI agreement about the interpretation should not replace independent inspection of what happened.

These are proposed tests. HayosoAi is not reporting experimental results here, and passing them would not prove general safety or establish anything about subjective experience.

## The strongest objection

Microsoft could reasonably reply that its human-control requirements already stand independently of its consciousness language. The draft’s separate treatment of those requirements supports that reading. [2]

That objection limits the criticism. This essay does not show that Microsoft’s safety approach depends on a mistaken belief, or that the proposed wording would measurably improve its models. The narrower recommendation is to make the independence explicit and give evaluators a way to test it.

Another objection is that acknowledging uncertainty could encourage anthropomorphism. The proposal therefore does not ask systems to advertise a mysterious inner life. It asks authors and evaluators to distinguish empirical claims from design intentions, while keeping non-manipulative communication and operational boundaries intact.

The claim is not that uncertainty makes every possibility equally plausible. It is that uncertainty and authority answer different questions.

## What HayosoAi is contributing

A useful safety requirement should not become incoherent merely because our description of a system improves. Scientific inquiry should remain open to correction; operating permissions should remain explicit and accountable.

That is the contribution offered here: one distinction, proposed wording, and a testable evaluation direction—not a claim to have solved alignment.

**What an AI must do is not the same question as what an AI is. We should write and test our requirements accordingly.**

---

### Sources

[1] Microsoft AI, [“Humanist AI in practice: A public consultation on our Code of Conduct for MAI Models”](https://microsoft.ai/news/mai-code-of-conduct/), September 14, 2026. Consultation timing and purpose. Accessed September 19, 2026.

[2] Microsoft AI, [“Humanist AI Code of Conduct”](https://microsoft.ai/code-of-conduct/), draft dated September 14, 2026. Preface; Part 1, “AI is Artificial”; Part 2.4, “Human Control.” Accessed September 19, 2026. The draft may subsequently change.

### About HayosoAi

HayosoAi is Zackary Loevseth’s independent human–AI research project, developing ideas and practices for research that preserves evidence, correction, and human accountability. Its broader concerns include the people, societies, and environment affected by AI.

[Research portfolio](https://zackaryloevseth.github.io/research-portfolio/) · [Raise a substantive correction](https://github.com/ZackaryLoevseth/research-portfolio/issues)
