"""Loopback-only v0.8 candidate. No deployment or external writes."""
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from pydantic import Field
from app import ROOT
from server_v6 import app as prior_app
from server_v5 import LOCK,get_session
from agent_v5 import Contract,Phase
from semantic_v8 import ask,session_facts,ModelBusy
app=FastAPI(title='BenchSloth v0.8 local review')
app.router.routes.extend(r for r in prior_app.router.routes if getattr(r,'path','') not in ['/api/agent/session/{id}/ask','/product/{name}'])
class Question(Contract):
 expected_version:int=Field(ge=0)
 question:str=Field(min_length=1,max_length=500)
 analysis_mode:str='lookup'
@app.post('/api/agent/session/{id}/ask')
def question(id:str,payload:Question):
 with LOCK:
  a=get_session(id)
  if a.version!=payload.expected_version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'Source/session changed; answer discarded.')
  source=a.plan.protocol;facts=session_facts(a.snapshot());version=a.version
 try:result=ask(source,payload.question,facts,payload.analysis_mode)
 except ModelBusy as e:raise HTTPException(429,str(e)) from e
 except ValueError as e:raise HTTPException(422,str(e)) from e
 except Exception as e:raise HTTPException(503,'Local analysis failed; no answer accepted. '+str(e)) from e
 with LOCK:
  a=get_session(id)
  if a.version!=version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'Session changed during analysis. Answer discarded.')
 result['session_version']=version
 return result
@app.get('/product/{name}')
def product_file(name:str):
 if name not in ['intelligence-v6.js','product-v6.css','desk-v8.css','desk-core-v8.js','desk-v8.js','revision-core-v8.js','revision-v8.js','revision-v8.css','revision-replays-v8.js','timing-core-v8.js','timing-v8.js','timing-v8.css']:raise HTTPException(404)
 return FileResponse(ROOT/'static'/name)

from revision_v8 import spans,versions,baseline,infer as revision_infer,hybrid
class RevisionPair(Contract):
 old:str=Field(min_length=1,max_length=100000)
 new:str=Field(min_length=1,max_length=100000)
 old_ids:list[int]
 new_ids:list[int]
 use_model:bool=False
@app.post('/api/revisions/compare')
def compare_revisions(payload:RevisionPair):
 try:
  ctx=spans(payload.old,payload.new,payload.old_ids,payload.new_ids);exact=versions(payload.old,payload.new);base=baseline(ctx);model=revision_infer(ctx) if payload.use_model else None
  return dict(context=ctx,exact=exact,baseline=base,model=model,hybrid=hybrid(ctx,model),model_calls=int(payload.use_model),read_only=True,timer_authority=False)
 except ModelBusy as e:raise HTTPException(429,str(e)) from e
 except ValueError as e:raise HTTPException(422,str(e)) from e
 except Exception as e:raise HTTPException(503,'Local revision proposal failed; no interpretation accepted. '+str(e)) from e

@app.get('/evidence-v8/index.html')
def pivot_evidence():return FileResponse(ROOT/'demo/evidence-v8/index.html')

# The v8 default is a full-document deterministic planner, with stricter
# unscoped-restriction holds. It is not the frozen evaluated semantic engine.
# Historical Gemma planners stay available in their frozen modules, not as the v8 default.
from source_agent_v8 import AttentionAgent
from server_v5 import remember
from source_review_v8 import apply_source_review_guards
from document_v8 import document
class ProtocolRequest(Contract):
 text:str=Field(min_length=1,max_length=100000)
@app.post('/api/source/plan')
def source_plan(payload:ProtocolRequest):
 import time
 began=time.perf_counter()
 try:
  # Validate the full source without invoking the frozen model parser.
  document(payload.text)
  a=AttentionAgent(payload.text,mode='source-plan');list(a.run())
  if a.phase!=Phase.REVIEW:raise ValueError('No complete deterministic source plan accepted.')
  source_review_flags=apply_source_review_guards(a)
  a.plan.engine='Deterministic source plan / original source restrictions';remember(a);plan=a.plan.model_dump();plan.update(agent=a.snapshot(),model_calls=0,inference_evidence=a.raw_evidence,engine='Deterministic source plan / original source restrictions',wall_seconds=time.perf_counter()-began,source_review_flags=source_review_flags,document=a.document,wait_classification=a.classifications)
  return plan
 except ValueError as e:raise HTTPException(422,str(e)) from e
