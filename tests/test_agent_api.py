import json,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from server_agent import app,SESSIONS,MAX_SESSIONS,remember
from attention_agent import AttentionAgent,Decision,Phase
class AgentAPI(unittest.TestCase):
 def setUp(self):self.c=TestClient(app)
 def fixture(self):
  a=AttentionAgent('Wait for 5 minutes.\nRead the label.',infer=lambda _:({'1':'none','2':'none'},{}));list(a.run());remember(a);return a
 def test_stale_version_and_unknown_id(self):
  a=self.fixture();r=self.c.post(f'/api/agent/session/{a.id}/decision',json={'expected_version':3,'decision':{'kind':'confirm_step','source_id':1}});self.assertEqual(r.status_code,409);self.assertEqual(a.version,0)
  self.assertEqual(self.c.get('/api/agent/session/unknown').status_code,404)
 def test_explicit_confirmation_and_invalidation(self):
  a=self.fixture();url=f'/api/agent/session/{a.id}/decision'
  self.assertEqual(self.c.post(url,json={'expected_version':0,'decision':{'kind':'start_timer','source_id':1}}).status_code,409)
  self.assertEqual(self.c.post(url,json={'expected_version':0,'decision':{'kind':'start_timer','source_id':1,'confirmed':True,'demo':True}}).status_code,200)
  self.assertEqual(self.c.delete(f'/api/agent/session/{a.id}').status_code,200);self.assertEqual(a.phase,Phase.STALE);self.assertIsNone(self.c.get(f'/api/agent/session/{a.id}').json()['plan'])
 def test_checkpoint_source_tampering_rejected(self):
  a=self.fixture();receipt=a.export().model_dump();receipt['source_steps'][0]['source']='Invent a new experimental step.'
  self.assertEqual(self.c.post(f'/api/agent/session/{a.id}/resume',json={'expected_version':0,'receipt':receipt}).status_code,422)
  self.assertEqual(a.phase,Phase.REVIEW)
 def test_stream_error_contains_actual_failed_tool(self):
  with patch('attention_agent.infer_semantics',side_effect=TimeoutError('Injected timeout')):
   # Inject explicit agent factory because the default callable was bound at definition.
   original=AttentionAgent
   def factory(source):return original(source,infer=lambda _:(_ for _ in ()).throw(TimeoutError('Injected timeout')))
   with patch('server_agent.AttentionAgent',side_effect=factory):
    rows=[json.loads(x) for x in self.c.post('/api/agent/stream',json={'text':'Wait for 5 minutes.'}).text.splitlines()]
  self.assertEqual(rows[-1]['type'],'error');self.assertEqual(rows[-2]['event']['tool'],'propose_temporal_links');self.assertFalse(any(x['type']=='result' for x in rows))
 def test_contracts_and_input_boundaries(self):
  self.assertGreaterEqual(len(self.c.get('/api/agent/tools').json()),11)
  self.assertEqual(self.c.post('/api/agent/stream',json={'text':'x'*12001}).status_code,422)
  self.assertEqual(self.c.post('/api/agent/stream',json={'text':'short'}).status_code,422)
