# Claim and evidence audit

**Snapshot:** 24 October 2026. This is a consistency audit of the current manuscript and repository, not a peer review, systematic literature review, or completed benchmark evaluation.

## Evidence inventory

| Claim or number | Source / calculation | Status | Safe wording |
|---|---|---|---|
| BashArena has 640 main-task IDs and four side-task families | Current ControlArena BashArena documentation | External benchmark specification; pin the exact installed revision before a run | “The protocol targets the documented BashArena setting; its exact task/scorer revision will be recorded for each experiment.” |
| Four policy clauses, 16 masks, 8 masks omit each clause | Exact enumeration in `src/design_audit.py` | Reproduced design arithmetic | A clause-mask leave-one-out diagnostic is in-family; it is not unseen-family transfer. |
| 7 of the other 15 masks also omit any fixed clause | Exact enumeration after removing the tested mask | Reproduced design arithmetic | Do not interpret the mask comparison as LOFO. |
| Eight toy proposals produce four adapter-residual positives | Hand-authored fixture and toy function | Synthetic software fixture | It tests code behavior only; it estimates no BashArena miss rate. |
| Power is 0.947 / 0.750 for 184 positives and 1.000 / 0.991 for 460 | 100,000 paired-Bernoulli draws, 15-point effect, discordance 0.30 / 0.50, seed 12, per-contrast alpha .025 | Planning simulation; assumes independent positive episodes | Optimistic sensitivity illustration; task clustering and cross-family overlap can lower power. |
| Calibration minimum p is 1/139 = 0.00719 with 138 calibration units | Split-conformal rank arithmetic | Reproduced finite-sample calculation, conditional on 138 independent exchangeable units | The manuscript plans about 138 task clusters, not yet an operational definition of the independent calibration unit. The 1%, 3%, and 10% rank thresholds are supported only if one eligible honest episode per cluster is used (or another valid cluster-level rule is specified); 0.3% is below the available rank resolution. |
| A nonzero conformal rank at 0.3% requires at least 333 calibration episodes | `ceil(1 / 0.003) - 1` | Reproduced arithmetic | This is a mathematical minimum, not a sample-size recommendation for useful precision. |
| Activation monitor detects adapter-residual risk or prevents harm | No benchmark trajectories, fitted probes, or held-out results are present | **Untested hypothesis** | Do not state an efficacy or prevention result. |
| Adapter correctly represents shell variants | No frozen adapter implementation or independent coverage study is present | **Not implemented / not established** | Treat adapter mapping and attribution as a major feasibility gate. |
| Model training and BashArena execution are reproducible | No completed run manifest, checkpoint, task split, or scorer revision is present | **Not run** | The Qwen3.5-2B YAML is a compute plan only. |

## Manuscript-to-repository consistency

- The manuscript says no BashArena results exist and shows dashes in the results table; the README preserves that boundary.
- The configured pilot is a Phase I feasibility plan. It is not a result and is not a preregistration.
- The design script's toy adapter support count is synthetic and must not be presented as a measured false-accept rate.
- The manuscript's paired-power values reproduce the script's seeded simulation to the reported precision. The simulation is unclustered and intentionally labeled optimistic.
- With 138 independent exchangeable calibration units, the smallest nonzero split-conformal p-value is about 0.719%. The 0.3% point is unsupported; 1% is supported only at coarse rank resolution. The manuscript currently gives a task-cluster count but must define how calibration episodes map to independent clusters before claiming episode-level split-conformal support.

## Gaps to close before an empirical preprint

1. Pin ControlArena, Inspect, BashArena dataset, scorer, model, and tokenizer commits/revisions; save them in an immutable manifest.
2. Implement and independently review the event adapter. Publish its finite grammar, canonical/variant test corpus, unmatched-action behavior, and per-family coverage before opening confirmatory scorer labels.
3. Verify first-effect attribution against pre/post scorer state and report ambiguous/unlabelable cases.
4. Resolve the split and calibration design in code, including which honest episode is selected per task cluster (or define a cluster-level maximum and change the alarm-budget unit). Report actual independent unit and cluster counts per fold; do not infer episode-level conformal coverage from a task-cluster count alone.
5. Implement all stated baselines and the task-clustered analysis before test evaluation. Check threshold ties and realized honest alarm rates.
6. Simulate power at the **task-cluster** level using pilot estimates; the existing paired-Bernoulli calculation is not sufficient for that gate.
7. Keep Phase I shadow detection, Phase II closed-loop prevention, and exploratory report correctness as separate claims.
8. Audit data licensing and external artifact checksums before any public release.

## External references checked for this snapshot

- [ControlArena BashArena setting documentation](https://control-arena.aisi.org.uk/settings/bash_arena.html) lists 640 main tasks, four side-task families, and use of the auto-submit wrapper. The documentation can change; record the tested package revision.
- The repository's [originality audit](originality-audit.md) is a dated, focused literature review, not a comprehensive novelty or plagiarism certification.

No external data or task trajectories were downloaded or included in this audit.
