"""Frozen length-stratified comparison; one pass, no overwrites or retries."""
import argparse,json,hashlib,time,sys,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from agent_v5 import AttentionAgent,Phase
from attention_agent import AttentionAgent as Previous
from association_v5 import candidate_rows,AFTER
from attention_agent import UNCLEAR_CUE,DURING_CUE,ATTENTION_CUE

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rules(source):
 labels={str(i+1):'none' for i in range(len(source.splitlines()))}
 for r in candidate_rows(source):
  note=source.splitlines()[r['note_id']-1];target=r['target_id']
  relation='unclear' if target is None or UNCLEAR_CUE.search(note) else 'after' if AFTER.search(note) else 'during' if DURING_CUE.search(note) and ATTENTION_CUE.search(note) else 'none'
  if relation!='none':labels[str(r['note_id'])]=f'{relation}:{target or 0}'
 return labels,{'coverage':[],'model_calls':0,'notice':'Strong deterministic candidate/section baseline; same verifier and source restriction policy.'}
def metrics(cases,records):
 gold=set();pred=set();correct_waits=unsafe=missed=complete=valid=abstentions=failures=0;latencies=[]
 for c,r in zip(cases,records):
  expected={(c['id'],k,v) for k,v in c['links'].items()};gold|=expected
  labels=r.get('labels',{});proposed={(c['id'],k,v) for k,v in labels.items() if v!='none'};pred|=proposed
  plan=r['snapshot']['plan'];offered=set(s['id'] for s in plan['steps'] if s['rest_minutes'] is not None) if plan else set();timers=set(c['timers'])
  correct_waits+=len(offered&timers);unsafe+=len(offered-timers);missed+=len(timers-offered);valid+=bool(plan);failures+=not bool(plan);complete+=bool(plan) and proposed==expected and offered==timers
  abstentions+=sum(a['validation']=='unresolved' for a in (plan['links'] if plan else []));latencies.append(r['wall_seconds'])
 tp=len(gold&pred);fp=len(pred-gold);fn=len(gold-pred)
 return dict(cases=len(cases),source_lines=sum(len(c['text'].splitlines()) for c in cases),gold_links=len(gold),tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,valid_plans=valid,gold_waits=sum(len(c['timers']) for c in cases),correct_waits=correct_waits,unsupported_timer_decisions=unsafe,missed_waits=missed,complete_workflows=complete,abstentions=abstentions,model_schema_failures=failures,mean_seconds=statistics.mean(latencies),max_seconds=max(latencies))
def main():
 p=argparse.ArgumentParser();p.add_argument('--split',choices=['development','holdout'],default='holdout');p.add_argument('--out',required=True);a=p.parse_args();out=R/a.out
 if out.exists():raise SystemExit('Refuse to overwrite any existing run directory')
 out.mkdir(parents=True);f=json.loads((R/'evaluation/v5/data-freeze.json').read_text());data=R/'evaluation/v5'/f'{a.split}.json';assert sha(data)==f['files'][data.name]
 if a.split=='holdout':
  freeze=json.loads((R/'evaluation/v5/candidate-freeze.json').read_text());assert all(sha(R/n)==h for n,h in freeze['files'].items())
 cases=json.loads(data.read_text());all_records={}
 for method in ['rules','v4','v5']:
  rows=[]
  for c in cases:
   factory=Previous if method=='v4' else AttentionAgent
   agent=factory(c['text'],**({'infer':rules,'mode':'rules'} if method=='rules' else {}));start=time.perf_counter();list(agent.run());snap=agent.snapshot();labels=agent.trace[3].result.get('labels',{}) if len(agent.trace)>3 else {}
   r=dict(id=c['id'],source=c['text'],labels=labels,snapshot=snap,raw_evidence=agent.raw_evidence,wall_seconds=time.perf_counter()-start);(out/f'{method}-{c["id"]}.json').write_text(json.dumps(r,indent=2)+'\n');rows.append(r);print(method,c['id'],snap['phase'],flush=True)
  all_records[method]=rows
 summary={m:{'total':metrics(cases,rs),'groups':{g:metrics([c for c in cases if c['group']==g],[r for c,r in zip(cases,rs) if c['group']==g]) for g in ['1-3','4-6','7-12','13-25']}} for m,rs in all_records.items()};summary['annotation']='Assistant-authored prospective varied cases, implementer-visible labels, no independent adjudication. Rules share candidate structure and source policy. No retry. All historical data unchanged.'
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
