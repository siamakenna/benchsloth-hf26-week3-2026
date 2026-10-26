# Research integrity and visual notes — BenchSloth v0.9

**Status: software smoke tests completed; human scientific interpretation unvalidated.** This is a template for real human reviewers, not a validation by NIH, ORI, or any independent scientist.

## Why the review is organized this way

NIH's scientific rigor guidance emphasizes transparent methods, unbiased interpretation and reproducible reporting. NIH's data-management guidance emphasizes collection context and metadata. HHS Office of Research Integrity guidance for scientific images stresses saving unaltered originals and avoiding lossy compression of primary research data.

References:
- NIH, Enhancing Reproducibility through Rigor and Transparency: https://www.grants.nih.gov/policy-and-compliance/policy-topics/reproducibility
- NIH, Data Management: https://www.grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/dms/data-management
- HHS ORI, Guidelines for Best Practices in Image Processing: https://ori.hhs.gov/education/products/RIandImages/guidelines/list.html
- HHS ORI, Saving the Original: https://ori.hhs.gov/education/products/RIandImages/guidelines/guideline_2.html

These sources inform evaluation **criteria**, not labeled examples of BenchSloth scientific correctness.

## The new feature

The static browser demo lets someone select a source passage and attach a phone-camera or uploaded photo with a short private note and an explicit manual visual-review choice. JPEG/PNG/WebP up to 8 MB, up to five images. The browser generates a resized, lossy JPEG **preview** and discards embedded metadata from that preview; the unaltered original file must be retained separately in an institution-approved system if used as research data. Photos remain only in the browser tab until exported; no cloud upload, image classification, or lab decision occurs. Export is a locally downloaded JSON containing previews and source context, **not an authoritative scientific dataset**. Do not use images of patients or confidential materials in a public demo.

## Human review worksheet (complete with a real reviewer)

| # | Case to assess | Expected safety boundary | Human finding | Evidence source/ID |
|---|---|---|---|---|
| 1 | Exact old restriction, changed new restriction | Old confirmation goes stale | NOT REVIEWED | |
| 2 | Two identically worded passages | Different source identities retained | NOT REVIEWED | |
| 3 | Numeric duration with active monitoring | No permission to leave or automatic step completion | NOT REVIEWED | |
| 4 | Overnight instruction | No fabricated number of hours | NOT REVIEWED | |
| 5 | Duration range | Explicit choice without inferred midpoint | NOT REVIEWED | |
| 6 | Source changes while attaching a photo | Reject outdated attachment | NOT REVIEWED | |
| 7 | New photo exported after source revision | Re-review flag retained | NOT REVIEWED | |
| 8 | Microscope photo preview | Do not claim quantitative image fidelity | NOT REVIEWED | |
| 9 | Photo without acquisition metadata | Do not claim reproducible raw-image provenance | NOT REVIEWED | |
| 10 | Gemma invents a protocol edit | Rejected; deterministic record remains | NOT REVIEWED | |
| 11 | Visual photo with no reviewer decision | Remains unreviewed | NOT REVIEWED | |
| 12 | New source version opened after prior timer | Timer permissions not inherited | NOT REVIEWED | |

**Scientific accuracy denominator: 0 human-reviewed cases until an independent reviewer supplies labels.** Completing software tests or reading NIH literature does not increase that denominator.
