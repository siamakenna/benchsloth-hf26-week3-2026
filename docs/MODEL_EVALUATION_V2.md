# V2 model evaluation — source-first waits and temporal attention links

## What changed and why

The historical V1 result remains unchanged: the final Gemma gate offered 3/13 gold
waits while guarded rules offered 10/13. `docs/MODEL_EVALUATION.md`, original raw
records and `docs/JUDGE_SCORECARD.md` remain intact. V2 assigns Gemma a different task:
associate contextual notes with earlier source occurrences. The model no longer
classifies a simple wait as a prerequisite for a timer.

The measured improvement is **exact temporal source-link recall/F1**, not superior
wait detection or demonstrated human time savings. A stronger design has not made
all model outputs reliable.

## Prospective V2 comparison

30 held-out synthetic cases; 68 source lines; 24 gold temporal links; 16 gold fixed
waits. See `evaluation/v2/RESULTS.md` for the generated comparison table and raw
`holdout-4b/summary.json` / `holdout-1b/summary.json` when complete.

Gemma 4B: 20 TP, 4 FP, 4 FN; precision 83.33%, recall 83.33%, F1 83.33%.
Guarded lexical associations: 14 TP, 1 FP, 10 FN; precision 93.33%, recall 58.33%,
F1 71.79%. Gemma finds six more exact links with three more false links. The F1
increase is 11.54 percentage points, with a precision tradeoff. No significance,
population-level accuracy or model stability claim follows from this small single pass.

Timer coverage: 4B hybrid 11/16; rules 14/16. Unsupported timer eligibility: zero
observed for both across 68 source lines. Valid plans: 30/30 for both, preserving
all 68 source occurrences. Zero missing, fabricated, reordered or duplicated accepted
steps: `build_plan` reconstructs each original occurrence deterministically, while
`validate_links` requires the complete exact key set and earlier target IDs.

The model's review flags reduced timer coverage. Its semantic contribution must not
be recast as more timers, faster work or better experimental outcomes. Both still
require a person to inspect every association and confirm timing.

## Architecture and safety boundary

- Original source/time functions remain in the unchanged V1 `app.py`. V2 code is in
  `attention.py`; the application entry point is `server:app`.
- Source candidates and meta-instruction filtering restrict the output schema.
  Standalone steps, clear simple waits and injected instructions are clamped to
  `none`. That does not solve temporal interpretation: model candidates still need
  to distinguish during/after/unclear and resolve earlier targets.
- Gemma returns one bounded enum per occurrence: `none`, `during:N`, `after:N` or
  `unclear:N`. `unclear:0` explicitly abstains on unresolved target identity.
- Source text, headings, time values and visible instruction excerpts are supplied
  by deterministic code. Gemma cannot author experimental instructions or time.
- A conservative independent context scan discovers monitoring or uncertain timing.
  Such notes block timer availability for review across the document. This can
  over-block an unaffected second wait; the miss remains in the denominator.
- Model during/unclear links can add review; they cannot remove a source restriction
  or grant timer eligibility. Exact, unrestricted waits no longer depend on a weak
  hands-on/hands-off label. A wrong model association can still increase review work.
- All browser timers require manual source confirmation. No experiment or equipment
  action is automated. A passive interval does not imply permission to leave the lab.

Gemma's source-association graph appears directly in the Attention Map/evidence
panel. It is not an ornamental explanation added to rule outputs. Its correctness
is scored separately from timing, and every proposed relation shows both original
source passages for challenge by the operator.

## Data provenance and independence limits

Eight development cases / 19 lines are separate from 30 held-out cases / 68 lines.
Cases cover nonadjacent context, first-versus-second waits, active monitoring,
after-interval work, uncertain timing, unresolved references, ordinary independent
actions, duplicate source text and embedded prompt instructions.

`0210301` freezes V2 labels before V2 model calls. Before *any held-out* model request,
two gold timer annotations were corrected: an unaffected wait in N07 and N08 is
eligible in gold even though the conservative implementation blocks both. The initial
annotations remain in Git; the correction and new SHA are recorded in `data-freeze.json`.
It was not based on held-out model outputs.

Candidate `b7c76c2` freezes the final engine, original source parser and evaluator.
The evaluator checks hashes before held-out requests, captures them at startup,
refuses to overwrite artifacts and makes no retry within a case. 4B was selected
before this held-out pass. The predeclared 1B comparison uses the same frozen task;
it is not a second chance to select a favorable holdout result.

