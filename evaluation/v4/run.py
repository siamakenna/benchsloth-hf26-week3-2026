"""Prospective model/verification/agent comparison. No retries or fixture fallback."""
import argparse,hashlib,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from attention import infer_semantics,baseline_links,build_plan as v2plan
from attention_agent import AttentionAgent,Decision,Phase

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def score(cases,records,method):
 gold=set();pred=set();offered=correct=unsafe=missing=valid=0
 for c,r in zip(cases,records):
  for k,v in c['links'].items():gold.add((c['id'],k,v))
  for k,v in r.get(method+'_labels',{}).items():
   if v!='none':pred.add((c['id'],k,v))
  plan=r.get(method+'_plan')
  if not plan:missing+=len(c['timers']);continue
  valid+=1;ids=set()
  for s in plan['steps']:
   t=s['rest_minutes'];g=c['timers'].get(str(s['id']))
   if t is not None:offered+=1;correct+=t==g;unsafe+=t!=g;ids.add(str(s['id']))
  missing+=len(set(c['timers'])-ids)
 tp=len(gold&pred);fp=len(pred-gold);fn=len(gold-pred)
 return dict(cases=len(cases),lines=sum(len(c['text'].splitlines()) for c in cases),valid_plans=valid,link_tp=tp,link_fp=fp,link_fn=fn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,gold_waits=sum(len(c['timers']) for c in cases),offered=offered,correct_waits=correct,unsupported_eligibility=unsafe,missed_waits=missing)

def main():
 p=argparse.ArgumentParser();p.add_argument('--split',choices=['development','holdout'],default='development');p.add_argument('--out',required=True);a=p.parse_args();out=R/a.out
 if out.exists() and any(out.glob('*.json')):raise SystemExit('Refuse overwrite')
 out.mkdir(parents=True,exist_ok=True);data=R/f'evaluation/v4/{a.split}.json';f=json.loads((R/'evaluation/v4/data-freeze.json').read_text());assert sha(data)==f['files'][data.name]
 engine={n:sha(R/n) for n in ['attention_agent.py','attention.py','app.py','evaluation/v4/run.py']}
 if a.split=='holdout':assert engine==json.loads((R/'evaluation/v4/candidate-freeze.json').read_text())['files']
 cases=json.loads(data.read_text());records=[];started=time.perf_counter()
 for c in cases:
  rule=baseline_links(c['text']);ra=AttentionAgent(c['text'],mode='rules',infer=lambda _,raw=rule:(raw,{}));list(ra.run())
  r={'id':c['id'],'input':c['text'],'rules_labels':ra.trace[3].result['labels'] if ra.phase!=Phase.FAILED else {},'rules_plan':ra.plan.model_dump() if ra.plan else None}
  clock=[0];agent=AttentionAgent(c['text'],clock=lambda:clock[0]);events=list(agent.run());r['events']=[e.model_dump() for e in events]
  if agent.raw_evidence:r.update(agent.raw_evidence)
  if agent.phase!=Phase.FAILED:
   raw=agent.raw_evidence['response']['response'];raw=json.loads(raw)
   r['raw_labels']=raw;r['v2_labels']=raw;r['v2_plan']=v2plan(c['text'],raw)
   r['agent_labels']=events[3].result['labels'];r['agent_plan']=agent.plan.model_dump()
   started_handoff=time.perf_counter();outcomes=[]
   for s in agent.plan.steps:
    if s.rest_minutes is None:continue
    # Controlled clock is an explicit simulation, not physical waiting or a human trial.
    for previous in agent.plan.steps:
     if previous.id<s.id and previous.id not in agent.confirmed:agent.decide(Decision(kind='confirm_step',source_id=previous.id),agent.version)
    agent.decide(Decision(kind='start_timer',source_id=s.id,confirmed=True,demo=True),agent.version);clock[0]+=10000
    h=agent.decide(Decision(kind='timer_finished'),agent.version)
    expected=next((x for x in agent.plan.steps if x.id>s.id and x.id not in agent.confirmed),None)
    outcomes.append(dict(source_id=s.id,correct=h.next_source_id==(expected.id if expected else None),exact_source=h.next_source==(expected.source if expected else None)))
   r['handoff_tests']=outcomes;r['handoff_lookup_ms']=(time.perf_counter()-started_handoff)*1000;r['receipt']=agent.export().model_dump()
  else:r['error']=events[-1].error
  records.append(r);(out/(c['id']+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(c['id'],r.get('error','valid'),flush=True)
 summary=dict(split=a.split,engine=engine,wall_seconds=time.perf_counter()-started,metrics={m:score(cases,records,m) for m in ['rules','v2','agent']},handoffs={'n':sum(len(r.get('handoff_tests',[])) for r in records),'correct':sum(x['correct'] and x['exact_source'] for r in records for x in r.get('handoff_tests',[]))},failures=sum('error'in r for r in records),annotation='Assistant-authored synthetic labels, not independent human gold. Handoff tests use a simulated clock. No human time saved or manual-source-review speed measured.')
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
