"""Build prepared scenarios from real frozen-run artifacts; no new inference.

A/C handoffs use a real10second demonstration. Initial trace remains the original
measured tool trace, not a reconstruction or simulated successful inference.
"""
import json,time,sys,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from agent_v5 import AttentionAgent,AttentionPlan,SourceBundle,extract_source_steps,ReviewQueue,TraceEvent,Phase,Decision
configs={'A':('S01','The clear wait: one source-supported interval. Confirm a ten-second demonstration; no experiment is running.'),'B':('M03','The uncertain note: repeated waits leave the target unspecified. Source-only abstention; no Gemma call was needed. Timer options remain blocked.'),'C':('X01','The longer workflow: thirteen original lines, two sections, two recorded Gemma classifications. Inspect each source pair and its return handoff.')}
for key,(id,description) in configs.items():
 record=json.loads((R/'evaluation/v5/final'/f'v5-{id}.json').read_text());snap=record['snapshot'];assert snap['plan'] is not None
 plan=copy.deepcopy(snap['plan']);plan['mode']='recorded';plan['agent']=snap;plan['inference_evidence']=record['raw_evidence'];plan['model_calls']=(record['raw_evidence'] or {}).get('model_calls',0);plan['scenario_description']=description;plan['engine']='Recorded v0.5 source-pair workflow / '+('Gemma3:4b' if plan['model_calls'] else 'source-only abstention')
 if key!='B':
  a=AttentionAgent(record['source']);a.bundle=extract_source_steps(record['source']);a.plan=AttentionPlan.model_validate(snap['plan']);a.phase=Phase.REVIEW;a.trace=[TraceEvent.model_validate(e) for e in snap['trace']];a.reviews=ReviewQueue.model_validate(snap['reviews']);step=next(s for s in a.plan.steps if s.rest_minutes is not None)
  a.decide(Decision(kind='start_timer',source_id=step.id,confirmed=True,demo=True),a.version);time.sleep(10.05);a.decide(Decision(kind='timer_finished'),a.version);plan['recorded_handoff']=a.handoff().model_dump();plan['recorded_handoff_provenance']='Actual automated ten-second wall-time demonstration, no participant or physical experiment.';(R/'evaluation/v5'/f'scenario-{key}-receipt.json').write_text(a.export().model_dump_json(indent=2))
 (R/'static'/f'scenario-v5-{key}.json').write_text(json.dumps(plan,indent=2)+'\n')
 print('Recorded scenario',key,'model calls',plan['model_calls'],flush=True)
