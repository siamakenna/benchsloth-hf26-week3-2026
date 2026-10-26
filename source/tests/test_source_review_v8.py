import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from server_v8 import app
from source_review_v8 import review_cues
class LiteralReview(unittest.TestCase):
 def plan(self,source):
  with patch('urllib.request.urlopen',side_effect=AssertionError('No model transport')):
   r=TestClient(app).post('/api/source/plan',json={'text':source});self.assertEqual(r.status_code,200);return r.json()
 def test_draft_question_is_reviewed_without_answering(self):
  text='Prepare the sample.\nQuestion: Is an additional hold required?';p=self.plan(text);self.assertTrue(p['steps'][1]['review_needed']);self.assertTrue(any(2 in i['source_ids'] for i in p['agent']['reviews']['items']));self.assertEqual(p['protocol'],text);self.assertEqual(p['rest_windows'],0)
 def test_caveat_is_visible_and_never_resolved(self):
  p=self.plan('This method has not been fully verified.\nRead the original note.');self.assertTrue(p['source_review_flags']);self.assertFalse(p['source_review_flags'][0]['semantic_scope_resolved']);self.assertFalse(p['source_review_flags'][0]['timer_authority']);self.assertEqual(p['model_calls'],0)
 def test_conditional_scope_not_inferred_as_dependency(self):
  p=self.plan('If the optional branch applies, inspect the original note.\nRecord the identifier.');self.assertTrue(p['steps'][0]['review_needed']);self.assertEqual(p['links'],[]);self.assertEqual(p['steps'][0]['source'],'If the optional branch applies, inspect the original note.')
 def test_review_guard_does_not_expand_timer_admission_with_larger_document_capacity(self):
  p=self.plan('Wait 5 minutes.\nKeep the original restriction in view.');self.assertIsNone(p['steps'][1]['rest_minutes']);r=TestClient(app).post('/api/source/plan',json={'text':'\n'.join(['Original occurrence.']*49)});self.assertEqual(r.status_code,200)
 def test_duration_lookup_quotes_alternatives_without_fixed_timer(self):
  from semantic_v8 import ask
  source='Incubate at 4C for 1 hour or overnight.\nRecord the label.';a=ask(source,'How long is source 1?');self.assertEqual(a['answer']['citations'],[{'id':1,'excerpt':source.splitlines()[0]}]);self.assertEqual(a['model_calls'],0);p=self.plan(source);self.assertEqual(p['rest_windows'],0)
 def test_duration_fact_lookup_keeps_source_scope_and_rejects_fabricated_ids(self):
  from semantic_v8 import ask
  source='Observe for 30-60 minutes.\nUse 20 ml of buffer.';self.assertEqual(ask(source,'How long is source 2?')['answer']['status'],'not_available');self.assertEqual(ask(source,'How long is source 1 and source 999?')['answer']['status'],'not_available')

 def test_long_source_is_admitted_independently_of_model_parser(self):
  r=TestClient(app).post('/api/source/plan',json={'text':'\n'.join('Source occurrence '+str(i) for i in range(58))});self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['steps']),58)

 def test_bare_temperature_unit_is_quoted_without_inference(self):
  from semantic_v8 import ask
  text='Keep the sample at 4C.\nRecord the label.';a=ask(text,'What temperature is specified in source 1?');self.assertEqual(a['answer']['citations'],[{'id':1,'excerpt':'Keep the sample at 4C.'}]);self.assertEqual(a['model_calls'],0);self.assertEqual(ask(text,'What temperature is specified in source 2?')['answer']['status'],'not_available')
