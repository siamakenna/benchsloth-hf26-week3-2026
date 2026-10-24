---
title: "My AI Lost to Simple Rules. So I Built BenchSloth Around Evidence."
published: false
tags: devchallenge, hf26challenge
cover_image: https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/dev-cover.png
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge: Week 3](https://dev.to/challenges/hacktoberfest-week3-2026-10-19): Slow and Steady.*

The most useful result in my AI benchmark was the one telling me to give the model less authority.

My first lab-note assistant recognized a wait—and then made it harder to use. Its model-driven policy offered just **3 of 13 eligible waits**. Guarded rules offered **10**. The clever part was getting in the way of the useful part.

I stopped asking AI to do what simple rules did better—and built an agent that manages attention around evidence.

![BenchSloth: original source, an Attention Map and evidence questions](https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/desktop-hero.png)

**[Explore BenchSloth in your browser →](https://siamakenna.github.io/benchsloth-hf26-week3-2026/)** No account, model download or installation required. The public experience replays authentic model outputs; its timers and decisions run in your browser.

## What I Built

BenchSloth gives your attention a plan, not just your experiment.

A wait is rarely the only thing a researcher needs to remember. There may be a note that belongs after it, a monitoring requirement that applies during it, an unclear reference to “that interval,” or an action waiting on the other side. A checklist keeps the lines. BenchSloth keeps their evidence and the unresolved questions together.

The workspace has three parts: **Source**, preserving the original words and occurrence IDs; **Attention**, showing fixed intervals and review needs in source order; and **Intelligence**, where you can inspect evidence selected for a question.

You can ask which earlier wait a note describes, open the quoted passages, inspect the actual model request, record a correction, confirm an interval and return to the next original instruction. The agent records the path between those actions. It never claims to have watched or completed the experiment.

## Demo

Start with **A, the clear wait**. Select its relationship question and open both source passages. The answer carries the actual recorded Gemma response, its measured duration and its verification trace.

Switch to **B, the uncertain note**. Two identical waits remain distinct occurrences. The note says “one of these waits” without identifying which. The recorded answer exposes that ambiguity; the plan offers no timer. You can record your own interpretation, but doing so cannot remove the source restrictions.

Then explore **C, the longer workflow**: thirteen lines across two sections. Follow a note back to its evidence, inspect the planner's eight real tools, and compare the current browser handoff with the separately labeled historical recording.

![Ask BenchSloth with original excerpts, an experimental relationship proposal and inspectable raw output](https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/ask-benchsloth.png)

For the signature moment, return to A and confirm its **ten-second demonstration**. Breathing Room keeps the clock and supporting source in view. When it ends, Return Handoff shows the next original instruction, recorded confirmations and open review questions. The source's seven-minute interval has not elapsed; only the explicitly shortened interface demonstration has.

![A real browser countdown in Breathing Room](https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/breathing-room.png)

[Watch the captioned demonstration with fresh local Gemma inference](https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/demo-captioned.webm). Recorded examples, live inference and deterministic browser functionality are labeled separately. The public site does not expose my development computer as a model server.

## Code

**[Source, frozen evaluations and reproduction instructions](https://github.com/siamakenna/benchsloth-hf26-week3-2026)**

Original code and SVG artwork use MIT. Gemma is an open-weight model with separate Google terms; model weights and runtime binaries are not redistributed. The public snapshot preserves benchmark evidence and documented development provenance. The full local development history remains intact.

## How I Built It

### Give the clock back to code

An exact source interval is a parsing and policy problem. BenchSloth keeps that work deterministic. If the source lacks an exact duration, contains a restriction or leaves a relevant target unresolved, an appealing model sentence cannot grant a timer.

The first improvement came from preserving source structure: stable occurrence IDs, headings, explicit references and ordinals. That matters when the same words appear twice. “After the second wait” must not drift to the nearest matching text.

The v0.5 planner recovered **22/22 reference links**, with **one extra unresolved association**, across twenty synthetic cases. It recovered **16/18 eligible waits**, with no observed unsupported timer offers. Strong scoped rules matched its accuracy. A separate eighteen-, twenty-one- and twenty-five-line supplement recovered **6/6 links and 3/3 waits** for both approaches. Those results remain separate; the original twenty cases reached fifteen actual lines.

A perfect-looking short score had already failed me: earlier six-line recordings missed real associations. Those failures are still in the repository. Source structure was useful. A model accuracy advantage was not established.

### Give Gemma a smaller, inspectable job

The new question layer runs local **Gemma 3 4B**, Q4_K_M, through Ollama on CPU. It selects among evidence candidates containing original passages, section context and possible relationships, including ambiguity and no-answer options. It does not generate experimental instructions or durations.

The path is explicit: prepare source → retrieve candidates → ask Gemma → check evidence identity → prepare review → maintain the attention plan → record an interval → hand attention back.

![The two paths of authority: semantic evidence proposals and deterministic source/timer state](https://siamakenna.github.io/benchsloth-hf26-week3-2026/assets/v6/architecture.png)

A citation check establishes that the quoted text exists. It does **not** establish that the text answers the question. That distinction became the central design constraint.

I tried three designs on six development questions, preserving all eighteen responses. The final engine was frozen before a new twenty-four-question run. The test includes missing facts, contradictions, repeated wording, named references across sections, monitoring language, embedded instruction attacks and inputs reaching twenty-five lines.

### Keep the result that spoils the headline

| Final synthetic QA comparison | Exact evidence/status | Exact QA workflow | Unsupported evidence selections |
|---|---:|---:|---:|
| Strong rules + retrieval | 14/24 | 14/24 | 7 |
| Raw Gemma selection | 13/24 | 11/24 | 11 |
| Combined candidate agent | 15/24 | 13/24 | 8 |

The combined selector found one more exact evidence set, but completed fewer exact workflows and produced more unsupported answers. “Unsupported” includes real passages that do not support the requested answer; it does not mean invented quotations or timer permissions. A complete QA workflow also requires the correct relationship, not just the right passages. Wrong relationships with correct evidence are penalized there, separately from the unsupported-evidence count.

The rules shortlist already contained every required passage in its top three for **16/16 answerable questions**. The model has not shown that it beats a person inspecting that shortlist. Mean local model request time was **25.40 seconds**, versus roughly **0.00067 seconds** for retrieval. This is request latency, not human time saved. Direct retrieval answers still wait for the Gemma call before routing; that unnecessary dependency remains a limitation.

One revealing case asks about a copper-tray interval across sections. Gemma finds the correct passages, but labels their relationship “unclear” where the reference says “after.” The evidence score improves; the complete semantic answer does not. On other cases it selects the wrong section or fails to abstain. Identity checks cannot repair understanding.

So direct questions use deterministic retrieval, while every model relationship is presented as an **experimental proposal requiring review**. QA cannot amend the Attention Map or relax a timer restriction. That narrower presentation is not retroactively counted as improved accuracy.

**[Does BenchSloth Actually Work? Inspect every case →](https://siamakenna.github.io/benchsloth-hf26-week3-2026/evidence/index.html)** Compare approaches, filter failures and long inputs, and read the original source, reference and raw response without downloading anything. The small, related synthetic set and assistant-authored, implementer-visible labels limit the conclusions. Independent human validation is still **n=0**; the no-install researcher trial is ready, with no invented outcomes or time-saving claims.

## Why Does Open Innovation Matter?

Open weights let me run the model locally and preserve the exact request. Open code lets someone inspect the source restrictions, reject my reference labels, replace Gemma or show that retrieval is enough for their notes. The useful freedom is not only adding intelligence. It is deciding where intelligence has not earned authority.

The design follows the same idea. Original botanical SVGs, notebook annotations and a quiet countdown support the work. The workbench shows structured inputs, outputs, rejected proposals and decisions—not private chain-of-thought or invented tool activity.

The intended Slow and Steady payoff is simple: fewer places to reconstruct context when returning to a task. Whether researchers actually do that faster and with fewer mistakes still needs a real trial. Until then, BenchSloth offers an inspectable place to keep the source, the uncertainty and the next step together.

## Prize Categories

**Best Use of Gemma.** Local Gemma 3 4B performs genuine source-pair classification and experimental evidence/relationship selection inside the bounded agent. Its contribution, latency and failures are directly inspectable. No comparative semantic advantage or additional partner integration is claimed.
