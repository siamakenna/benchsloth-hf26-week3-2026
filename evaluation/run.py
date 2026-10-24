"""One pass, no retries. All failures remain in case/line denominators."""
import argparse, datetime, hashlib, json, platform, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import MODEL, OLLAMA_HOST, infer_with_evidence, validate_model_output, rule_kind, fixed_duration

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ENGINE_SHA = sha(ROOT/"app.py")
def metrics(rows, method):
    pred=[r[method] for r in rows]; gold=[r['gold_kind'] for r in rows]
    tp=sum(p=='hands_off' and g=='hands_off' for p,g in zip(pred,gold))
    fp=sum(p=='hands_off' and g!='hands_off' for p,g in zip(pred,gold))
    fn=sum(p!='hands_off' and g=='hands_off' for p,g in zip(pred,gold))
    timers=[r.get(method+'_timer') for r in rows]
    return dict(lines=len(rows),true_positive=tp,false_positive=fp,false_negative=fn,
        precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None,
        f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
        incorrect_labels=sum(p!=g for p,g in zip(pred,gold)),
        unsafe_timer_eligibility=sum(t is not None and r['gold_timer'] is None for t,r in zip(timers,rows)),
        unsupported_timer_eligibility=sum(t is not None and t!=r['gold_timer'] for t,r in zip(timers,rows)),
        timer_decisions=sum(t is not None for t in timers),
        review_or_abstention=sum(r.get(method+'_review',p in ('review','failed')) for r,p in zip(rows,pred)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--split',choices=['development','holdout'],default='development');ap.add_argument('--out',required=True);ap.add_argument('--rules-only',action='store_true');args=ap.parse_args()
    out=ROOT/args.out
    if out.exists() and any(out.glob('*.json')): raise SystemExit('Refusing to overwrite an evaluation run')
    out.mkdir(parents=True,exist_ok=True)
    freeze=json.loads((ROOT/'evaluation/data-freeze.json').read_text())
    path=ROOT/f'evaluation/{args.split}.json'
    assert sha(path)==freeze['files'][path.name], 'Data changed since freeze'
    candidate=ROOT/'evaluation/candidate-freeze.json'
    if args.split=='holdout':
        assert candidate.exists(), 'Freeze candidate first'
        for name,digest in json.loads(candidate.read_text())['files'].items(): assert sha(ROOT/name)==digest,name
    cases=json.loads(path.read_text());rows=[];case_reports=[];started=time.perf_counter()
    for case in cases:
        lines=[l.strip() for l in case['text'].splitlines() if l.strip()]
        kinds=case.get('kinds',[case.get('kind')]);timers=case.get('timers',[case.get('timer_minutes')])
        record={'id':case['id'],'input':case['text'],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        raw=None;plan=None
        if not args.rules_only:
            try:
                raw,evidence=infer_with_evidence(case['text']);record.update(evidence);record['parsed']=raw
                plan=validate_model_output(case['text'],raw);record['plan']=plan
            except Exception as exc:
                record['error']=str(exc)
                record.update(getattr(exc,'evidence',{}))
        else: record['skipped']='rules-only run; no model request'
        candidates=raw.get('steps',[]) if isinstance(raw,dict) else []
        if isinstance(raw,dict) and 'steps' not in raw:
            candidates=[{'id':int(k) if k.isdigit() else k,'kind':v} for k,v in raw.items()]
        record['accepted']=plan is not None
        record['missing_steps']=max(0,len(lines)-len(candidates));record['extra_steps']=max(0,len(candidates)-len(lines))
        record['duplicate_ids']=len(candidates)-len({str(x.get('id')) for x in candidates if isinstance(x,dict)})
        for i,(line,gold,timer) in enumerate(zip(lines,kinds,timers)):
            # A model-only prediction has a meaningful identity only at the matching ID.
            c=candidates[i] if i<len(candidates) and isinstance(candidates[i],dict) else {}
            mk=c.get('kind','failed') if c.get('id')==i+1 else 'failed'
            rk=rule_kind(line);rt=fixed_duration(line)[0] if rk=='hands_off' else None
            step=plan['steps'][i] if plan else {}
            guarded=validate_model_output(line,{'1':rk})['steps'][0]
            rows.append(dict(case=case['id'],id=i+1,text=line,gold_kind=gold,gold_timer=timer,rules=rk,rules_timer=rt,
                guarded_rules=guarded['kind'],guarded_rules_timer=guarded['rest_minutes'],guarded_rules_review=guarded['review_needed'],model=mk,model_timer=fixed_duration(line)[0] if mk=='hands_off' else None,
                pipeline=step.get('kind','failed'),pipeline_timer=step.get('rest_minutes'),pipeline_review=step.get('review_needed',True)))
        (out/(case['id']+'.json')).write_text(json.dumps(record,indent=2)+'\n');case_reports.append(record)
        print(case['id'], 'accepted' if plan else record.get('error','rules-only'),flush=True)
    summary={'split':args.split,'model':MODEL,'rules_only':args.rules_only,'cases':len(cases),'lines':len(rows),'accepted_plans':sum(r['accepted'] for r in case_reports),'failed_runs':sum('error' in r for r in case_reports),'wall_seconds':time.perf_counter()-started,'engine_sha256':ENGINE_SHA,'data_sha256':sha(path),'metrics':{m:metrics(rows,m) for m in ['rules','guarded_rules','model','pipeline']},'missing_steps':sum(r['missing_steps'] for r in case_reports),'extra_steps':sum(r['extra_steps'] for r in case_reports),'duplicate_ids':sum(r['duplicate_ids'] for r in case_reports),'annotation':'Assistant-authored synthetic labels, not independent human or real-world validation.'}
    (out/'rows.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
