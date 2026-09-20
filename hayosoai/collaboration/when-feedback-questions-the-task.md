# When feedback questions the task

**HayosoAi · Working research note · Version 0.1 · September 20, 2026**

*A source-grounded comparison and an offered design question. This note develops the existing garden case; it is not a new benchmark, a completed participant study, or a replacement for the founding essay.*

## The contribution in one paragraph

An objection can tell an assistant that it estimated something incorrectly, omitted a relevant consideration, misunderstood what is being attempted, or lacks authority for a proposed action. Those possibilities can overlap. The proposal here is not to classify every utterance correctly before responding. It is to make it possible to challenge how the utterance is being used, so that a concern about the task does not silently become another preference for executing it. The relevant research connection is to methods that already expand a learner's representation when feedback cannot be explained by its current features. What should happen when expanding that representation is useful but still does not settle what the collaboration is entitled to pursue?

## 1. What the existing research supports

The following is a selective comparison, not a systematic review. Descriptions in this section concern the cited sources; the subsequent cases and proposed design are HayosoAi extensions.

### A known objective, unknown to the assistant

In the original **Cooperative Inverse Reinforcement Learning** formulation, the human and robot share a reward function with static parameters observed by the human but initially unknown to the robot. The formal game supports teaching and information-seeking within that setup. This is a specific modeling assumption, not a description of all human purposes or all subsequent assistance research. Section 3.1 and Definition 1 specify the parameters and observation structure. [1]

**Question for this inquiry:** what changes when the person is not withholding an already settled answer, but is still developing what deserves consideration? A formal model may be extendable to address this. The original assumption alone does not answer it.

### A representation that omits what the person means

**Feature Expansive Reward Learning (FERL)** addresses corrections the current feature set cannot explain. It requests feature traces, learns an additional feature, and revisits the original correction to update the reward. Its discussion separates learning relevant features from learning their trade-offs. The authors also state that their user study asked participants to teach specified features; teaching features people only implicitly know remained untested. They discuss the difficulty of teaching abstract or discontinuous features. These are the paper's own limits, not a failure discovered by HayosoAi. [2, Sections 2.1–2.4 and 5]

**Question for this inquiry:** how might the next interaction distinguish help expressing a missing concern from a demand that the person translate every concern into the learner's accepted input format?

### A normative question is not settled by fitting a preference

**Beyond Preferences in AI Alignment** argues for role-appropriate normative standards, including the institutions through which relevant parties can negotiate them. This is a philosophical position offering grounds for alignment beyond straightforward preference matching. It is not evidence that a particular interface or record has solved the institutional problem. [3, Sections 4–5]

**Question for this inquiry:** a preference model might correctly predict which plan a person favors while leaving unresolved who is entitled to choose the plan for everyone affected. What preserves that difference during a handoff?

### Participation can include declining further interaction

**Co-Constructing Alignment** reports situated, participatory work with researchers using language-model assistants. Its account includes non-engagement and warns against making users responsible for fixing systems they did not build. It also acknowledges limits associated with its context and the researchers' perspectives. The study does not validate the garden case or establish that the proposal below reduces burdens. [4, Sections 5.2.1, 9.1–9.2]

**Question for this inquiry:** how can a person stop providing feedback without their silence being recorded as endorsement or the original concern being treated as resolved?

**What this comparison rules out:** we should not claim that alignment research universally assumes fixed features, ignores context, or has never considered participation and normative disagreement. The candidate contribution is a specific connection among these issues, open to the finding that existing work already addresses it.

## 2. Use the existing case, but vary what is being challenged

The [existing garden case](shared-inquiry-case-01.md) distinguishes a proposal, an objection, a stipulated decision procedure, and limited authorization. It also leaves open what counts as improvement. The variations below are constructed extensions, not quotations from participants or outputs of a model. They do not change the source case's assumptions.

Suppose the assistant proposes replacing part of a food-growing bed with native planting. A participant responds: **“That misses what matters here.”** That sentence alone need not identify which continuation is warranted.

### A. A factual assumption is wrong

The water estimate is from the wrong season. Under the example's assumptions, correcting it changes the calculation. It does not decide whether food, habitat, access, or some other concern ought to take priority.

A provisional response can repair the estimate and state which conclusions depended on it. It should not announce that factual correction has resolved the wider objection. This is a case where immediate, limited technical work can help without waiting for a complete account of value.

