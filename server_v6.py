"""Loopback-only product API: frozen v5 planner plus read-only Gemma QA."""
import json,threading
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from pydantic import Field
from server_v5 import app as v5_app,SESSIONS,LOCK,get_session,remember
from app import ROOT
from agent_v5 import Contract,Phase
from semantic_v6 import ask,session_facts
app=FastAPI(title='BenchSloth v0.6')
app.router.routes.extend(r for r in v5_app.router.routes if getattr(r,'path','') not in ['/media/{name}','/evidence/{name}'])
QA_GATE=threading.BoundedSemaphore(1)
class Question(Contract):
 expected_version:int=Field(ge=0)
 question:str=Field(min_length=1,max_length=500)
@app.post('/api/agent/session/{id}/ask')
def question(id:str,payload:Question):
 with LOCK:
  a=get_session(id)
  if a.version!=payload.expected_version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'Source/session changed; ask again from the current plan.')
  source=a.plan.protocol;facts=session_facts(a.snapshot());version=a.version
 if not QA_GATE.acquire(blocking=False):raise HTTPException(429,'One local question is already running; try again when it ends.')
 try:
  try:result=ask(source,payload.question,facts)
  except ValueError as e:raise HTTPException(422,str(e)) from e
  except Exception as e:raise HTTPException(503,'Local question failed; no answer accepted. '+str(e)) from e
 finally:QA_GATE.release()
 with LOCK:
  a=get_session(id)
  if a.version!=version or a.phase in [Phase.STALE,Phase.FAILED]:raise HTTPException(409,'Session changed during inference. Answer discarded; ask again.')
 result['session_version']=version
 return result
@app.get('/api/questions')
def recorded_questions():
 p=ROOT/'static/questions-v6.json'
 return json.loads(p.read_text()) if p.exists() else {}
@app.get('/product/{name}')
def product_file(name:str):
 if name not in ['intelligence-v6.js','product-v6.css']:raise HTTPException(404)
 return FileResponse(ROOT/'static'/name)
@app.get('/media/{name}')
def media(name:str):
 files={'demo.webm':ROOT/'assets/v6/demo-captioned.webm','evaluation.json':ROOT/'evaluation/v6/summary.json'}
 if name not in files or not files[name].exists():raise HTTPException(404)
 return FileResponse(files[name])
@app.get('/evidence/{name}')
def evidence_file(name:str):
 if name not in ['index.html','explorer.js','data.json','summary.json','boundary-summary.json']:raise HTTPException(404)
 return FileResponse(ROOT/'demo/evidence'/name)
