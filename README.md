# BenchSloth v0.9.1 — Pick up where you left off

Instructions change. Your notes and previous decisions shouldn't disappear when they do.

BenchSloth is a small, local-first research desk for finding a source passage, keeping a manually started countdown alongside its restrictions, comparing old and new instructions, and figuring out what needs another look. **It does not run experiments, know physical progress, or authorize unattended work.**

## Try the interactive demo

**[Open BenchSloth on Render](https://benchsloth-hf26-week3-2026.onrender.com)**

The Render site publishes only the self-contained browser demo, synthetic media, a concise evidence page, and a source/evidence download. Try the sample instructions, pin a passage, compare versions, mark a prior decision as needing review, and use **Pick up where I left off**. The standalone browser demo works without a model and prevents network model calls.

Run the same demo locally:

```sh
python3 -m http.server 8000 --directory web
```

Open http://127.0.0.1:8000.

Watch the [72-second walkthrough](web/media/walkthrough.mp4), or see the [desktop](web/media/fresh-desktop.jpg) and [mobile](web/media/fresh-390.jpg) screenshots.

## Photos as private visual notes

The demo now allows camera/file image attachment to a selected source passage, a short observation, manual visual-review status and a private JSON export. Photo previews are resized and re-encoded, **not suitable as unmodified primary scientific image data**; keep instrument originals and metadata separately. No cloud upload, computer vision model, or scientific verification happens. The human-review checklist is in `docs/SCIENTIFIC_REVIEW_AND_IMAGE_NOTES.md`.

## Where Gemma fits (and doesn't)

BenchSloth also contains an **experimental local Gemma 3 4B** Context Recovery option, implemented in `source/recovery_v9.py` and `source/server_v9.py`. The model received versioned evidence and state; invalid outputs were rejected rather than promoted to instructions. **This Render site does not run Gemma.** The included Python sources are selected inspectable implementation files, not a deployed/public backend or a guarantee that the model can run from this ZIP alone.

In a frozen synthetic comparison, Gemma produced 3 complete handoffs among 27 attempts (26 returned, one timed out; one further planned case not attempted), versus 27/27 paired deterministic handoffs. Mean local returned request time was ~58 seconds on the test machine. One invented change was detected and rejected. Human scientific correctness and productivity savings remain unmeasured. See `evidence/gemma` for the evaluation contract, aggregate report and raw audit.

## Technical notes

The uploaded owner-only repository passed 163 Python unit tests and 60 JavaScript assertions in an independent recheck of the supplied ZIP. This smaller public ZIP also receives its own manifest, privacy screening, HTTP and build checks. Some source modules refer to assets kept in the full original development project; do not expose `server_v9.py` publicly without a separate security review, authentication and privacy design.

The published static build is deterministic and self-contained. A source quote or model citation does not prove scientific interpretation. Old version approvals never transfer to NEW, and a countdown expiring never claims a step completed.

## Structure

- `web/`: the explicitly permitted static demo and synthetic video/screenshots
- `source/`: selected inspectable Python, JavaScript and synthetic tests
- `evidence/gemma/`: bounded model comparison artifacts (no private laboratory originals)
- `scripts/build_render.py`: strict SHA-256-checked static-site build
- `docs/SCIENTIFIC_REVIEW_AND_IMAGE_NOTES.md`: NIH-informed review worksheet; no human labels are claimed.
- The DEV article is maintained separately on DEV Community.

Project code and original design are released under MIT; Gemma model weights follow their own license. No private lab SOPs, unpublished notebooks, or owner-review packages are included. This public release was prepared from the user-supplied v0.9 archive with local checkpoint reported as `7df5a53`.


## Release-specific checks

The static app provides an **optional photo-notes panel**. Photos are held locally in the browser until explicit JSON export and are linked to one source passage. Previews are lossy and do not replace unmodified scientific originals. Twelve research-integrity review scenarios are supplied as a blank worksheet; **0 human reviewers have scored them**. No scientific, clinical or microscope image classification occurs.
