"""Local-only v0.9. No publication/deployment or external model endpoint."""
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from pydantic import Field
from app import ROOT
from server_v8 import app as prior_app
from server_v5 import get_session,LOCK
from agent_v5 import Contract,Phase
from recovery_v9 import make_context,baseline,infer,ModelBusy
app=FastAPI(title='BenchSloth v0.9 local owner review')
app.router.routes.extend(r for r in prior_app.router.routes if getattr(r,'path','')not in ['/product/{name}'])
@app.get('/product/{name}')
def product(name:str):
 if name not in ['intelligence-v6.js','product-v6.css','desk-v8.css','desk-core-v8.js','desk-v8.js','revision-core-v8.js','revision-v8.js','revision-v8.css','revision-replays-v8.js','timing-core-v8.js','timing-v8.js','timing-v8.css','recovery-v9.js','recovery-v9.css']:raise HTTPException(404)
 return FileResponse(ROOT/'static'/name)
class Recover(Contract):
 expected_version:int=Field(ge=0)
 old:str=Field(min_length=1,max_length=100000)
 question:str=Field(default='Help me pick up where I left off',max_length=500)
 selected_ids:list[int]=Field(default_factory=list,max_length=6)
 mode:str='deterministic'
@app.post('/api/agent/session/{id}/recover')
def recover(id:str,payload:Recover):
 with LOCK:
  a=get_session(id)
  if a.version!=payload.expected_version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'Source/state changed. Context recovery discarded.')
  snap=a.snapshot();source=a.plan.protocol;version=a.version
  state=dict(version=version,source_hash=a.source_hash,phase=a.phase.value,confirmed_old_ids=[],confirmed_new_ids=list(a.confirmed),reviews=[r['question']for r in snap['reviews']['items']if r['status']=='pending'],next_source_id=snap['handoff']['next_source_id'])
 try:
  if payload.mode not in ['deterministic','gemma']:raise ValueError('Choose deterministic or actual local Gemma mode.')
  ctx=make_context(payload.old,source,state,payload.question,payload.selected_ids);result=dict(context=ctx,fallback=baseline(ctx),mode='Deterministic fallback / zero model calls',model_calls=0,model=None)
  if payload.mode=='gemma':result.update(model=infer(ctx),model_calls=1,mode='Local Gemma inference / experimental')
 except ModelBusy as e:raise HTTPException(429,str(e))from e
 except ValueError as e:raise HTTPException(422,str(e))from e
 except Exception as e:raise HTTPException(503,'Local Context Recovery unavailable; deterministic handoff remains available. '+str(e))from e
 with LOCK:
  a=get_session(id)
  if a.version!=version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'State changed during inference. Response discarded.')
 result.update(read_only=True,timer_authority=False,state_version=version)
 return result
