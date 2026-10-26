import unittest,hashlib
from unittest.mock import patch
from fastapi.testclient import TestClient
from server_v8 import app
from document_v8 import document,source_bundle,context_windows,references,wait_classification
from semantic_v8 import ask,context,classify_rules
from app import input_lines
class FullDocument(unittest.TestCase):
 def plan(self,s):
  with patch('urllib.request.urlopen',side_effect=AssertionError('No model')):
   r=TestClient(app).post('/api/source/plan',json={'text':s});self.assertEqual(r.status_code,200,r.text[:100]);return r.json()
 def test_150_occurrences_no_loss_raw_hash_offsets(self):
  s='\r\n'.join('  # Section '+str(i)if i%20==0 else '  Original occurrence '+str(i)+'  'for i in range(150));d=document(s);self.assertEqual(d['source'],s);self.assertEqual(d['source_hash'],hashlib.sha256(s.encode()).hexdigest());self.assertEqual(len(d['rows']),150)
  for r in d['rows']:self.assertEqual(s[r['start']:r['end']],r['source'])
  self.assertEqual(len(self.plan(s)['steps']),150)
 def test_model_parser_bound_stays_frozen(self):
  with self.assertRaises(ValueError):input_lines('x\n'*49)
 def test_full_bounds_reject_without_partial_result(self):
  for s in ['x\n'*513,'x'*100001]:
   self.assertEqual(TestClient(app).post('/api/source/plan',json={'text':s}).status_code,422)
 def test_duplicate_text_occurrences_not_merged(self):
  d=document('Wait 5 minutes.\n'*150);self.assertEqual([r['id']for r in d['rows']],list(range(1,151)));self.assertEqual(len(source_bundle(d['source'])),150)
 def test_overlap_context_deduplicates_ids_not_original_occurrences(self):
  s='# Source\n'+'\n'.join('Original '+str(i)for i in range(150));w=context_windows(s,[48,49]);self.assertEqual(len({r['id']for r in w['rows']}),len(w['rows']));self.assertIn(1,[r['id']for r in w['rows']]);self.assertIn(47,[r['id']for r in w['rows']])
 def test_huge_selected_original_fails_context_without_truncation(self):
  with self.assertRaises(ValueError):context_windows('x'*7000,[1])
 def test_oversized_model_span_does_not_block_deterministic_review(self):
  s='Wait 5 minutes.\nUnclear which wait: '+('original context '*500)
  with patch('semantic_v8.infer',side_effect=AssertionError('No inference')):
   a=ask(s,'Which wait does source 2 refer to?');self.assertEqual(a['model_calls'],0);self.assertEqual(a['answer']['status'],'ambiguous');self.assertTrue(any(c['excerpt']==s.splitlines()[1].strip()for c in a['answer']['citations']))
 def test_explicit_long_lookup_includes_last_original(self):
  s='\n'.join('Occurrence '+str(i)for i in range(150));a=ask(s,'Show source 150');self.assertEqual(a['answer']['citations'],[{'id':150,'excerpt':'Occurrence 149'}]);self.assertEqual(a['model_calls'],0)
 def test_unknown_mixed_ids_fail_closed(self):
  a=ask('Original source.\n'*150,'Show source 150 and source 999');self.assertEqual(a['answer']['citations'],[])
 def test_full_ordinal_before_candidate_budget(self):
  s='# A\nWait 1 minutes.\n'+'\n'.join('Wait '+str(i)+' minutes.'for i in range(2,70))+'\n# B\nAfter the first wait, record the label.';ctx=context(s);self.assertEqual(classify_rules(ctx)['target_id'],2);self.assertIn(2,[r['id']for r in ctx['candidates']]);self.assertLessEqual(len(ctx['candidates']),3)
 def test_explicit_source_beats_recent_candidate(self):
  s='Wait 1 minutes.\n'+'\n'.join('Wait '+str(i)+' minutes.'for i in range(2,65))+'\nAfter the wait at source 1, record the label.';self.assertEqual(classify_rules(context(s))['target_id'],1)
 def test_cross_section_reference_retained_without_proximity_guess(self):
  s='# A\nWait 5 minutes.\n# B\nMonitor during the interval.';d=document(s);self.assertFalse(references(d['rows'],d['rows'][-1])['resolved']);p=self.plan(s);self.assertEqual(p['rest_windows'],0);self.assertEqual(p['protocol'],s);self.assertTrue(any(a['validation']=='unresolved'for a in p['links']));self.assertTrue(any(2 in r['source_ids']and 4 in r['source_ids']for r in p['agent']['reviews']['items']))
 def test_reference_notes_do_not_redefine_wait_ordinals(self):
  d=document('Wait 5 minutes.\nDuring the first wait, inspect the label.\nWait 7 minutes.\nAfter the second wait, record the identifier.');self.assertEqual(references(d['rows'],d['rows'][-1])['ids'],[3])
 def test_explicit_cross_section_reports_original_scope(self):
  d=document('# A\nWait 5 minutes.\n# B\nAfter source 2, record a label.');r=references(d['rows'],d['rows'][-1]);self.assertTrue(r['cross_section']);self.assertEqual(r['ids'],[2])
 def test_global_restriction_blocks_earlier_and_later_waits(self):
  p=self.plan('Wait 5 minutes.\n'+'Read the identifier.\n'*70+'Never leave the procedure unattended.\nWait 6 minutes.');self.assertEqual(p['rest_windows'],0)
 def test_wait_taxonomy_is_evidence_only(self):
  cases={'Monitor continuously for 5 minutes.':'explicitly_monitored_period','If approved, wait 5 minutes.':'conditional_wait','Wait 5–10 minutes.':'duration_range','Prepare labels during source 1.':'overlapping_preparation_or_dependency','Run centrifuge for 5 minutes.':'equipment_running_supervision_unknown','Wait overnight.':'unresolved_or_unsupported_duration','Wait 5 minutes.':'explicit_wait_with_source_evidence'}
  for s,c in cases.items():
   d=document(s);v=wait_classification(d['rows'][0],d['rows']);self.assertIn(c,v['classes']);self.assertFalse(v['timer_authority']);self.assertIsNone(v['human_label'])
 def test_review_acknowledgement_cannot_enable_wait(self):
  c=TestClient(app);p=self.plan('Wait 5 minutes.\nMonitor throughout the interval.');sid=p['agent']['id'];rev=p['agent']['reviews']['items'][0]['id'];a=c.post(f'/api/agent/session/{sid}/decision',json={'expected_version':0,'decision':{'kind':'acknowledge_review','review_id':rev}});self.assertEqual(a.status_code,200);r=c.post(f'/api/agent/session/{sid}/decision',json={'expected_version':1,'decision':{'kind':'start_timer','source_id':1,'confirmed':True}});self.assertEqual(r.status_code,409)
 def test_simple_original_wait_still_needs_explicit_confirmation(self):
  c=TestClient(app);p=self.plan('Wait 5 minutes.');self.assertEqual(p['rest_windows'],1);sid=p['agent']['id'];r=c.post(f'/api/agent/session/{sid}/decision',json={'expected_version':0,'decision':{'kind':'start_timer','source_id':1,'confirmed':False}});self.assertEqual(r.status_code,409)
