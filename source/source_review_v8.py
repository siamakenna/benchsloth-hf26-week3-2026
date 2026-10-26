"""Literal review cues for source-only plans; never resolve scientific conditions.
Frozen model experiments and source/timer admission grammars stay unchanged.
"""
import re
from agent_v5 import ReviewItem
QUESTION=re.compile(r'\?|\bquestion\s*:',re.I)
CONDITION=re.compile(r'\b(if|unless|optional|either|prior to|before|until)\b',re.I)
CAVEAT=re.compile(r'\b(?:not (?:been )?(?:fully )?(?:verified|tested|confirmed)|has not been|have not (?:fully )?(?:verified|tested|confirmed)|unknown|unspecified)\b',re.I)
RESTRICTION=re.compile(r'\b(?:must|never|do not|don.t|avoid|keep|kept|fresh|ice.cold|pre.chilled|continuously|unattended)\b',re.I)
def review_cues(source):
 flags=[]
 if QUESTION.search(source):flags.append('Explicit source question: remains unanswered')
 if CONDITION.search(source):flags.append('Conditional / ordering wording: scope needs human review')
 if CAVEAT.search(source):flags.append('Explicit verification caveat: not established by this tool')
 if RESTRICTION.search(source):flags.append('Explicit handling / restriction wording: retain original constraint')
 return flags

def apply_source_review_guards(agent):
 """Only downgrade or expose review state, preserving exact IDs and source words."""
 flags=[]
 for step in agent.plan.steps:
  cues=review_cues(step.source)
  if not cues:continue
  flags.append(dict(source_id=step.id,cues=cues,authority='literal deterministic review cue',semantic_scope_resolved=False,timer_authority=False))
  step.review_needed=True;step.rest_minutes=None;step.kind='review';step.reason='; '.join(cues)+'. Inspect the original; no scientific answer inferred.'
  if not any(step.id in r.source_ids for r in agent.reviews.items):
   agent.reviews.items.append(ReviewItem(id='v8-literal-source-'+str(step.id),source_ids=[step.id],question='Review the original question, condition or restriction at source '+str(step.id)+'. No answer or dependency has been inferred.',reason='; '.join(cues),priority=1,impact='Organizer review only. Critical restrictions and timer authority are unchanged.',proposal='No scientific interpretation accepted',passages=[step.source]))
 agent.plan.rest_windows=sum(s.rest_minutes is not None for s in agent.plan.steps)
 agent.plan.documented_rest_minutes=sum(s.rest_minutes or 0 for s in agent.plan.steps)
 agent.plan.review_needed=sum(s.review_needed for s in agent.plan.steps)
 return flags
