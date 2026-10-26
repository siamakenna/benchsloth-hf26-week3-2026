"""Session-only usability guards around the frozen evaluated inference policy.

No model/candidate/verifier/timer-eligibility changes. Headings are not next actions;
failed checkpoint restoration is atomic rather than partly mutating a session.
"""
import copy,math
from agent_v5 import AttentionAgent as FrozenAgent,Phase
class AttentionAgent(FrozenAgent):
 def handoff(self):
  h=super().handoff()
  cursor=(self.timer['source_id']+1) if self.phase==Phase.RETURN and self.timer and self.timer['status']=='completed' else 1
  next_step=next((s for s in (self.plan.steps if self.plan and self.phase not in [Phase.FAILED,Phase.STALE] else []) if s.id>=cursor and s.id not in self.confirmed and not s.source.lstrip().startswith('#')),None)
  h.next_source_id=next_step.id if next_step else None;h.next_source=next_step.source if next_step else None
  return h
 def resume(self,receipt):
  before=copy.deepcopy(self.__dict__)
  try:
   t=receipt.handoff.timer
   if t:
    required={'source_id','source','start_ms','end_ms','duration_ms','status','demo'}
    if not required.issubset(t):raise ValueError('Checkpoint timer fields are incomplete')
    if t['status'] not in ['running','completed','interrupted'] or type(t['demo']) is not bool:raise ValueError('Invalid checkpoint timer state')
    for k in ['start_ms','end_ms','duration_ms']:
     if type(t[k]) not in [int,float] or not math.isfinite(t[k]) or t[k]<0:raise ValueError('Invalid checkpoint timer timestamp')
    step=next((s for s in self.plan.steps if s.id==t['source_id']),None)
    if not step or step.rest_minutes is None or step.source!=t['source']:raise ValueError('Checkpoint timer source is not eligible')
    expected=10000 if t['demo'] else int(step.rest_minutes*60000)
    if t['duration_ms']!=expected or t['end_ms']-t['start_ms']!=expected:raise ValueError('Checkpoint duration does not match source/demo interval')
    if 'elapsed_ms' in t and (type(t['elapsed_ms']) not in [int,float] or not math.isfinite(t['elapsed_ms']) or t['elapsed_ms']<0):raise ValueError('Invalid checkpoint elapsed time')
    if t['status']=='completed' and (t.get('elapsed_ms',-1)<expected or self.clock()<t['end_ms']):raise ValueError('Checkpoint interval cannot be completed before its duration')
   for record in receipt.decisions:
    if record.kind=='acknowledge_review':
     item=next((q for q in self.reviews.items if q.id==record.details.get('review_id')),None)
     if not item:raise ValueError('Checkpoint review ID is unknown')
     item.status='acknowledged'
   return super().resume(receipt)
  except Exception:
   self.__dict__.clear();self.__dict__.update(before);raise
