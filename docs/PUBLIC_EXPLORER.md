# Public product and evidence explorer

Entry: `demo/index.html`. Evidence: `demo/evidence/index.html`. Both work from local files and a GitHub Pages project subpath, without installation, authentication, model weights or required downloads.

The attention desk has Source, Attention and Intelligence regions. Choose A/B/C, inspect original occurrences and associations, select a recorded question, open cited passages and raw requests, make a human correction, confirm a ten-second demonstration, enter Breathing Room, then return to current browser facts. The initial planner outputs are recorded. QA records preserve actual inference and any deterministic routing. Static visitors choose stored questions; arbitrary fresh questions require the local application. The UI does not claim a prepared response is fresh inference.

The evidence explorer, “Does BenchSloth Actually Work?”, displays all24 final questions. Compare strong retrieval/rules, an explicitly adapted v0.5 source view, raw Gemma and the final routed answer. Filter matches, mismatches, review cases, long sources, monitoring/timer-related questions, associations and no-answer cases. Inspect full source, reference, selected IDs, exact quotes, scoring, request/response and deterministic shortlist without downloading JSON. Historical v0.5 planner metrics remain separately labeled.

The explorer also explains configuration, reproduction, architecture, scope of source checks, synthetic labels, human n=0, limitations, license and asset provenance. No network request to a private inference API is made by the static payload. The code link points to the intended reviewed repository; external public routes cannot be verified until publication is explicitly authorized.

Public mode language:

- **Live Gemma inference:** fresh local requests in the loopback app and authentic video.
- **Recorded Gemma output:** preserved outputs replayed with their measured request and routing trace.
- **Deterministic browser functionality:** source navigation, manual decisions, timers and current-session handoff.

No secure hosted inference service was provisioned. Static replay plus the authentic video is the release path; the development Mac is not a public server.
