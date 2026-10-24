import unittest
from fastapi.testclient import TestClient
from server_v5 import app,remember
from runtime_v5 import AttentionAgent
from agent_v5 import Phase
class V5API(unittest.TestCase):
 def setUp(self):
  self.c=TestClient(app);self.a=AttentionAgent('Wait 5 minutes.\nAfter that wait, read the tag.',infer=lambda _:({'1':'none','2':'after:1'},{}));list(self.a.run());remember(self.a);self.url=f'/api/agent/session/{self.a.id}/decision'
 def test_correction_and_stale_response(self):
  r=self.c.post(self.url,json={'expected_version':0,'decision':{'kind':'correct_link','source_id':2,'target_id':1,'relation':'after'}});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['plan']['links'][0]['validation'],'user-corrected');self.assertEqual(len(r.json()['handoff']['changes']),1)
  self.assertEqual(self.c.post(self.url,json={'expected_version':0,'decision':{'kind':'reject_link','source_id':2}}).status_code,409)
 def test_rejection_preserves_source_and_eligibility(self):
  r=self.c.post(self.url,json={'expected_version':0,'decision':{'kind':'reject_link','source_id':2}});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['plan']['steps'][1]['source'],'After that wait, read the tag.');self.assertEqual(r.json()['plan']['steps'][0]['rest_minutes'],5)
 def test_unknown_correction_target_fails_without_version_change(self):
  r=self.c.post(self.url,json={'expected_version':0,'decision':{'kind':'correct_link','source_id':2,'target_id':9,'relation':'after'}});self.assertEqual(r.status_code,409);self.assertEqual(self.a.version,0)

 def test_malformed_timer_returns_422_not_500(self):
  r=self.a.export().model_dump();r['handoff']['timer']={'source_id':1,'source':'Wait 5 minutes.'};before=self.a.snapshot();response=self.c.post(f'/api/agent/session/{self.a.id}/resume',json={'expected_version':self.a.version,'receipt':r});self.assertEqual(response.status_code,422);self.assertEqual(before,self.a.snapshot())
 def test_shortened_source_checkpoint_is_rejected(self):
  r=self.a.export().model_dump();r['handoff']['timer']={'source_id':1,'source':'Wait 5 minutes.','start_ms':0,'end_ms':1,'duration_ms':1,'status':'completed','demo':False,'elapsed_ms':1};response=self.c.post(f'/api/agent/session/{self.a.id}/resume',json={'expected_version':self.a.version,'receipt':r});self.assertEqual(response.status_code,422)
