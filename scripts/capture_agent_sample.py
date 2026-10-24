"""Capture actual local Gemma/tool events and a real 10-second automated demo handoff."""
import json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from attention_agent import AttentionAgent,Decision,Phase
SOURCE='''1. Wait for 5 minutes.
2. After that wait, record the label.
3. Incubate overnight.'''
def main():
 a=AttentionAgent(SOURCE);list(a.run())
 if a.phase!=Phase.REVIEW:raise SystemExit(a.trace[-1].error)
 initial=a.snapshot();plan=a.plan.model_dump();plan['mode']='recorded';plan['agent']=initial
 plan['agent']['id']='recorded-example-session';plan['engine']='Recorded local Gemma 4B / actual typed agent trace'
 a.decide(Decision(kind='start_timer',source_id=1,confirmed=True,demo=True),a.version)
 time.sleep(10.05)
 a.decide(Decision(kind='timer_finished'),a.version)
 plan['recorded_handoff']=a.handoff().model_dump();plan['recorded_handoff_provenance']='Actual automated demonstration; 10-second browser-convenience interval measured with real wall time. No human participant or experiment.'
 (R/'static/agent-sample.json').write_text(json.dumps(plan,indent=2)+'\n')
 (R/'evaluation/v4/sample-recording.json').write_text(json.dumps({'source':SOURCE,'raw_evidence':a.raw_evidence,'initial_trace':initial['trace'],'recorded_session_receipt':a.export().model_dump()},indent=2)+'\n')
 print('Recorded actual Gemma,',len(initial['trace']),'tools; handoff:',plan['recorded_handoff']['next_source_id'])

if __name__=="__main__":main()