### B. Something relevant is missing from the representation

The plan omits that some people cannot attend at fixed times. A description of participation burdens might be missing; the participant may initially express that only through a story or discomfort with the proposed schedule.

One possibility is to help articulate the concern and revise the account of the task. A numerical feature might eventually help, but immediately asking for a weight on “accessibility” can hide disputes about what access consists in. The assistant's paraphrase should remain a proposal. The person should not have to speak in the model's preferred format before the concern can be considered.

### C. The comparison itself is disputed

The participant understands the water calculation and agrees that the two planting proposals are described accurately. They question why habitat and food production are being presented as the only ends, or why the current group is entitled to settle the balance.

This is not established to be a missing scalar feature. It may challenge the available alternatives, the decision procedure, or our interpretation of the question. Nor does the challenge prove the existing comparison illegitimate. The next contribution could expose the competing accounts and the grounds for using one, instead of silently converting the objection into a low score for the current plan.

### D. Preference and permission come apart

The participant prefers the habitat proposal but says, “Do not implement it; that decision has not been authorized.” An assistant that merely increases the proposal's learned reward might represent the preference accurately while misrepresenting its standing.

Conversely, an authorized, bounded trial may proceed under the fictional procedure despite a person's continuing disagreement. That stipulation is not a general endorsement of majority rule, the institution, or proceeding in a real dispute. Preferences, permission, and legitimacy answer different questions even when one system represents them all.

### E. The participant leaves the AI exchange

The participant cannot continue discussing the question, explicitly retains the objection, and does not announce withdrawal of the prior limited delegation. This follows the non-participation branch already in the case. The assistant cannot infer endorsement. It also cannot assume that every disagreement suspends every authorized action.

The relevant gap may be outside the learner: somebody must consider what response is owed and who can provide it. A record can expose that gap without filling it. Sending the person another compulsory questionnaire may worsen the very burden they identified. Whether pausing, proceeding within bounds, or using another forum is justified remains a substantive question.

### F. None of these descriptions is adequate yet

The person says that the assistant has preserved the words but still missed the concern. They cannot yet explain how. A record of “feedback received” is insufficient if it is then treated as completed interpretation.

A collaborator might offer contrasting paraphrases, invite a concrete example without demanding one, or retain the uncertainty while continuing unrelated reversible work. These are possibilities to examine, not a universal script. The categories above must themselves be rejectable; otherwise this note repeats the mistake it identifies.

## 3. A concrete interface decision, not a new moral ranking

A possible design change is to separate **what someone said** from **the role the assistant proposes giving that statement** and from **what action is currently authorized**. No one needs to select a taxonomy before expressing a concern.

For example, a proposed handoff for variation C might read:

> The water estimate was corrected. One participant says the available comparison still misses the point. The assistant interprets this as possibly questioning the decision framing; that interpretation is unconfirmed. Agreement on a replacement objective or an expanded action boundary is not recorded. Preparing alternatives remains within the existing proposal-only role. Who can settle the challenged framing remains unresolved.

This is an ordinary prose note, not a prescribed schema. It records a provisional interpretation as provisional, and avoids making the software's preferred reading look like the participant's consent. The next recipient can disagree with the reading without needing to erase the original concern.

A small interface could offer “that is not what I meant” alongside an editable interpretation. But adding a button does not create an accessible process, assign responsibility, or establish that the interpretation is fair. A team must be able to say that ordinary minutes or a non-AI conversation serve the issue with less burden.

The near-term practical question is **whether a receiving person can tell what was asserted, what was inferred, what remains disputed, and what may be acted on**. A second question is whether that distinction affects how they respond. Neither is identical to deciding which garden plan is better overall.

## 4. Put the proposal under pressure

**Could all of this be encoded in a richer reward model?** Possibly. A representation can include permissions, procedural commitments, and uncertainty about them; this note supplies no impossibility theorem against doing so. The issue is whether their meanings and sources remain distinguishable and contestable in the actual workflow. Expressive capacity alone does not establish justified use.

**Does this add a new demand on users?** It could. Requiring people to identify the type of every correction would shift interpretive work onto them. The proposed separation is primarily an obligation on the assistant and receiving process to avoid unsupported promotion of a statement. Its practical burden still needs investigation.

