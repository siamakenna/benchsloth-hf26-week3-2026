# V2 frozen temporal-link evaluation

| Approach | Link TP / FP / FN | Precision | Recall | F1 | Correct waits / 16 | Unsupported eligibility / 68 | Valid plans / 30 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Guarded rules | 14 / 1 / 10 | 93.3% | 58.3% | 71.8% | 14/16 | 0/68 | 30/30 |
| Gemma 4b hybrid | 20 / 4 / 4 | 83.3% | 83.3% | 83.3% | 11/16 | 0/68 | 30/30 |
| Gemma 1b hybrid | 13 / 4 / 11 | 76.5% | 54.2% | 63.4% | 14/16 | 0/68 | 30/30 |

30 synthetic cases, 68 source lines, 24 gold links, 16 gold fixed waits. Labels authored by coding assistant, not independently human adjudicated. Model suggestions cannot enable timers. See raw records for errors and latency.
