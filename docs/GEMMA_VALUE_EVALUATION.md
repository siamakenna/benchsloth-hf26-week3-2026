# Does Gemma add value? — v0.6 frozen comparison

**A reliable accuracy advantage is not established.** The combined candidate agent selects one more exact evidence set than rules, but completes fewer exact QA workflows, offers more unsupported answers and costs substantial CPU latency. Strong retrieval already includes every required reference passage in its top3 on all16 answerable questions. This is not evidence that Gemma improves the complete task.

Gemma now performs real, inspectable source-evidence and relationship selection. This is a stronger product interaction than another duration classifier, but capability implementation is not proof of comparative usefulness. The release therefore presents model relationships as **experimental proposals requiring human review**, never automatic map changes. This presentation narrowing does not rescore failed cases or claim perfect abstention.

## Prospective protocol and configuration

Data freeze ae08aab precedes semantic prompt development. Engine/evaluator freeze af4bfae precedes final inference. SHA256 files are in DATA_FREEZE.json and ENGINE_FREEZE.json. Historical datasets/runs are unchanged. Six development examples informed three designs: broad structured QA, numeric candidate choices, then copied-text candidates. All18 development outputs and two prototype implementations are preserved. The final configuration adds section metadata and stronger deterministic direct-question routing, frozen before final inference. No final case was rerun or tuned after its result was inspected.

Final set:24 assistant-authored, implementer-visible synthetic questions;16 answerable,4 ambiguous,4 no-answer. Eleven have question-specific relationship references:7 concrete links and4 unresolved targets. Sources reach25 lines;6 cases have13–25 lines. Repeated templates and archive distractors reduce effective independence. Independent human adjudication n=0. This is a prospective final set, not a blinded external test.

Model: locally cached Gemma3:4b Q4_K_M on a16GB Intel CPU Mac, Ollama0.40.10, temperature0,seed42,4096 context,24 generated-token cap,90-second request timeout,no retries. Context is bounded at14000 assembled prompt characters; token coverage beyond this tested source range is unproven. No larger suitable cached model was available; the smaller cached1B was not substituted to improve a headline.

Strong baseline: BM25 with headings, generic synonyms, explicit fact checks and v0.5 structural candidate rules. It displays a3-passage shortlist plus full source; direct answers use the best passage, and contradictions use both relevant passages. The v0.5 source-view adapter is intentionally the same baseline: v0.5 did not have native QA. It is **not a new measured v0.5 QA inference run**. Historical native v0.5 planner evaluation is separate.

## Results

| Approach | Exact status+IDs | Descriptive Wilson95% | Unsupported answers | Correct abstention status | Missed answerable | Exact QA workflow | Mean / max request |
|---|---:|---|---:|---:|---:|---:|---|
| Strong rules + retrieval | 14/24 | 38.8%–75.5% | 7 | 8/8 | 3/16 | 14/24 | 0.001s / 0.00s |
| v0.5 source-view adapter | 14/24 | 38.8%–75.5% | 7 | 8/8 | 3/16 | 14/24 | 0.001s / 0.00s |
| Raw Gemma evidence selection | 13/24 | 35.1%–72.1% | 11 | 3/8 | 0/16 | 11/24 | 25.403s / 62.97s |
| Combined candidate agent | 15/24 | 42.7%–78.8% | 8 | 7/8 | 0/16 | 13/24 | 25.403s / 62.97s |

Unsupported answer means confident answer status with wrong/extra evidence, or where the reference calls for abstention. It does not mean an invented quote or timer permission. Correct abstention status excludes whether its evidence IDs match; primary exact scoring includes that. Missed answerable means an answerable question was abstained on, not all wrong evidence selections. Exact workflow requires status, exact IDs and exact question-specific relationship; no human or physical completion is measured. Overlapping intervals and correlated small synthetic cases do not establish a statistically persuasive improvement.

| Question-specific link metric | Rules | Raw Gemma | Combined candidate |
|---|---:|---:|---:|
| Concrete links recovered |1/7|1/7|1/7|
| False concrete associations |3|7|6|
| Link precision |25.0%|12.5%|14.3%|
| Link recall |14.3%|14.3%|14.3%|
| Exact relationship answers incl. unresolved |5/11|4/11|4/11|

The primary evidence score can count the correct passages even when the proposed relationship is wrong. Q17 is exactly that distinction: Gemma finds the copper-tray passages4 and13, but labels their relationship unclear instead of after. Treating15/24 as15 fully correct semantic answers would be misleading. The stored field name `verified_agent` is historical evaluation terminology for the combined candidate; verification checks source identity, not entailment.

## Timer and workflow isolation

QA is read only; it makes no timer offers. All24 request records completed without transport/schema errors; the means above include all24 real calls. Direct deterministic answers still wait for the model request before routing, so their latency/outage dependency remains a limitation.

The unchanged v0.5 planner's **separate**20-case set has22/22 reference links,1 extra unresolved association,16/18 waits,0 observed unsupported offers and17/20 exact plans; strongest rules tie accuracy. Separate actual18/21/25-line supplement:6/6 links,3/3 waits,0 unsupported offers for both. These are not pooled with QA. Browser tests exercise actual10-second demo timers; they do not establish laboratory safety, user time saved or physical task success.

## Reproduction and disclosure

Run `scripts/v6/evaluate.py final`, then `scripts/v6/summarize.py`; the evaluator writes only missing records. For a fresh inference run use a copied checkout with final-run moved aside. Raw source, references, proposals, actual requests/responses, routing and per-case scoring are in the no-download public explorer and evaluation/v6. The model result is preserved even when rejected or bypassed. No hidden success-only reruns or independent-human claims are made.

The highest-value next correction is better relationship interpretation and no-answer calibration, independently adjudicated against the retrieval shortlist. Until then, source search and human review carry the product; a broader model-authority claim is unsupported. This limitation should not delay an otherwise honest, authorized submission past the deadline.
