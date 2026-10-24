import unittest
from runtime_v5 import AttentionAgent
from agent_v5 import Decision
class Runtime(unittest.TestCase):
 def make(self):
  a=AttentionAgent('# Batch\nWait 5 minutes.\nAfter that wait, label slides.',infer=lambda _:({'1':'none','2':'none','3':'after:2'},{}));list(a.run());return a
 def test_heading_is_not_next_action(self):self.assertEqual(self.make().handoff().next_source_id,2)
 def test_rejected_checkpoint_is_atomic(self):
  a=self.make();a.decide(Decision(kind='reject_link',source_id=3),0);receipt=a.export();receipt.handoff.timer={'source_id':99};b=self.make();before=b.snapshot()
  with self.assertRaises(ValueError):b.resume(receipt)
  self.assertEqual(before,b.snapshot())
 def test_acknowledgements_survive_restore(self):
  a=AttentionAgent('Incubate overnight.',infer=lambda _:({'1':'none'},{}));list(a.run());a.decide(Decision(kind='acknowledge_review',review_id='source-1'),0);r=a.export();b=AttentionAgent(a.source,infer=lambda _:({'1':'none'},{}));list(b.run());b.resume(r);self.assertEqual(b.reviews.items[0].status,'acknowledged')
 def test_timer_structure_and_duration_are_rejected_atomically(self):
  for timer in [{'source_id':2,'source':'Wait 5 minutes.'},{'source_id':2,'source':'Wait 5 minutes.','start_ms':0,'end_ms':1,'duration_ms':1,'status':'completed','demo':False,'elapsed_ms':1}]:
   a=self.make();r=a.export();r.handoff.timer=timer;before=a.snapshot()
   with self.assertRaises(ValueError):a.resume(r)
   self.assertEqual(a.snapshot(),before)
 def test_valid_completed_demo_restore(self):
  clock=[1000];a=AttentionAgent('Wait 5 minutes.',infer=lambda _:({'1':'none'},{}),clock=lambda:clock[0]);list(a.run());a.decide(Decision(kind='start_timer',source_id=1,confirmed=True,demo=True),0);clock[0]+=10000;a.decide(Decision(kind='timer_finished'),1);r=a.export();b=AttentionAgent(a.source,infer=lambda _:({'1':'none'},{}),clock=lambda:clock[0]);list(b.run());b.resume(r);self.assertEqual(b.timer['status'],'completed')