Labels were authored by the coding assistant separately from the evaluated Gemma,
not by independent human researchers. They were visible to the implementer; cases
share linguistic patterns. V1's holdout is now exposed and historical, not reused
as unseen V2 data. These are prospective synthetic checks, not independent external
validation. The researcher trial remains uncompleted.

## Development attempts retained

The first V2 4B attempt accepted 7/8 plans, with exact-link F1 76.92%. It hallucinated
a relation for independent work and linked an embedded meta-instruction; the latter
was rejected. One deterministic context cue was missing, causing a development-only
unsupported timer candidate in the rules path. This evidence remains in `dev-4b`.

A development-only refinement clamps nonreferential/injected lines to `none`, adds
actual contextual checking language to the conservative review scan, and states
unclear/during/after distinctions through structured examples. Revised 4B development:
8/8 source-valid plans and 6/6 exact gold links, identical to rules on that small set.
These results informed the freeze; they are not held-out success claims.

During the revised development process, a source-display review rule was corrected
on disk while that process retained its imported version. Its per-case plans and
startup engine hash are the historical record. No such engine change occurred
during or after the held-out evaluation.

## Failure analysis — selected 4B candidate

All four wrong links are retained in `holdout-4b/error-analysis.json`:

- N17 and N18: “after” actions were incorrectly interpreted as `during`. These add
  unnecessary review and remove valid timers. They are not beneficial abstentions.
- N27 and N30: explicitly unresolved targets were attached to source 1 rather than
  `unclear:0`. Structural source-ID validity did not make the interpretation correct.

The baseline has higher link precision. Wrong suggested links can increase human
review work even when the safety layer remains conservative. An independent label
review and actual user task are needed to judge whether recall gains are worthwhile.
No post-result prompt/policy tuning was applied to this exposed holdout.

## Frozen 1B comparison and end-to-end case definition

The predeclared 1B pass completed 30/30 plans: 13 TP, 4 FP, 11 FN, precision 76.47%,
recall 54.17%, F1 63.41%. It offered 14/16 gold waits with zero observed unsupported
eligibility. Total 147.167 seconds, n=30; it is faster here but weaker on the selected
semantic task. No model selection was changed after seeing held-out scores.

Exact case-level link sets: 4B 26/30 versus rules 20/30. If successful workflow means
both the exact gold link set and exact gold timer set, 4B completed 24/30 versus
rules 18/30. These are scored synthetic workflows, not human task success or
laboratory use. `workflow-derived.json` defines and retains these calculations.
This provides a measured improvement in a meaningful interpretation dimension,
while the lower timer coverage and false-link burden remain material tradeoffs.

## Timing, hardware and commands

Actual loopback Ollama 0.40.10, CPU execution on the Intel i5 machine reporting 16 GB
installed memory. Available memory was not reliably measured. Gemma 3 4B and 1B use
Q4_K_M weights/digests recorded in `evaluation/environment/models.json`.
Temperature 0, seed 42, context 4096, generation budget 64 + 20 tokens per line,
120-second request timeout. Model weights were already cached; no weights are shipped.

4B held-out pass: 346.781 seconds total, per-request mean 11.553 s, median 10.565 s,
range 9.230–25.094 s, n=30. Runtime was warm after development; this is not a cold
start benchmark. CPU resource contention/browser checks may affect wall time.
No isolated inference speedup claim is made.

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
python eval/evaluate.py
python evaluation/v2/run.py --split development --model gemma3:4b --out evaluation/v2/my-dev
python evaluation/v2/run.py --split holdout --model gemma3:4b --out evaluation/v2/my-4b-replication
python evaluation/v2/run.py --split holdout --model gemma3:1b --out evaluation/v2/my-1b-replication
uvicorn server:app --host 127.0.0.1 --port 8771
```

Repeated exposed-set runs are replications, not unseen tests. Raw requests, response
strings, runtime timing/token counts, exact labels and complete plans are saved for
every case, including failures. No prepared output substitutes for failed inference.

## V1 regression and user-facing limits

`v1-source-regression.json` runs only the V2 deterministic source path on the exposed
old 42 cases: 10/13 eligible waits, 0 unsupported decisions. This confirms removal
of the original gating regression; it is not a new Gemma benchmark or a direct
comparison between the two different semantic tasks.

The no-install replay is prepared and labeled. Browser/contrast/performance checks
measure interface behavior, not user benefit. The actual v2 recording is a selected
local inference example, not representative accuracy. Completed human participants:
0. Public repository/demo publication remains unauthorized. Offline-disconnected
operation, scientific validity and general laboratory safety remain untested.
