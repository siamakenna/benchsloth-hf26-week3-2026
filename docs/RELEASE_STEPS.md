# Next step: make this release available to judges

The files in this ZIP are a deliberately smaller version of the user-supplied v0.9 checkout. They do not include the original private laboratory protocols, owner-review pages, or full development history. This is **not** the complete owner archive.

The local application and benchmarked source passed 163 Python tests and 60 JavaScript assertions in the supplied source. The separate public site is a deterministic static demo; local Gemma runs are experimental and are **not** served by Render.

## GitHub

Unzip this file into an **empty folder outside** your original `benchsloth-week3` repository. Verify the files and try the demo locally:

```sh
python3 scripts/build_render.py
python3 -m http.server 8801 --directory render_public
```

Visit http://127.0.0.1:8801 . When you are satisfied, stop the local server, then run:

```sh
bash scripts/publish_mac.sh
```

The script checks hashes, asks for confirmation, and publishes a new `benchsloth-v09-public` branch to your existing GitHub repository. It will not overwrite `main` or change your DEV post. Authentication may require a GitHub credential prompt. If that fails, do not force-push or upload the entire private ZIP.

## Render

Once the public GitHub branch exists, create a Render **Static Site** connected to `siamakenna/benchsloth-hf26-week3-2026` at branch `benchsloth-v09-public`.

- Build command: `python3 scripts/build_render.py`
- Publish directory: `render_public`
- Automatic deploys: **Off** until you approve new revisions
- No backend commands, keys, environment secrets, or Ollama exposed

After Render reports `live`, open the exact public URL and test desktop/mobile, the revision flow, the countdown, the evidence page, the source download, and the 72-second walkthrough. Inspect the HTTPS status and response headers. **Don't publish the DEV article until you've approved those results and the final text.**

## Remaining limitations

The Render page does not perform Gemma inference. It does not know whether physical laboratory steps have happened, cannot validate scientific decisions, and does not prove that a timer means someone can leave an experiment unattended. Gemma completed 3/27 tested context-recovery handoffs versus 27/27 for the paired deterministic baseline. No independent user time-saving or scientific-accuracy data exists.
