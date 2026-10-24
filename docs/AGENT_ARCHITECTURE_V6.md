# BenchSloth v0.6 architecture

BenchSloth is a bounded attention agent, not an autonomous scientist. Its new read-only question layer selects original evidence; it cannot change a protocol, duration, timer permission or physical state.

## Two cooperating paths

The planner remains the frozen v0.5 engine (`agent_v5.py`, `association_v5.py`) with the existing session wrapper (`runtime_v5.py`). Eight typed tools preserve occurrence IDs, exact source text, offsets and hashes, parse literal durations, propose and check temporal links, detect restrictions, prepare human review and derive a return handoff. Headings scope candidate targets; duplicate wording never collapses IDs. Original v0.5 benchmarks are unchanged.

The v0.6 question path is `retrieve_source_evidence → gemma_select_evidence → verify_answer_evidence → route_read_only_answer`. Candidate options contain source IDs, original passages, section headings, possible relationships, ambiguity and no-answer. Gemma chooses one option through constrained JSON. It does not generate experimental procedures or answer prose. The interface quotes the original text and identifies interpretation separately.

Development exposed poor broad-schema answers. Two failed prototypes and all 18 development responses are preserved. The selected design uses copied evidence text and section context. Direct questions are routed to stronger deterministic retrieval; relationship questions use the model selection. Both raw proposal and final routed result remain inspectable. **The current implementation still makes the model request before routing direct questions**, so those questions incur inference latency and a model outage returns an error. No fallback silently substitutes a prepared answer.

## Verification is limited

Checks cover schema, occurrence identity, exact excerpts, duplicate IDs, valid earlier wait targets, session-fact availability and one explicit unresolved-language pattern. They do not prove entailment, resolve every negation or establish that a real quote answers the question. A wrong during/after interpretation can survive the identity check. The product calls this evidence selection for review, not validated scientific advice.

QA never mutates the plan or timer. A semantic relationship is a review proposal only; manual correction is explicit and recorded. Even a manual correction cannot relax original timer restrictions. In the current browser session, handoff facts are derived deterministically from source order, review status, confirmation decisions and timer outcome. Physical completion is never inferred.

## Live API and static replay

`server_v6.py` runs on loopback port 8772. In-memory sessions are capped at 32. One QA request runs at a time; another gets HTTP429. Inputs are capped at 48 lines /12000 source characters /500 question characters, with a separate 14000-character assembled QA prompt cap and a90-second request timeout. Oversized QA contexts fail visibly rather than claiming coverage. Model settings: Gemma3:4b Q4_K_M, temperature0, seed42,4096-token context,24-token output cap, no hidden retry. The prompt-character cap is conservative engineering, not a tokenizer-level coverage proof.

Expected session versions are checked before and after inference. Source changes or intervening decisions discard stale answers. Browser revisions and abort signals prevent a late result from replacing a newer view. Read-only questions, failure, stale-result and concurrency tests exercise these boundaries.

The public payload contains no model endpoint. Three authentic recorded planner scenarios and nine separately captured QA requests are replayed. Timers, source highlighting, corrections and current handoff run in JavaScript. Recorded session facts are never substituted for current browser facts. Every answer carries its actual request, raw response, routing decision, source hash and measured duration. The captioned video separately shows fresh local inference.

## Stack and provenance

Existing Python/FastAPI/Ollama avoids a deadline-driven migration. Original SVG artwork and code use MIT. Gemma weights have separate Google terms and are not distributed. No BioRender, Canva, Lovable or Base44 integration is required or claimed. No local server is exposed publicly; no paid infrastructure is needed.
