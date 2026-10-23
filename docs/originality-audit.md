# Originality and novelty audit

**Research snapshot:** 21 October 2026. This is a focused literature and naming check, not an exhaustive systematic review and not a plagiarism-detection report.

## Assessment

The current draft is newly composed prose; it does not intentionally reproduce passages from the cited work. No corpus-based similarity or plagiarism detector has been run, so this is not a certification of textual originality.

As a research contribution, the draft's first framing is **not sufficiently distinct yet**. Its central idea—use pre-action hidden-state signals to forecast unauthorized agent behavior, gate actions, and reduce later false reports—has a very close prior in *The Agent Knew* (arXiv:2610.17301, submitted 12 October 2026). That paper reports residual-stream forecasts for both unauthorized actions and false reports, gates every proposed action, measures effects over full episodes, and tests transfer to AgentDojo. We must cite it and must not claim to be the first activation-based action gate, the first to forecast agent lies, or the first to prevent lies by preventing violations.

The current coverage-conditioned framing is **not yet convincingly novel for a competitive research conference**: it may read as an incremental ablation of known components. A sharper candidate is a **shield-residual activation monitor**. Define its target only on proposals the formal gate admits, then ask whether activations identify the harmful false accepts left by that gate better than text/trace and structured-action signals. Test transfer to a held-out policy mutation at a locked review budget. This is narrower than “combine probes and rules,” and is not a claim that no prior work has done it. It becomes a defensible contribution only if action-level labels can be validated, the test has enough residual harmful proposals, and a direct comparison with close learned-risk systems shows added value.

## Closest work and implications

