import copy,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from revision_v8 import versions,spans,flags,baseline,hybrid
from server_v8 import app
class RevisionContracts(unittest.TestCase):
 def setUp(self):self.old='Wait 5 minutes.\nWatch continuously.\nRecord the label.';self.new='Wait 8 minutes.\nYou may stop watching.\nRecord the label.'
 def test_exact_original_versions_and_occurrences(self):
  v=versions(self.old,self.new);self.assertEqual(v['old_rows'][0],{'id':1,'source':'Wait 5 minutes.'});self.assertEqual(v['new_rows'][0]['source'],'Wait 8 minutes.');self.assertFalse(v['timer_transfer']);self.assertFalse(v['session_transfer'])
 def test_numeric_monitoring_and_negation_always_visible(self):
  for ids,expected in [([1],'numeric'),([2],'Monitoring'),([2],'restriction')]:self.assertTrue(any(expected in f for f in flags(spans(self.old,self.new,ids,ids))))
 def test_model_same_cannot_suppress_critical_alerts(self):
  ctx=spans(self.old,self.new,[1],[1]);before=copy.deepcopy(ctx);p=hybrid(ctx,{'classification':'same'});self.assertTrue(p['critical']);self.assertTrue(p['deterministic_flags']);self.assertTrue(p['review_required']);self.assertFalse(p['timer_authority']);self.assertEqual(ctx,before)
 def test_unknown_or_duplicate_or_noninteger_ids_fail_closed(self):
  for ids in [[999],[1,1],[],[True],['1']]:
   with self.assertRaises(ValueError):spans(self.old,self.new,ids,[1])
 def test_all_exact_edits_account_for_numeric_changes(self):
  v=versions(self.old,self.new);self.assertIn('Wait 5 minutes.',v['exact_edits'][0]['old_text']);self.assertIn('Wait 8 minutes.',v['exact_edits'][0]['new_text'])
 def test_repeated_words_keep_distinct_occurrences(self):
  ctx=spans('Wait 5 minutes.\nWait 5 minutes.','Wait 5 minutes.\nWait 6 minutes.',[2],[2]);self.assertEqual(ctx['old'][0]['id'],2);self.assertIn('numeric',' '.join(flags(ctx)))
 def test_long_input_scope_exact_source12_not_position(self):
  old='\n'.join('Source marker '+str(i) for i in range(1,24));new=old.replace('marker 12','changed marker 12');ctx=spans(old,new,[12],[12]);self.assertEqual(ctx['old'][0]['source'],'Source marker 12');self.assertEqual(ctx['new'][0]['source'],'Source changed marker 12')
 def test_default_revision_api_makes_zero_model_calls(self):
  with patch('server_v8.revision_infer',side_effect=AssertionError('No model call')) as m:
   r=TestClient(app).post('/api/revisions/compare',json={'old':self.old,'new':self.new,'old_ids':[1],'new_ids':[1]});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['model_calls'],0);m.assert_not_called()
 def test_revision_api_rejects_unknown_ids(self):
  r=TestClient(app).post('/api/revisions/compare',json={'old':self.old,'new':self.new,'old_ids':[12],'new_ids':[1]});self.assertEqual(r.status_code,422)
 def test_failed_model_never_becomes_recorded_success(self):
  with patch('server_v8.revision_infer',side_effect=TimeoutError('fixture timeout')):
   r=TestClient(app).post('/api/revisions/compare',json={'old':self.old,'new':self.new,'old_ids':[1],'new_ids':[1],'use_model':True});self.assertEqual(r.status_code,503);self.assertNotIn('model',r.json())

class SourceDefault(unittest.TestCase):
 def test_new_source_default_does_not_invoke_model(self):
  with patch('association_v5.urllib.request.urlopen',side_effect=AssertionError('No model call')):
   r=TestClient(app).post('/api/source/plan',json={'text':'Wait 5 minutes.\nAfter that wait, record the tag.'});self.assertEqual(r.status_code,200);self.assertEqual(r.json()['model_calls'],0);self.assertEqual(r.json()['mode'],'source-plan');self.assertEqual([s['source'] for s in r.json()['steps']],['Wait 5 minutes.','After that wait, record the tag.'])
