from pathlib import Path
import json,statistics
R=Path(__file__).resolve().parents[1]
base=R/'evaluation/v2'
rows=[]
for name in ['4b','1b']:
 p=base/f'holdout-{name}/summary.json'
 if not p.exists():continue
 s=json.loads(p.read_text());model=s['metrics']['model'];rules=s['metrics']['rules']
 if not rows:rows.append(('Guarded rules',rules,None))
 rows.append(('Gemma '+name+' hybrid',model,s['wall_seconds']))
header='| Approach | Link TP / FP / FN | Precision | Recall | F1 | Correct waits / 16 | Unsupported eligibility / 68 | Valid plans / 30 |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
for name,m,t in rows:header+=f"| {name} | {m['link_tp']} / {m['link_fp']} / {m['link_fn']} | {m['precision']:.1%} | {m['recall']:.1%} | {m['f1']:.1%} | {m['correct_timers']}/16 | {m['unsupported_timer_eligibility']}/68 | {m['valid_plans']}/30 |\n"
(base/'RESULTS.md').write_text('# V2 frozen temporal-link evaluation\n\n'+header+'\n30 synthetic cases, 68 source lines, 24 gold links, 16 gold fixed waits. Labels authored by coding assistant, not independently human adjudicated. Model suggestions cannot enable timers. See raw records for errors and latency.\n')
p=R/'docs/DEV_POST_DRAFT.md';s=p.read_text();a=s.index('<!-- V2_RESULTS -->')+len('<!-- V2_RESULTS -->');b=s.index('<!-- /V2_RESULTS -->',a);s=s[:a]+'\n\n'+header+'\nGemma 4B found six more exact temporal links, with three more false links. Its extra review reduced eligible-wait coverage. This establishes a narrower measured semantic contribution on this synthetic sample, not overall timer superiority or human time savings.\n\n'+s[b:];p.write_text(s)
print(header)
