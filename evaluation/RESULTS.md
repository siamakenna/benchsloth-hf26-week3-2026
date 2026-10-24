# Frozen held-out results

| Approach | Passive precision | Recall | F1 | Incorrect or abstained labels / 45 | Unsupported timer eligibility | Offered timers |
|---|---:|---:|---:|---:|---:|---:|
| Starter lexical rules | 69.7% | 88.5% | 78.0% | 14/45 | 9/45 | 19 |
| Rules + final validator | 100.0% | 46.2% | 63.2% | 25/45 | 0/45 | 10 |
| Gemma 4B classifications | 100.0% | 61.5% | 76.2% | 12/45 | 0/45 | 6 |
| Gemma + final validator | 100.0% | 15.4% | 26.7% | 24/45 | 0/45 | 3 |

42/42 source-valid plans; 0 failed runs, missing/extra steps or duplicate IDs.
302.581 seconds total; synthetic assistant labels, no independent human adjudication.
Model-only timers use the deterministic duration parser but omit the passive-source validator; these are counterfactual eligibility decisions, not browser timer starts.
