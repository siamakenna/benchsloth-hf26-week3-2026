from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];data=json.loads((R/'evaluation/v6/explorer-data.json').read_text());s=data['summary'];cases=data['cases']
rows=[]
for k,label in [('rules','Strong rules + retrieval'),('v5_source_view','v0.5 source-view adapter'),('raw_gemma','Raw Gemma evidence selection'),('verified_agent','Combined candidate agent')]:
 m=s[k];ci='–'.join(f'{x*100:.1f}%' for x in m['exact_wilson95']);rows.append(f"| {label} | {m['exact']}/24 | {ci} | {m['unsupported_answer']} | {m['abstention_correct']}/8 | {m['missed_answer']}/16 | {m['complete_workflow']}/24 | {m['mean_seconds']:.3f}s / {m['max_seconds']:.2f}s |")
body='''# Does Gemma add value? — v0.6 frozen comparison

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
'''+ '\n'.join(rows)+'''

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
'''
(R/'docs/GEMMA_VALUE_EVALUATION.md').write_text(body)
lines=['# Semantic error analysis — v0.6','', 'All24 original final outcomes are retained. No error is repaired in the frozen records. References are synthetic and independently unadjudicated.','', '| Case | Tags | Rules exact | Raw exact | Combined exact | Combined reference disagreement |','|---|---|---:|---:|---:|---|']
for r in cases:
 c=r['case'];p=r['gemma'].get('answer',{});g=c['reference'];issues=[]
 if p.get('status')!=g['status']:issues.append(f"status {p.get('status')} vs {g['status']}")
 if p.get('source_ids')!=g['source_ids']:issues.append(f"IDs {p.get('source_ids')} vs {g['source_ids']}")
 if p.get('association')!=g['association']:issues.append('relationship differs')
 lines.append('| '+c['id']+' | '+', '.join(c['tags'])+' | '+ ' | '.join('yes' if r['scores'][k]['exact'] else 'no' for k in ['rules','raw_gemma','verified_agent'])+' | '+('; '.join(issues) or 'exact evidence; inspect relationship separately')+' |')
lines+=['','## Main failure families','','Named short cross-section references can choose the nearest wrong wait; longer context is not automatically better. Q17 finds the right passages but not the correct relation. Q19 overcommits on an explicitly unspecified21-line source; identity checks reject that proposal, but the resulting no-answer differs from the expected ambiguity response. Raw Gemma answers missing-parameter questions using unrelated real passages; direct deterministic routing fixes the four tested no-answer questions but is not general missing-information detection. Q07 confuses during/after despite correct citations. Q20 selects the wrong section on25 lines.','','The strong retrieval shortlist contains all gold passages for16/16 answerable cases. The model has not shown an advantage over a person inspecting that shortlist. Do not compare free-text fluency against rules that cannot write prose.','','Engineering reviewer probes outside the frozen set: a during proposal for an explicit after note can pass identity checks; an absent pressure question can retrieve an irrelevant wait. These are disclosed qualitative counterexamples, not added to the24-case denominator. Broader factual QA and semantic verification remain experimental.','','Shipped presentation narrows authority: every Gemma relationship is a review-required proposal. No automatic association or timer permission is granted from QA, and the narrowing is not retroactively scored as model accuracy.']
(R/'docs/SEMANTIC_ERROR_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
