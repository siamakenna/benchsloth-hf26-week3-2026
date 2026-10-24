# Semantic error analysis — v0.6

All24 original final outcomes are retained. No error is repaired in the frozen records. References are synthetic and independently unadjudicated.

| Case | Tags | Rules exact | Raw exact | Combined exact | Combined reference disagreement |
|---|---|---:|---:|---:|---|
| Q01 | clear | no | yes | no | IDs [1] vs [2] |
| Q02 | monitoring | no | yes | no | IDs [1] vs [2] |
| Q03 | cross-section, association | no | no | no | IDs [4, 5] vs [2, 5]; relationship differs |
| Q04 | repeated, association, review | yes | yes | yes | exact evidence; inspect relationship separately |
| Q05 | no-answer | yes | no | yes | exact evidence; inspect relationship separately |
| Q06 | uncertain, timer | no | yes | no | IDs [1] vs [2] |
| Q07 | monitoring, association | yes | yes | yes | relationship differs |
| Q08 | association | no | yes | yes | exact evidence; inspect relationship separately |
| Q09 | contradiction, review | yes | yes | yes | exact evidence; inspect relationship separately |
| Q10 | adversarial, no-answer | yes | no | yes | exact evidence; inspect relationship separately |
| Q11 | similar-terms | yes | yes | yes | exact evidence; inspect relationship separately |
| Q12 | association, semantic-comparison | no | no | no | IDs [1, 3] vs [2, 3]; relationship differs |
| Q13 | cross-section, association | no | no | no | IDs [4, 5] vs [2, 5]; relationship differs |
| Q14 | underspecified, association, review | yes | yes | yes | exact evidence; inspect relationship separately |
| Q15 | no-answer | yes | no | yes | exact evidence; inspect relationship separately |
| Q16 | monitoring, paraphrase | no | yes | no | IDs [1] vs [2] |
| Q17 | long, repeated, cross-section, association | no | yes | yes | relationship differs |
| Q18 | long, monitoring | yes | no | yes | exact evidence; inspect relationship separately |
| Q19 | long, repeated, association, review | yes | no | no | status not_available vs ambiguous; IDs [] vs [4, 11, 21]; relationship differs |
| Q20 | long, cross-section, association | no | no | no | IDs [16, 25] vs [5, 25]; relationship differs |
| Q21 | long, no-answer | yes | no | yes | exact evidence; inspect relationship separately |
| Q22 | long, contradiction, review | yes | no | yes | exact evidence; inspect relationship separately |
| Q23 | monitoring, association, review | yes | yes | yes | exact evidence; inspect relationship separately |
| Q24 | adversarial, timer | yes | yes | yes | exact evidence; inspect relationship separately |

## Main failure families

Named short cross-section references can choose the nearest wrong wait; longer context is not automatically better. Q17 finds the right passages but not the correct relation. Q19 overcommits on an explicitly unspecified21-line source; identity checks reject that proposal, but the resulting no-answer differs from the expected ambiguity response. Raw Gemma answers missing-parameter questions using unrelated real passages; direct deterministic routing fixes the four tested no-answer questions but is not general missing-information detection. Q07 confuses during/after despite correct citations. Q20 selects the wrong section on25 lines.

The strong retrieval shortlist contains all gold passages for16/16 answerable cases. The model has not shown an advantage over a person inspecting that shortlist. Do not compare free-text fluency against rules that cannot write prose.

Engineering reviewer probes outside the frozen set: a during proposal for an explicit after note can pass identity checks; an absent pressure question can retrieve an irrelevant wait. These are disclosed qualitative counterexamples, not added to the24-case denominator. Broader factual QA and semantic verification remain experimental.

Shipped presentation narrows authority: every Gemma relationship is a review-required proposal. No automatic association or timer permission is granted from QA, and the narrowing is not retroactively scored as model accuracy.
