# v0.5 frozen length-stratified evaluation

Data freeze `b1f1b4d`; candidate/evaluator freeze `3590ade`. Hashes in `evaluation/v5/data-freeze.json` and `candidate-freeze.json`. Twenty varied prospective synthetic cases,140 source lines,22 reference associations,18 eligible waits. Five cases per group:1–3,4–6,7–12,13–25 lines. The actual longest frozen case is 15 lines; the 13–25 bin does **not** establish 25-line reliability. Source length bounds are group names, not proof of coverage at every length. Labels were coding-assistant-authored, visible to the implementer and not independently adjudicated. Raw responses, prompts, output budgets and measured workflow times are retained. No retries or held-out tuning.

| Method on same 20 cases | TP / FP / FN | F 1 | Waits recovered | Unsupported offers | Exact workflows | Mean workflow seconds |
|---|---:|---:|---:|---:|---:|---:|
| Strong scoped rules |22 /1 /0|97.78%|16/18|0|17/20|0.0043|
| Unchanged v4 whole-protocol Gemma |9 /1 /13|56.25%|16/18|1|9/20|17.167|
| V5 focused Gemma + scoped verification |22 /1 /0|97.78%|16/18|0|17/20|5.779|

| Length bin, n=5 each | V4 exact links / reference | V5 exact links / reference | V5 wrong / missed | V5 wait recovery |
|---|---:|---:|---:|---:|
|1–3|3/3|3/3|1 /0|2/2|
|4–6|2/6|6/6|0 /0|5/5|
|7–12|1/6|6/6|0 /0|6/6|
|13–25(actual max 15)|3/7|7/7|0 /0|3/5|

“Exact workflow” in the frozen JSON means the entire accepted association set and offered timer-ID set match the reference. It is an exact plan metric, not a claim of human task success or physical experiment completion. Timer/user-state behavior is checked separately.

All methods produced 20/20 structurally valid plans and zero model/schema failures. V5 and scoped rules had 5 explicit unresolved associations; these include correct uncertainty labels and one extra unresolved paragraph association, so abstention is not automatically an error. Same-length rules/v5 metrics match. The model's incremental accuracy over the stronger rules is **not established** here. The measured improvement over v4 comes from structural candidates, a focused classification task and source policy together; do not attribute it all to Gemma.

Three remaining failed exact workflows: P 01 contains a single unstructured paragraph with wait, after-action and monitoring; v5 adds an unresolved association where the reference has no cross-occurrence link. This is a short-case regression versus v4. X 02's `# Observation` heading is over-read as monitoring, blocking an unrelated valid wait. P 04's `Record unrelated observation` notes over-trigger monitoring and block a later valid wait. These conservative losses remain unchanged after final inference. They are not relabeled as successes. V4's unsupported offer occurred on the forward-reference case P 02 under this reference policy; zero observed v5 offers is limited evidence, not general safety validation.

The earlier 32-case 22/22 result remains historical, on a different short corpus. Do not combine its denominator with this one. Exact original six-line failures were also re-run separately as exposed development evidence: v5 recovered both explicit ordinal links; on the original deictic version it recovered one link and left the second target unresolved. Raw files in `evaluation/v5/exposed-originals/`; these are not additional unseen successes.

Latency is local CPU workflow wall time, not controlled hardware, cold-start or model-only latency. Structural abstention cases make no model call and reduce the mean; v5 maximum 15.332 s, v4 maximum 61.459 s. There is no cloud inference fee; electricity, hardware and model download costs are not measured. No human time-saved result.

Replication: `python evaluation/v5/run.py --split holdout --out evaluation/v5/new-replication`. It refuses existing output directories and checks frozen source hashes. The exposed-set replication is not a new unseen test. `runtime_v5.py` supplies session-only atomic checkpoint recovery and heading-skipping handoff; it does not alter the frozen inference policy or evaluated map.

## Separate actual 18/21/25-line supplement

The initial 13–25 bin stopped at 15 lines. Three additional boundary cases were frozen at `be5febc` after architecture selection but before any boundary inference, with the engine unchanged. They are not a preselection holdout and are not pooled with the 20-case score. Across 64 source lines/6 reference links/3 eligible waits, v4 recovered 1/6 links and 2/3 waits (0/3 exact workflows); v5 and strong rules both recovered 6/6 links and 3/3 waits (3/3 exact workflows). Zero unsupported offers and zero schema failures for all. Mean workflow time v4 33.779 s, v5 12.104 s. One correct unresolved target is an abstention. Three boundary examples cannot establish general 25-line reliability. Raw evidence and separate summary are in `evaluation/v5/boundary-run/`.
