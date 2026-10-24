"""Prospective source-link task; no retries, all failures retained."""
import argparse,hashlib,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from app import MODEL
from attention import infer_semantics,build_plan,baseline_links,validate_links

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(cases,records,method):
    gold=set();pred=set();timers=good=unsafe=missed=valid=links_valid=review=steps=0
    for c,r in zip(cases,records):
        for note,val in c['links'].items():gold.add((c['id'],note,val))
        raw=r.get(method+'_labels',{});plan=r.get(method+'_plan')
        for note,val in raw.items():
            if val!='none':pred.add((c['id'],note,val))
        if plan:
            valid+=1;links_valid+=len(plan['links']);review+=plan['review_needed'];steps+=len(plan['steps'])
            for s in plan['steps']:
                t=s['rest_minutes'];g=c['timers'].get(str(s['id']))
                timers+=t is not None;good+=t is not None and t==g;unsafe+=t is not None and t!=g
            offered={str(s['id']) for s in plan['steps'] if s['rest_minutes'] is not None}
            missed+=len(set(c['timers'])-offered)
        else:missed+=len(c['timers'])
    tp=len(pred&gold);fp=len(pred-gold);fn=len(gold-pred)
    return dict(cases=len(cases),source_lines=sum(len(c['text'].splitlines()) for c in cases),valid_plans=valid,failed_plans=len(cases)-valid,
        link_tp=tp,link_fp=fp,link_fn=fn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
        timer_eligible=timers,correct_timers=good,unsupported_timer_eligibility=unsafe,missed_gold_waits=missed,gold_waits=sum(len(c['timers']) for c in cases),review_lines=review,
        structurally_valid_links=links_valid,accepted_source_lines=steps)

def main():
    a=argparse.ArgumentParser();a.add_argument('--split',choices=['development','holdout'],default='development');a.add_argument('--out',required=True);a.add_argument('--model',default=MODEL);x=a.parse_args()
    out=R/x.out
    if out.exists() and any(out.glob('*.json')):raise SystemExit('Refusing overwrite')
    out.mkdir(parents=True,exist_ok=True);data=R/f'evaluation/v2/{x.split}.json';freeze=json.loads((R/'evaluation/v2/data-freeze.json').read_text());assert sha(data)==freeze['files'][data.name]
    engine={p:sha(R/p) for p in ['attention.py','app.py','evaluation/v2/run.py']}
    if x.split=='holdout':
        f=json.loads((R/'evaluation/v2/candidate-freeze.json').read_text());assert engine==f['files']
    cases=json.loads(data.read_text());records=[];start=time.perf_counter()
    for c in cases:
        raw=baseline_links(c['text']);r={'id':c['id'],'input':c['text'],'rules_labels':raw,'rules_plan':build_plan(c['text'],raw,'rules')}
        try:
            raw,ev=infer_semantics(c['text'],x.model);r.update(ev);r['model_labels']=raw;r['model_plan']=build_plan(c['text'],raw,model=x.model)
        except Exception as e:r.update(error=str(e),**getattr(e,'evidence',{}))
        records.append(r);(out/(c['id']+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(c['id'],r.get('error','valid'),flush=True)
    summary=dict(task='Exact temporal source-note associations, not v1 line classification',model=x.model,split=x.split,wall_seconds=time.perf_counter()-start,engine=engine,data_sha256=sha(data),metrics={m:metrics(cases,records,m) for m in ['rules','model']},annotation='Assistant-authored labels; not independent human validation. Model only adds review; no model-enabled timers.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
