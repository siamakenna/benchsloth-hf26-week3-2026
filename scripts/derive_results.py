"""Produce presentation summaries from immutable raw evidence; never change labels."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'evaluation/holdout-4b/summary.json').read_text());rows=json.loads((R/'evaluation/holdout-4b/rows.json').read_text())
assert s['lines']==len(rows)
extra={}
for method in ['rules','guarded_rules','model','pipeline']:
    predicted=sum(r[method]=='hands_off' for r in rows)
    correct=sum(r[method]==r['gold_kind'] for r in rows)
    exact=sum(r[method+'_timer'] is not None and r[method+'_timer']==r['gold_timer'] for r in rows)
    extra[method]={'semantic_correct':correct,'semantic_denominator':len(rows),'passive_predictions':predicted,'correct_timer_decisions':exact,'gold_timer_lines':sum(r['gold_timer'] is not None for r in rows)}
for method in ['rules','guarded_rules','model','pipeline']:
    accepted=[r for r in rows if r[method] not in ('review','failed')]
    extra[method].update(incorrect_nonreview_labels=sum(r[method]!=r['gold_kind'] for r in accepted),nonreview_labels=len(accepted),review_classifications=len(rows)-len(accepted))
extra['semantic_vetoes']=[{'case':r['case'],'text':r['text'],'rules':r['rules'],'model':r['model'],'gold':r['gold_kind']} for r in rows if r['rules']=='hands_off' and r['gold_kind']!='hands_off' and r['model']!='hands_off']
extra['paraphrases_model_found_rules_missed']=[{'case':r['case'],'text':r['text'],'pipeline':r['pipeline']} for r in rows if r['gold_kind']=='hands_off' and r['model']=='hands_off' and r['rules']!='hands_off']
(R/'evaluation/holdout-4b/derived.json').write_text(json.dumps(extra,indent=2)+'\n')
headers='| Approach | Passive precision | Recall | F1 | Incorrect or abstained labels / 45 | Unsupported timer eligibility | Offered timers |\n|---|---:|---:|---:|---:|---:|---:|\n'
labels={'rules':'Starter lexical rules','guarded_rules':'Rules + final validator','model':'Gemma 4B classifications','pipeline':'Gemma + final validator'}
for m in labels:
 d=s['metrics'][m];headers+=f"| {labels[m]} | {d['precision']:.1%} | {d['recall']:.1%} | {d['f1']:.1%} | {d['incorrect_labels']}/45 | {d['unsupported_timer_eligibility']}/45 | {d['timer_decisions']} |\n"
(R/'evaluation/RESULTS.md').write_text('# Frozen held-out results\n\n'+headers+'\n42/42 source-valid plans; 0 failed runs, missing/extra steps or duplicate IDs.\n302.581 seconds total; synthetic assistant labels, no independent human adjudication.\nModel-only timers use the deterministic duration parser but omit the passive-source validator; these are counterfactual eligibility decisions, not browser timer starts.\n')
for name,start,end in [('README.md','<!-- RESULTS -->','<!-- /RESULTS -->'),('docs/DEV_POST_DRAFT.md','<!-- EVALUATION_TABLE -->','<!-- /EVALUATION_TABLE -->')]:
 p=R/name;text=p.read_text();a=text.index(start)+len(start);b=text.index(end,a)
 detail='\n\n'+headers+'\n42 cases / 45 lines; 42/42 source-valid plans; 0 failed runs, missing/extra steps or duplicate IDs. Total model workflow time: **302.581 seconds**. These are synthetic, assistant-authored labels.\n\n**No broad model superiority demonstrated.** Gemma improved raw passive precision but lost recall. The final pipeline offered only 3 of 13 gold fixed waits, compared with 10 for guarded rules; both had zero observed unsupported eligibility decisions. Actual human usefulness remains unmeasured.\n\n'
 p.write_text(text[:a]+detail+text[b:])
print(json.dumps(extra,indent=2))
