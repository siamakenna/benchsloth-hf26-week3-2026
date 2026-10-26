"""V2 server; V1 engine/evaluator remain untouched as historical evidence."""
import json,time,urllib.request
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app import app,ProtocolRequest,OLLAMA_HOST,MODEL,input_lines
from attention import infer_semantics,build_plan,sample_plan

@app.post('/api/attention')
def attention(payload:ProtocolRequest):
    try:
        started=time.perf_counter();input_lines(payload.text)
        labels,_=infer_semantics(payload.text);result=build_plan(payload.text,labels)
        result['wall_seconds']=round(time.perf_counter()-started,3);return result
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e)) from e
    except RuntimeError as e:raise HTTPException(status_code=503,detail=str(e)) from e

@app.post('/api/attention/stream')
def stream(payload:ProtocolRequest):
    def events():
        started=time.perf_counter()
        def event(type,**data):return json.dumps(dict(type=type,elapsed=round(time.perf_counter()-started,3),**data))+'\n'
        try:
            yield event('stage',stage='Preparing source lines')
            input_lines(payload.text)
            yield event('stage',stage='Checking local model readiness')
            with urllib.request.urlopen(OLLAMA_HOST+'/api/tags',timeout=3) as r:tags=json.loads(r.read(500000))
            if MODEL not in [m.get('name') for m in tags.get('models',[])]:raise RuntimeError('Selected local model is not installed.')
            yield event('stage',stage='Analyzing source language')
            labels,_=infer_semantics(payload.text)
            yield event('stage',stage='Validating evidence links')
            result=build_plan(payload.text,labels)
            yield event('stage',stage='Preparing your Attention Map')
            result['wall_seconds']=round(time.perf_counter()-started,3)
            yield event('result',result=result)
        except Exception as e:yield event('error',message=str(e) if isinstance(e,(ValueError,RuntimeError)) else 'Local model could not be reached; check Ollama.')
    return StreamingResponse(events(),media_type='application/x-ndjson',headers={'Cache-Control':'no-store'})

@app.get('/api/attention/sample')
def sample():return sample_plan()
