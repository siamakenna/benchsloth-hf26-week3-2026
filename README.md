# BenchSloth v0.6 — an attention plan around evidence

A local Gemma attention agent for source-linked laboratory notes: original passages, an Attention Map, experimental evidence questions, explicit review, manually confirmed timers and an original-source return handoff. Synthetic research-organizer preview; no equipment control or physical experiment verification.

**Public publication remains on hold.** The exact clean snapshot, Pages deployment and DEV post require owner approval. Intended repository: `siamakenna/benchsloth-hf26-week3-2026`. Intended demo: `https://siamakenna.github.io/benchsloth-hf26-week3-2026/`. These are planned destinations, not verified live URLs.

## Explore without installation

Open `demo/index.html`: choose A/B/C, inspect source associations, select authentic recorded questions, open excerpts and real requests, make a correction, confirm a10-second demonstration, enter Breathing Room and return to current browser facts. The static experience makes no inference API calls. Recorded Gemma output and deterministic browser functionality are separately labeled. Arbitrary fresh questions require the local app.

Open `demo/evidence/index.html` for **Does BenchSloth Actually Work?** All24 frozen QA cases, references, baseline/model/combined outputs, filters, raw evidence, configuration and reproduction are readable without downloading JSON. Optional exports remain available.

Captioned genuine live inference: `assets/v6/demo-captioned.webm`. Final article: `docs/DEV_POST_FINAL.md`; local images/links preview: `docs/DEV_POST_LOCAL_PREVIEW.md`.

## What the evidence supports

| Frozen QA comparison | Exact status + evidence | Exact QA workflow | Unsupported answers |
|---|---:|---:|---:|
| Strong rules + retrieval |14/24|14/24|7|
| Raw Gemma |13/24|11/24|11|
| Combined candidate |15/24|13/24|8|

**No reliable model advantage is established.** The3-passage retrieval shortlist contains all required evidence for16/16 answerable questions. Mean local Gemma request25.40s,max62.97s; rules mean0.00067s. The combined candidate's95% descriptive Wilson interval for exact evidence cases is42.7–78.8%; related synthetic wording and assistant-authored, implementer-visible labels limit generalization. Model relationships therefore ship as experimental proposals requiring human review. A valid quote does not prove a correct interpretation. The UI narrowing is not rescored as improved accuracy.

QA is read only and grants no timer permissions. The separate unchanged v0.5 planner benchmark:20cases140lines,22/22 reference links,1 extra unresolved association,16/18 eligible waits,0 observed unsupported offers,17/20 exact plans. Strong scoped rules tie. A separately frozen actual18/21/25-line supplement:6/6 links,3/3 waits for both; not pooled. Original v0.4 six-line failures and every historical benchmark remain preserved. Exact plans/QA workflows do not measure human or physical task success.

Independent human source adjudicators and usability participants: **n=0**. No measured time savings. The no-install researcher packet includes blinded questions and a condition-rotated raw/numbered-source/actual-product task trial. No participant responses are included.

## Run fresh local inference

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
ollama pull gemma3:4b
ollama serve
.venv/bin/uvicorn server_v6:app --host 127.0.0.1 --port 8772
```

Open `http://127.0.0.1:8772`, edit approved non-sensitive source, analyze, then ask a question. Local Gemma3:4b Q4_K_M uses temperature0,seed42,4096-token context and24 output tokens per evidence choice. Planner and QA have separate bounded calls. QA accepts at most48 source lines/12000 source characters/500 question characters, plus a14000-character assembled prompt budget and90-second timeout. Long unsupported contexts fail visibly. No hidden retries or prepared substitute on failure. One local QA request at a time; stale session responses are discarded. Do not expose this unauthenticated development server publicly.

Direct questions use deterministic retrieval after the model request, so they still incur model latency and outage dependency. Missing-information handling is narrow; broad factual QA and semantic verification remain experimental. Browser timers are convenience displays and can be delayed by sleep, throttling or clock changes. Required observation still applies.

## Reproduce and verify

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/v6/evaluate.py final
.venv/bin/python scripts/v6/summarize.py
.venv/bin/python scripts/v6/build_explorer.py
.venv/bin/python scripts/v6/build_replay.py
```

The evaluator writes missing runs only. To make fresh requests, use a copied checkout and move `evaluation/v6/final-run` aside. Preserve shipped records. Data freeze ae08aab and engine freeze af4bfae precede final inference; hashes are in evaluation/v6. Three designs were tried on6 development examples; all18 development outputs and both prototypes remain available. Evaluation of v0.5 QA is explicitly a source-view/retrieval adapter, not a native QA inference run. Native historical planner runs stay separate.

Browser checks use Playwright (package.json): `node scripts/v6/browser.cjs` against loopback; `node scripts/v6/pages.cjs` serves the actual project subpath. They are automated flows, not human outcomes. See `evaluation/v6` for saved checks and actual requests. Building the optional source ZIP requires the complete checkout; the interactive product and evidence explorer do not require a download.

## Architecture and release records

- `docs/AGENT_ARCHITECTURE_V6.md`: two authority paths, contracts and session state.
- `docs/GEMMA_VALUE_EVALUATION.md`, `docs/SEMANTIC_ERROR_ANALYSIS.md`: complete comparison and disagreements.
- `docs/PUBLIC_EXPLORER.md`, `docs/DESIGN_SYSTEM_FINAL.md`: experience, scope and design.
- `docs/HUMAN_VALIDATION.md`: genuine independent-review status.
- `docs/JUDGE_SCORECARD_FINAL.md`: adversarial AI review, unofficial weights and weaknesses.
- `docs/PUBLIC_DISCLOSURE_MANIFEST.md`, `docs/SUBMISSION_VERIFICATION.md`: exact payload scope and approval hold.

Original source/artwork: MIT. Google Gemma model weights have separate terms and are not redistributed. No paid inference service, private protocol, credential, full Codex conversation or researcher response is shipped. BioRender, Canva, Base44 and Lovable are not claimed as runtime integrations. Project development began October23,2026; a clean public snapshot does not rewrite the preserved local development history or backdate project creation.