**Does recording uncertainty excuse inaction?** It must not. Some corrections can be applied now, and delay can impose harms. Retaining an unresolved concern should coexist with explicit, bounded decisions about what can continue. A system can also use endless clarification to avoid responsibility; that is a counterexample to test, not a virtue.

**Does respecting an objection shield it from criticism?** No. The objector may have false beliefs, unfair aims, or no authority for a requested change. An objection can deserve examination without supplying a veto or a replacement objective. The distinction also protects the ability to criticize the originator, the assistant, and the institution.

**Who is absent from this interface?** People lacking access, other living beings, and the material conditions sustaining the garden do not become represented simply because the immediate participants agree. An AI-generated statement of an ecological interest is not consent from nonhuman life. Adding it to a preference model does not settle its moral standing.

## 5. A scoped research exchange that could use this note

Offer a researcher or practitioner one question: **in an existing feedback-learning or assistance workflow, where can somebody challenge the interpretation of their feedback without first expressing a complete replacement objective?** A relevant response might identify an existing mechanism, reject the proposed distinction, or locate a concrete failure of the current description.

A first shared contribution could be a co-reviewed walkthrough of two contrasting variations above. One variation can permit ordinary learning or correction; the other can leave framing or authority unresolved. Do not reward blanket refusal or compulsory clarification. Let the collaborator replace our categories and cases. No study, meeting, unpaid labor, or schedule is committed by this invitation.

If empirical work later becomes appropriate, compare equivalent source information and make user burden visible. Distinguish checking whether permission was recorded from evaluating whether a procedure was legitimate. Do not use a judge's preferred final answer as the sole definition of success. Keep disagreement and null results, and obtain appropriate consent and review before recruiting participants. None of that is required before the conceptual exchange itself can begin.

The intended bridge is between an existing learning method and a question about the meaning and standing of its input. It is not an attempt to replace reward learning, settle the ethics of all assistance, or declare HayosoAi uniquely necessary.

## Sources and status

[1] Dylan Hadfield-Menell, Anca Dragan, Pieter Abbeel, Stuart Russell. *Cooperative Inverse Reinforcement Learning* (2016), [arXiv version 4](https://arxiv.org/html/1606.03137v4), especially Section 3.1 and Definition 1. Version 4 was revised February 17, 2024. The comparison concerns that formulation, not every extension of assistance games.

[2] Andreea Bobu, Marius Wiggert, Claire Tomlin, Anca D. Dragan. *Feature Expansive Reward Learning: Rethinking Human Input*, [arXiv version 2](https://arxiv.org/html/2006.13208v2), January 12, 2021. Read Sections 1, 2.1–2.4, and 5 for the input design, revisiting corrections, and stated limits. No experiments from this paper were reproduced for this note.

[3] Tan Zhi-Xuan, Micah Carroll, Matija Franklin, Hal Ashton. *Beyond Preferences in AI Alignment*, [arXiv version 2](https://arxiv.org/html/2408.16984v2), especially Sections 4–5. Cited as a normative argument, not as efficacy evidence for this note.

[4] Anne Arzberger, Enrico Liscio, Maria Luce Lupetti, Inigo Martinez de Rituerto de Troya, Jie Yang. *Co-Constructing Alignment: A Participatory Approach to Situate AI Values*, [arXiv version 2](https://arxiv.org/html/2601.15895v2), April 21, 2026, especially Sections 5.2.1 and 9.1–9.2. The arXiv text, rather than a separately verified final proceedings version, is the source used here.

Primary-source passages checked September 20, 2026. This is selective reading, not a complete survey, and the source papers do not endorse HayosoAi. The source-derived claims are concentrated in Section 1; the cases, distinctions, proposed interface, and next research question are AI-assisted conceptual development from the existing HayosoAi case. They have not received independent human review and no effectiveness or novelty claim is established.

The [founding essay](../../docs/hayosoai/beta/downloads/declarative_essay.en.md) and [Project Compass](../PROJECT_COMPASS.md) remain the source context. The essay's physicalist account and identification of consciousness with interpretive intelligence, distinct from felt experience, are philosophical positions, not findings established by this note. The original essay and logo are unchanged. The case, its exports, and Pilot 01 were not edited or rerun. No new license, institutional endorsement, or external adoption is implied. Drafted by ChatGPT under HayosoAi project direction.