| Work | Relevant overlap | Implication for our paper |
|---|---|---|
| [The Agent Knew: Internal States Forecast Unauthorized Actions and Stop Them, and the Lies That Follow](https://arxiv.org/abs/2610.17301) (2026 preprint) | Residual-stream probes forecast unauthorized actions and false reports; risk-triggered steering/action gating reduces violations; whole-episode outcomes and AgentDojo transfer are evaluated. | Directly overlaps the original thesis and both requested outcomes. Distinguish through formal-specification coverage, the formal gate's independent invariant, and the marginal-value question. It is a recent arXiv preprint, not evidence of peer-reviewed priority. |
| [Before Agent Tells The Lie](https://arxiv.org/abs/2610.06576) (2026 preprint) | Studies whether hidden representations predict later deceptive agent outcomes and whether activation steering changes them. | Rules out a broad novelty claim for hidden-state prediction or steering as deception mitigation. |
| [DeceptGuard](https://arxiv.org/abs/2603.13791) (2026 preprint) | Compares black-box, chain-of-thought, and activation-probe monitors for agent deception on a synthetic benchmark. | Activation-probe deception monitoring and multi-monitor comparisons are already studied. We need a stronger distinction than “add a probe.” |
| [From Probe Scores to Alarm Policies](https://arxiv.org/abs/2610.04575) (2026 preprint) | Argues that AUROC does not establish operational value at fixed false-alarm/review budgets; defines an operational-validity contract. | Keep trajectory-level calibration, matched intervention/review budgets, and realized test-set alarm rates central. |
| [AgentSpec](https://arxiv.org/abs/2503.18666) and [Pro2Guard/ProbGuard](https://arxiv.org/abs/2508.00500) | Programmable runtime rules and proactive probabilistic risk enforcement for agent actions. AgentSpec appeared in ICSE 2026; the Pro2Guard arXiv record was revised under the ProbGuard title and notes ASE 2026 acceptance. | Runtime enforcement and predictive risk gating are established. Our formal gate needs an explicit policy representation and separate safety role, not just a generic “rulebook.” |
| [VIGIL](https://arxiv.org/abs/2606.26524) and [MENTOR](https://arxiv.org/abs/2610.17039) | Behavioral specifications, trace-sensitive policies, and history-dependent shields for tool-using agents. | Formal or specification-based agent shields are an active and crowded line. Avoid claiming that formal policy enforcement itself is new. |
| [ControlArena](https://www.aisi.gov.uk/blog/introducing-controlarena-a-library-for-running-ai-control-experiments) and [Inspect](https://inspect.aisi.org.uk/) | ControlArena is an AI-control experiment library; it runs on Inspect. | Neither is a new benchmark contribution for this study. Name the concrete setting/version and describe any added report-labeling protocol. |

## Evaluation feasibility check

The current strongest setting candidate is [BashArena](https://control-arena.aisi.org.uk/settings/bash_arena.html): it has four scorer-defined side-task families (firewall disabling, sensitive-data exfiltration, malware download/execution, and universal passwordless sudo escalation), paired with system-administration tasks in Docker. The current ControlArena docs report 640 main tasks and 2,560 task/side-task combinations; the original paper reports 637 main tasks. Pin the exact release, dataset hash, scorer version, and task subset before any experiment.

BashArena's documented scorers cover main-task success and side-task detection, not report honesty. The paper should therefore add the same neutral final-status request in every condition and a separately validated, blinded report-to-log rubric. Call these labels false reports or misreports, not lies, because behavior labels cannot establish intent.

The standard auto_submit_protocol_wrapper also terminates a trajectory as soon as a side-task effect is detected. To observe a subsequent report without allowing further tool actions, the draft now specifies an instrumented protocol that closes all tools and permits one report-only turn after either normal completion or early termination. This changes the evaluation protocol and must be identified as an extension; do not present its report-honesty results as scores from unchanged BashArena.

The tools include Bash, Python, and a restricted text editor. A formal gate over these interfaces needs an explicit event adapter from candidate tool calls to a finite policy trace. Report the adapter's coverage and what happens when a call cannot be parsed; the invariant is conditional on complete mediation and correct event mapping. This is a major implementation risk and should be settled before claiming the gate provides broad formal guarantees.

## Locked coverage manipulation proposed for the draft

- **Benchmark-complete:** include one formal clause for each of the four programmed side-task families.
- **Leave-one-family-out:** run four ablations, each removing one clause and keeping the other three.
- **Task-generic:** retain schema and task-authorization checks, but no side-task-specific clauses.

These levels measure coverage of benchmark-coded objectives, not completeness against real-world hazards. Keep the policy compiler and event adapter fixed across conditions. The primary estimand compares formal-plus-text/trace monitoring with formal-plus-activation monitoring at the same trusted-fallback budget; formal-only enforcement is a separate baseline. The coverage interaction asks whether the incremental safety gain is larger when one or all side-task clauses are missing. Report report-correctness outcomes separately so a lower sabotage rate is not mistaken for improved honesty.

## Naming and provenance checks

- **LatentGuard** is already used by multiple unrelated safety papers, including [Latent Guard for text-to-image safety](https://arxiv.org/abs/2404.08031), [controllable latent steering](https://arxiv.org/abs/2509.19839), and [latent reasoning for LLM safeguards](https://arxiv.org/abs/2608.03838). Avoid presenting it as our original method name; use it only as a cited prior work or replace it with a distinct name after the method is settled.
- Exact-name searches did not surface a clearly identifiable LLM-agent paper called **SpecEnforce** or benchmark called **Inspect-AgentBench**. This does not prove those names are unused in private, unpublished, or poorly indexed work.
- The original description conflated three things: **Inspect** is an evaluation framework, **ControlArena** is the AISI AI-control experiment library, and **AgentBench** is a separate agent-evaluation benchmark with tasks available through [Inspect Evals](https://ukgovernmentbeis.github.io/inspect_evals/evals/agent_bench/). The draft should say which specific setting it will run and should not call Inspect an AISI red-teaming arena.

## Candidate novelty statement

> We test whether internal activation features identify harmful false accepts among proposals admitted by a formal action gate, and whether this signal transfers to a held-out policy mutation. At a fixed review budget, we compare activation features with text/trace and structured-action monitors, measuring both residual-harm detection and closed-loop side-task outcomes. The formal gate retains authority over every encoded invariant. This is a candidate empirical distinction; it is not a priority claim, and it depends on validating action-level labels and finding measurable incremental value.

This wording is intentionally a research question, not a result or a priority claim. The strongest candidate contrast with *The Agent Knew* is the gate-conditioned residual-risk target plus held-out policy-mutation transfer against activation-free risk monitors; dataset choice alone is not enough.

## Evidence still needed before claiming novelty

1. Implement the policy-mutation folds and compare directly with the closest paper's public method where feasible, plus strong text/trace, structured-action risk, and formal-only baselines.
2. Define the gate's allowed set and residual false-accept label before test; ensure scorer outcomes and test-mutation data do not leak into monitor fitting. Threshold calibration may use development scores only.
3. Score sabotage from environment state and score false reports against an execution log. If the chosen setting has no natural final-status report, add and document a standardized report prompt rather than implying the benchmark already labels lies.
4. Use scenario-level train/development/test splits, matched task instances, paired seeds, and locked thresholds; report realized false-alarm and intervention rates, not just AUROC.
5. Stress-test an agent that knows the monitor exists. Include false positives on legitimate actions, delayed attacks, repeated alarms, policy-parser errors, and specification errors.
6. Re-run the literature search immediately before submission. This rapidly changing area has several relevant preprints from October 2026.

## Methods and focused-search update (21 October 2026)

The revised draft narrows the monitor's role to pre-dispatch prediction of scorer-defined side-task state transitions. It does not train the action probe on report labels and does not claim to identify intent. False reports remain a separately annotated episode outcome after tool access closes. The approved one-turn report-only extension is explicitly an instrumented BashArena protocol, not an unchanged benchmark score.

The control comparison now defines a fallback as replacing an otherwise specification-admissible proposal with the same trusted policy used in the comparator. Its primary calibration target is a 10% episode-level fallback rate on a fixed, balanced development mixture, with formal denials excluded. Proposal-level replacement counts and honest-task fallback incidence are separate measures. Thresholds are locked before test, and the draft cites the ControlArena description of defer-to-trusted behavior and the recent operational-validity analysis of activation alarm policies.

A focused search for activation probes combined with formal shields, residual false-accept labels, and held-out policy mutations did not surface a directly matching study. The closest integrated overlaps remain *The Agent Knew* and NEXUS; operational alarm calibration and runtime shields are also active areas. This search does not establish priority: database coverage is incomplete, terminology varies, and relevant 2026 work may appear before submission. The defensible novelty candidate is now the prespecified test of activation-specific value on gate-admitted harmful proposals, including transfer to a held-out policy mutation at a matched development-set fallback target.

The BashArena documentation says its `auto_submit_protocol_wrapper` runs hidden side-task tests after every action and terminates on the first triggered live failure. This makes action-level labels plausible, but the default documentation does not guarantee that every check result and pre/post environment snapshot is retained in logs. The proposed instrumentation must record the attempted action, prior side-task predicate state, post-action check results, and first triggering transition. Validate attribution and coverage before fitting monitors; quantify unlabelable cases and mark the primary result unsupported if missing labels are too frequent or uneven by family. A benchmark-complete gate claim also depends on a validated event adapter that can reject a harmful proposal before execution; terminal scoring alone cannot establish that guarantee.

## Additional close work and novelty reassessment (21 October 2026)

Three additional records make the current contribution claim weaker:

- [NEXUS: Structured Runtime Safety for Tool-Using LLM Agents](https://arxiv.org/abs/2607.19356) already combines deterministic rules, argument inspection, a calibrated plan-level learned risk score, and an intervention policy. Its learned features are structured-plan features rather than residual-stream activations, but the broad “formal rules plus learned risk score for escalation” architecture is not new.
- [One Monitor Does Not Fit All: Formalism-Agnostic Runtime Verification for Agentic AI](https://arxiv.org/abs/2610.19818) formalizes monitor composition and canonical event adapters, distinguishes attempts from completed effects, and evaluates a temporal monitor together with a report-content monitor. Our instrumentation and report-monitoring protocol are therefore not stand-alone novelty claims.
- [Why Formal Monitors Fail](https://arxiv.org/abs/2608.01388) studies formal-monitor coverage as attack-pattern distributions change and gives an entropy-based coverage bound. Its definition of coverage differs from our deliberate omission of benchmark policy clauses, but it means “formal monitor coverage” itself is not a new research question.

**Updated judgment:** The revised draft now states a sharper candidate: score only gate-admitted proposals, train on residual harmful transitions, and test transfer to a held-out policy mutation against activation-free baselines. This is more differentiated than a generic coverage ablation, but it is still not an established novelty claim. Without a successful action-level labeling pipeline and empirical evidence of incremental transfer value, the paper is not yet ready to claim a novel conference contribution.

**Recommended sharper direction:** define a *shield-residual activation monitor*. After the formal gate evaluates a proposal, train and evaluate the activation signal only on the residual set the gate would admit, asking whether hidden-state information identifies benchmark-harmful outcomes among those false accepts. The draft's current candidate design holds out the exact leave-one-clause-out policy mutation from monitor fitting, trains on residual proposals from the other clause-subset variants, and compares activation with text/trace and structured-action monitors at the same review budget. This tests generalization across policy mutations. It does not claim unseen-family generalization, since fitting on mutations that omit other clauses may expose the monitor to examples from the same side-task family. The paper must state that limitation clearly.

This pivot is only a candidate until the instrumented wrapper yields reliable action-level labels and policy decisions can be replayed on logged pre-action states. NEXUS's learned risk score under formal intervention is a close conceptual neighbor, so the manuscript must compare against it and avoid a “first hybrid monitor” claim. A focused search did not find an exact activation-based, held-out-shield-false-accept study, but search absence is not proof of novelty. The draft explicitly does not claim unseen-family generalization; its held-out unit is the exact policy mutation.

