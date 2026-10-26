"""Full-document deterministic agent. Frozen model planners remain unchanged.
Unknown restriction scope blocks timers across the document, never just a chunk.
"""
import re
from runtime_v5 import AttentionAgent as SessionAgent
from agent_v5 import SourceBundle,SourceStep,Phase,AttentionPlan,PlanStep,Verification,Association,prepare_review_queue,Handoff
from app import fixed_duration,timer_source_check
from document_v8 import document,wait_classification,MONITOR,RESTRICT,CONDITION,WAIT
from source_review_v8 import review_cues
class AttentionAgent(SessionAgent):
 def run(self):
  if self.phase!=Phase.EMPTY:raise ValueError('This source run already started.')
  self.phase=Phase.ANALYZING;d=document(self.source);rows=d['rows'];ids=[r['id']for r in rows]
  self.bundle=self.tool('extract_full_document',lambda:SourceBundle(source_hash=d['source_hash'],steps=[SourceStep(**{k:r[k]for k in ['id','source','start','end']})for r in rows]),SourceBundle,ids);yield self.trace[-1]
  self.classifications=[wait_classification(r,rows)for r in rows]
  # A lexical restriction does not establish its scope. Keep all waits held until
  # scope is reviewed; acknowledgement/correction never loosens this gate.
  blockers=[r['id']for r in rows if not r['is_heading'] and (RESTRICT.search(r['source'])or MONITOR.search(r['source'])or CONDITION.search(r['source'])or '?' in r['source']or review_cues(r['source']))]
  links=[];unresolved_context={}
  for row,c in zip(rows,self.classifications):
   ref=c['reference']
   if not ref['ids'] and not ref['missing']:
    if re.search(r'\b(?:during|after|before|throughout)\b',row['source'],re.I)and re.search(r'\b(?:wait|interval|hold|incubation)\b',row['source'],re.I):
     candidates=[r['id']for r in rows if r['id']<row['id']and WAIT.search(r['source'])and not r['is_heading']]
     if candidates:unresolved_context[row['id']]=candidates
     else:continue
    else:continue
   temporal=[key for key in ['before','during','after']if re.search(r'\b'+key+r'\b',row['source'],re.I)]
   # Only an explicit complete-document reference and single literal phase are
   # represented. Cross-section implicit proximity is never an accepted link.
   target=ref['ids'][0] if ref['resolved'] and len(ref['ids'])==1 and len(temporal)==1 and temporal[0]!='before' else 0
   relation=temporal[0] if target else 'unclear'
   links.append(Association(note_id=row['id'],target_id=target,relation=relation,source=row['source'],target_source=rows[target-1]['source']if target else None,proposed=f'{relation}:{target}',validation='verified'if target else 'unresolved',support=[],reason=ref['basis']+'. Literal reference only; scientific dependency not inferred.'))
  self.tool('resolve_global_source_references',lambda:Verification(labels={},links=links),Verification,ids);yield self.trace[-1]
  steps=[]
  for r,c in zip(rows,self.classifications):
   minutes,reason=fixed_duration(r['source']);eligible,admission=timer_source_check(r['source']);rest=minutes if eligible and not blockers and minutes is not None else None
   review=not r['is_heading'] and bool(c['classes']or review_cues(r['source'])or c['reference']['ids']or c['reference']['missing'])
   if minutes is not None and eligible and blockers:reason='Unresolved document restriction scope at source IDs '+', '.join(map(str,blockers))+'. No timer permission inferred.'
   elif rest is None:reason=reason+'; '+admission
   steps.append(PlanStep(id=r['id'],source=r['source'],label=' '.join(r['source'].split()[:10]),kind='note'if r['is_heading']else 'hands_off'if rest is not None else 'review'if review else 'hands_on',fixed_minutes=minutes,rest_minutes=rest,rule_supported=bool(eligible),review_needed=review,reason=reason,evidence=[a for a in links if a.note_id==r['id']or a.target_id==r['id']]))
  self.plan=self.tool('build_full_source_attention_map',lambda:AttentionPlan(steps=steps,links=links,rest_windows=sum(s.rest_minutes is not None for s in steps),documented_rest_minutes=sum(s.rest_minutes or 0 for s in steps),review_needed=sum(s.review_needed for s in steps),engine='Deterministic full-document source plan',mode='source-plan',protocol=self.source),AttentionPlan,ids);yield self.trace[-1]
  self.reviews=prepare_review_queue(self.plan)
  for item in self.reviews.items:
   candidates=unresolved_context.get(item.source_ids[0],[])
   if candidates:
    item.source_ids=list(dict.fromkeys(item.source_ids+candidates));item.passages=[rows[i-1]['source']for i in item.source_ids];item.reason='Cross-section or implicit target unresolved. Earlier original wait occurrences are inspection candidates only; no scope or dependency inferred.';item.proposal='No accepted association; inspect original IDs '+', '.join(map(str,candidates))
  self.document=d;self.raw_evidence={'model_calls':0,'coverage':[],'source_hash':d['source_hash'],'retained_occurrences':len(rows),'omitted_occurrences':0,'unresolved_restriction_ids':blockers,'wait_classification':self.classifications,'unresolved_reference_candidates':unresolved_context};self.phase=Phase.REVIEW
  self.tool('generate_handoff',self.handoff,Handoff,ids);yield self.trace[-1]
 def handoff(self):
  h=super().handoff()
  if getattr(self,'document',None) and h.next_source_id:
   headings={r['id']for r in self.document['rows']if r['is_heading']}
   cursor=h.next_source_id
   next_step=next((s for s in self.plan.steps if s.id>=cursor and s.id not in headings and s.id not in self.confirmed),None)
   h.next_source_id=next_step.id if next_step else None;h.next_source=next_step.source if next_step else None
  return h
