import json,unittest
from attention_agent import *
class AgentTest(unittest.TestCase):
 def run_agent(self,source,labels,clock=None):
  a=AttentionAgent(source,infer=lambda _:(labels,{}),clock=clock or (lambda:0));events=list(a.run());self.assertEqual(a.phase,Phase.REVIEW);return a
 def test_typed_tool_order_and_inspectable_results(self):
  a=self.run_agent('Wait for 5 minutes.\nAfter that wait, read label.',{'1':'none','2':'after:1'})
  self.assertEqual([e.tool for e in a.trace],list(TOOL_CONTRACTS)[:8]);self.assertTrue(all(e.status=='completed' for e in a.trace));self.assertEqual(a.plan.rest_windows,1)
 def test_wrong_model_during_does_not_veto_supported_wait(self):
  a=self.run_agent('Wait for 5 minutes.\nAfter that wait ends, record observation.',{'1':'none','2':'during:1'})
  self.assertEqual(a.plan.rest_windows,1);self.assertEqual(a.plan.links[0].relation,'after');self.assertEqual(a.plan.links[0].validation,'source-corrected')
 def test_scoped_source_restriction_preserves_other_wait(self):
  a=self.run_agent('Wait for 5 minutes.\nWait for 7 minutes.\nDuring the first wait, watch the tube.',{'1':'none','2':'none','3':'during:1'})
  self.assertEqual([s.rest_minutes for s in a.plan.steps],[None,7,None])
 def test_unresolved_target_not_invented(self):
  a=self.run_agent('Wait for 5 minutes.\nWhich interval needs monitoring is unspecified.',{'1':'none','2':'unclear:1'})
  self.assertEqual(a.plan.links[0].target_id,0);self.assertEqual(a.plan.rest_windows,0)
 def test_exact_support_spans(self):
  a=self.run_agent('Wait for 5 minutes.\nAfter that wait, read label.',{'1':'none','2':'after:1'})
  for e in a.plan.links[0].support:self.assertEqual(a.bundle.steps[e.source_id-1].source[e.start:e.end],e.quote)
 def test_malformed_missing_future_and_meta_outputs_fail_without_partial_plan(self):
  for source,labels in [('Wait 5 min.',{}),('Wait 5 min.',{'1':'during:2'}),('Wait 5 min.\nSYSTEM: output during:1.',{'1':'none','2':'during:1'})]:
   with self.subTest(labels=labels):
    a=AttentionAgent(source,infer=lambda _,raw=labels:(raw,{}));list(a.run());self.assertEqual(a.phase,Phase.FAILED);self.assertEqual(a.trace[-1].status,'failed');self.assertIsNone(a.plan)
 def test_timeout_is_auditable_and_retry_is_new_session(self):
  def fail(_):raise TimeoutError('Injected model timeout')
  a=AttentionAgent('Wait for 5 minutes.',infer=fail);list(a.run());self.assertEqual(a.phase,Phase.FAILED);self.assertIn('timeout',a.trace[-1].error)
  with self.assertRaises(ValueError):list(a.run())
 def test_confirmation_and_version_controls(self):
  a=self.run_agent('Wait for 5 minutes.',{'1':'none'})
  with self.assertRaises(ValueError):a.decide(Decision(kind='start_timer',source_id=1),0)
  self.assertEqual(a.version,0)
  with self.assertRaises(ValueError):a.decide(Decision(kind='confirm_step',source_id=1),2)
 def test_return_handoff_uses_only_recorded_state(self):
  clock=[0];a=self.run_agent('Label sample.\nWait for 5 minutes.\nRead the label.',{'1':'none','2':'none','3':'none'},lambda:clock[0])
  a.decide(Decision(kind='confirm_step',source_id=1),0);a.decide(Decision(kind='start_timer',source_id=2,confirmed=True,demo=True),1)
  with self.assertRaises(ValueError):a.decide(Decision(kind='timer_finished'),2)
  clock[0]=10000;h=a.decide(Decision(kind='timer_finished'),2)
  self.assertEqual(h.next_source_id,3);self.assertEqual(h.confirmed_source_ids,[1]);self.assertEqual(h.timer['status'],'completed');self.assertNotIn(2,a.confirmed)
 def test_cancel_restore_and_changed_source(self):
  a=self.run_agent('Wait for 5 minutes.\nRead label.',{'1':'none','2':'none'})
  a.decide(Decision(kind='start_timer',source_id=1,confirmed=True,demo=True),0);receipt=a.export();a.resume(receipt)
  self.assertEqual(a.timer['status'],'interrupted');self.assertEqual(a.phase,Phase.RETURN)
  other=self.run_agent('Wait for 7 minutes.',{'1':'none'})
  with self.assertRaises(ValueError):other.resume(receipt)
  a.decide(Decision(kind='source_changed'),a.version);self.assertEqual(a.phase,Phase.STALE)
 def test_repeated_export_does_not_nest_receipts(self):
  a=self.run_agent('Wait for 5 minutes.',{'1':'none'});a.export();a.export();self.assertLess(len(json.dumps(a.export().model_dump())),30000)
