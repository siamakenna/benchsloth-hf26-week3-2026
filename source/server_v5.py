"""v0.5 loopback API. In-memory sessions, optimistic versions, bounded capacity."""
import json,threading,time
from collections import OrderedDict
from fastapi import HTTPException
from fastapi.responses import StreamingResponse,FileResponse
from pydantic import Field
from fastapi import FastAPI
from server import app as base_app
app=FastAPI(title="BenchSloth v0.5")
app.router.routes.extend(r for r in base_app.router.routes if not getattr(r,"path","").startswith("/api/agent") and not getattr(r,"path","").startswith("/media"))
from app import ProtocolRequest,ROOT
from runtime_v5 import AttentionAgent
from agent_v5 import Decision,Contract,Receipt,TOOL_CONTRACTS,Phase

SESSIONS=OrderedDict();LOCK=threading.RLock();MAX_SESSIONS=32
class SessionDecision(Contract):
    expected_version:int=Field(ge=0)
    decision:Decision
class ResumeRequest(Contract):
    expected_version:int=Field(ge=0)
    receipt:Receipt

def remember(a):
    with LOCK:
        SESSIONS[a.id]=a
        while len(SESSIONS)>MAX_SESSIONS:SESSIONS.popitem(last=False)

def get_session(id):
    if id not in SESSIONS:raise HTTPException(404,'Session expired or unavailable. Import a saved checkpoint after reanalyzing source.')
    return SESSIONS[id]

@app.post('/api/agent/stream')
def agent_stream(payload:ProtocolRequest):
    def events():
        a=AttentionAgent(payload.text);start=time.perf_counter();iterator=a.run()
        names=['Preparing source','Parsing explicit durations','Associating source / local model when needed','Checking associations','Checking source restrictions','Building attention plan','Preparing human review','Ready for review']
        for name in names:
            yield json.dumps({'type':'stage','stage':name,'elapsed':time.perf_counter()-start})+'\n'
            try:event=next(iterator)
            except StopIteration:break
            yield json.dumps({'type':'tool','event':event.model_dump()})+'\n'
            if event.status=='failed':
                yield json.dumps({'type':'error','message':event.error,'trace':[e.model_dump() for e in a.trace]})+'\n';return
        if a.phase!=Phase.REVIEW:
            yield json.dumps({'type':'error','message':'Agent stopped before a complete plan.'})+'\n';return
        remember(a);plan=a.plan.model_dump();plan['wall_seconds']=round(time.perf_counter()-start,3);plan['agent']=a.snapshot();plan['inference_evidence']=a.raw_evidence;plan['model_calls']=(a.raw_evidence or {}).get('model_calls',0)
        yield json.dumps({'type':'result','result':plan})+'\n'
    return StreamingResponse(events(),media_type='application/x-ndjson',headers={'Cache-Control':'no-store'})

@app.get('/api/agent/tools')
def tools():return TOOL_CONTRACTS

@app.get('/api/agent/sample')
def sample():
    p=ROOT/'static'/'scenario-v5-A.json'
    if not p.exists():raise HTTPException(503,'Recorded agent sample has not been captured.')
    return json.loads(p.read_text())

@app.get('/api/agent/scenarios')
def scenarios():return {k:json.loads((ROOT/'static'/f'scenario-v5-{k}.json').read_text()) for k in ['A','B','C']}

@app.get('/api/agent/session/{id}')
def session(id:str):
    with LOCK:return get_session(id).snapshot()

@app.post('/api/agent/session/{id}/decision')
def decision(id:str,payload:SessionDecision):
    with LOCK:
        a=get_session(id)
        try:a.decide(payload.decision,payload.expected_version)
        except ValueError as e:raise HTTPException(409,str(e)) from e
        return a.snapshot()

@app.post('/api/agent/session/{id}/resume')
def resume(id:str,payload:ResumeRequest):
    with LOCK:
        a=get_session(id)
        if payload.expected_version!=a.version:raise HTTPException(409,'Stale session version')
        try:a.resume(payload.receipt)
        except ValueError as e:raise HTTPException(422,str(e)) from e
        return a.snapshot()

@app.get('/api/agent/session/{id}/export')
def export(id:str):
    with LOCK:
        try:return get_session(id).export().model_dump()
        except ValueError as e:raise HTTPException(409,str(e)) from e

@app.get('/media/{name}')
def media(name:str):
    files={'demo.webm':ROOT/'assets/v5/demo-captioned.webm','evaluation.json':ROOT/'evaluation/v5/final/summary.json'}
    if name not in files or not files[name].exists():raise HTTPException(404)
    return FileResponse(files[name])

@app.delete('/api/agent/session/{id}')
def invalidate_session(id:str):
    with LOCK:
        a=get_session(id)
        if a.phase not in [Phase.STALE,Phase.FAILED]:a.decide(Decision(kind='source_changed'),a.version)
        return {'status':'invalidated','version':a.version}

@app.get('/evidence/{name}')
def evidence_file(name:str):
    if name not in ['index.html','summary.json','boundary-summary.json']:raise HTTPException(404)
    return FileResponse(ROOT/'demo'/'evidence'/name)

@app.get('/downloads/benchsloth-source.zip')
def code_download():return FileResponse(ROOT/'demo'/'downloads'/'benchsloth-source.zip')
