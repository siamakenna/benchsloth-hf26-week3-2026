"""Bounded Attention Agent: typed tools, source verification and auditable state.

Orchestration is explicit Python, not an unconstrained model planner. Gemma proposes
relations only. The agent never executes experiments or starts timers autonomously.
"""
from __future__ import annotations
from datetime import datetime,timezone
from enum import Enum
import hashlib,re,time,uuid
from typing import Any,Literal,Callable
from pydantic import BaseModel,ConfigDict,Field
from app import input_lines,fixed_duration,timer_source_check,MODEL
from association_v5 import infer_pairs, candidate_rows, structure, AFTER as V5_AFTER
from attention import infer_semantics,validate_links,baseline_links,WAITISH,META

class Contract(BaseModel):
    model_config=ConfigDict(extra='forbid')
class SourceStep(Contract):
    id:int;source:str;start:int;end:int
class SourceBundle(Contract):
    source_hash:str;steps:list[SourceStep]
class DurationStep(Contract):
    id:int;minutes:float|None;eligible:bool;reason:str
class DurationBundle(Contract):
    steps:list[DurationStep]
class Proposal(Contract):
    labels:dict[str,str];model:str
class Span(Contract):
    source_id:int;start:int;end:int;quote:str
class Association(Contract):
    note_id:int;target_id:int;relation:Literal['during','after','unclear'];source:str;target_source:str|None
    proposed:str;validation:Literal['verified','source-corrected','unresolved','rejected','user-corrected','user-rejected'];support:list[Span];reason:str
class Verification(Contract):
    labels:dict[str,str];links:list[Association]
class Restriction(Contract):
    note_id:int;target_ids:list[int];reason:str;support:list[Span]
class Conflicts(Contract):
    restrictions:list[Restriction]
class PlanStep(Contract):
    id:int;source:str;label:str;kind:Literal['hands_off','hands_on','note','review'];fixed_minutes:float|None;rest_minutes:float|None
    rule_supported:bool;review_needed:bool;reason:str;evidence:list[Association]
class AttentionPlan(Contract):
    steps:list[PlanStep];links:list[Association];rest_windows:int;documented_rest_minutes:float;review_needed:int;engine:str;mode:str;protocol:str
class ReviewItem(Contract):
    id:str;source_ids:list[int];question:str;status:Literal['pending','acknowledged']='pending'
    priority:int=5;reason:str='Source review';impact:str='Display only; no permission to change source timing.';proposal:str='No accepted association';passages:list[str]=Field(default_factory=list)
class ReviewQueue(Contract):
    items:list[ReviewItem]
class Handoff(Contract):
    message:str;next_source_id:int|None;next_source:str|None;confirmed_source_ids:list[int];pending_reviews:list[ReviewItem];timer:dict[str,Any]|None
    observed_activity:str='Only browser/user decisions were recorded; no physical experiment was observed.'
    changes:list[dict]=Field(default_factory=list)
class TraceEvent(Contract):
    seq:int;tool:str;status:Literal['completed','failed'];source_ids:list[int];elapsed_ms:float;result:dict[str,Any];error:str|None=None
class Phase(str,Enum):
    EMPTY='empty';ANALYZING='analyzing';REVIEW='ready-for-review';RUNNING='timer-running';RETURN='return-handoff';FAILED='failed';STALE='stale'
class Decision(Contract):
    kind:Literal['confirm_step','reopen_step','acknowledge_review','start_timer','timer_finished','cancel_timer','source_changed','correct_link','reject_link']
    source_id:int|None=None;review_id:str|None=None;confirmed:bool=False;demo:bool=False
    target_id:int|None=None;relation:Literal['after','during','unclear']|None=None
class DecisionRecord(Contract):
    version:int;kind:str;source_id:int|None;at_ms:int;details:dict[str,Any]
class Receipt(Contract):
    version:int;source_hash:str;phase:str;source_steps:list[SourceStep];decisions:list[DecisionRecord];trace:list[TraceEvent];handoff:Handoff

AFTER_CUE=re.compile(r'\bafter\b|\bonce\b.{0,65}\b(?:ends?|finishe[sd]?)\b|\bwhen\b.{0,65}\b(?:over|ends?|finishe[sd]?)\b',re.I)
DURING_CUE=re.compile(r'\b(?:during|throughout|while|halfway|midpoint|continuously)\b',re.I)
ATTENTION_CUE=re.compile(r'\b(?:watch\w*|observ\w*|monitor\w*|inspect\w*|check\w*|attention|invert\w*|keep an eye)\b',re.I)
UNCLEAR_CUE=re.compile(r'\b(?:provisional|unconfirmed|not been confirmed|uncertain|conflict\w*|placeholder|may be revised|unspecified|does not say which|does not identify|cannot be determined)\b',re.I)
UNRESOLVED_CUE=re.compile(r'which.{0,60}(?:unspecified|unclear)|does not (?:say which|identify)|cannot be determined|one of these',re.I)

AFTER_CUE=V5_AFTER

def digest(source:str)->str:return hashlib.sha256(source.encode()).hexdigest()
def extract_source_steps(source:str)->SourceBundle:
    expected=input_lines(source);steps=[];offset=0
    for line in source.splitlines(keepends=True):
        clean=line.strip()
        if clean:
            start=offset+line.index(clean);steps.append(SourceStep(id=len(steps)+1,source=clean,start=start,end=start+len(clean)))
        offset+=len(line)
    assert [s.source for s in steps]==expected
    return SourceBundle(source_hash=digest(source),steps=steps)
def parse_explicit_durations(bundle:SourceBundle)->DurationBundle:
    rows=[]
    for s in bundle.steps:
        m,reason=fixed_duration(s.source);eligible,_=timer_source_check(s.source)
        rows.append(DurationStep(id=s.id,minutes=m,eligible=bool(eligible and m is not None),reason=reason))
    return DurationBundle(steps=rows)
def spans(step:SourceStep,pattern:re.Pattern)->list[Span]:
    return [Span(source_id=step.id,start=m.start(),end=m.end(),quote=m.group()) for m in pattern.finditer(step.source)]
def wait_ids(bundle:SourceBundle,before:int|None=None)->list[int]:
    return [s.id for s in bundle.steps if (before is None or s.id<before) and WAITISH.search(s.source) and not META.search(s.source)
            and not AFTER_CUE.search(s.source) and not ATTENTION_CUE.search(s.source)]
def explicit_target(note:str,ids:list[int])->int|None:
    if re.search(r'\bfirst\b',note,re.I):return ids[0] if ids else None
    if re.search(r'\bsecond\b',note,re.I):return ids[1] if len(ids)>1 else None
    return ids[0] if len(ids)==1 else None

def verify_source_links(bundle:SourceBundle,proposal:Proposal)->Verification:
    # Structural validation is still fail closed, before any semantic repair.
    validate_links('\n'.join(s.source for s in bundle.steps),proposal.labels)
    out={str(s.id):'none' for s in bundle.steps};links=[]
    for key,value in proposal.labels.items():
        if value=='none':continue
        note=bundle.steps[int(key)-1];relation,target=value.split(':');target=int(target);original=relation
        after=bool(AFTER_CUE.search(note.source));during=bool(DURING_CUE.search(note.source));unclear=bool(UNCLEAR_CUE.search(note.source))
        row=next((r for r in candidate_rows('\n'.join(s.source for s in bundle.steps)) if r['note_id']==note.id),None)
        unresolved=bool(UNRESOLVED_CUE.search(note.source)) or bool(row and row['target_id'] is None);ids=wait_ids(bundle,note.id);explicit=row['target_id'] if row else explicit_target(note.source,ids)
        state='verified';reason='Literal temporal support and valid source occurrence.'
        if unresolved:
            relation,target='unclear',0;state='unresolved';reason='Source explicitly leaves target identity unresolved.'
        elif unclear:
            relation='unclear'
            if relation!=original:state='source-corrected';reason='Source states uncertainty; proposed relation was not supported.'
        elif after and not during:
            relation='after'
            if original!='after':state='source-corrected';reason='Explicit after-interval wording contradicts proposed relation.'
        elif not (during or ATTENTION_CUE.search(note.source)) and relation=='during':
            state='rejected';reason='No literal attention-during support; keep as a review question.'
        elif relation=='after' and not after:
            state='rejected';reason='No explicit after-interval support.'
        elif relation=='unclear' and not unclear and not unresolved:
            state='rejected';reason='No source uncertainty cue supports this proposal.'
        if target and (target not in ids or (explicit is not None and target!=explicit)):
            state='rejected';reason='Target is not an earlier wait, or conflicts with an explicit ordinal reference.'
        if target and explicit is None and len(ids)>1:
            state='rejected';reason='Multiple earlier waits; target remains a proposed interpretation requiring review.'
        support=spans(note,UNCLEAR_CUE if relation=='unclear' else AFTER_CUE if relation=='after' else DURING_CUE)
        if not support:support=spans(note,ATTENTION_CUE)
        for span in support:assert note.source[span.start:span.end]==span.quote
        a=Association(note_id=note.id,target_id=target,relation=relation,source=note.source,target_source=bundle.steps[target-1].source if target else None,
            proposed=value,validation=state,support=support,reason=reason);links.append(a)
        if state!='rejected':out[key]=f'{relation}:{target}'
    return Verification(labels=out,links=sorted(links,key=lambda a:a.note_id))

def detect_conflicts(bundle:SourceBundle)->Conflicts:
    restrictions=[];all_waits=wait_ids(bundle)
    for note in bundle.steps:
        if META.search(note.source):continue
        unclear=bool(UNCLEAR_CUE.search(note.source));during=bool(DURING_CUE.search(note.source));attention=bool(ATTENTION_CUE.search(note.source));after=bool(AFTER_CUE.search(note.source))
        row=next((r for r in candidate_rows('\n'.join(s.source for s in bundle.steps)) if r['note_id']==note.id),None)
        genuine=unclear or (attention and not (after and not during)) or bool(row and row['target_id'] is None)
        if not genuine:continue
        previous=wait_ids(bundle,note.id);row=next((r for r in candidate_rows('\n'.join(s.source for s in bundle.steps)) if r['note_id']==note.id),None);target=row['target_id'] if row else explicit_target(note.source,previous)
        ids=[target] if target is not None and not UNRESOLVED_CUE.search(note.source) else all_waits
        restrictions.append(Restriction(note_id=note.id,target_ids=ids,reason='Source timing is unresolved.' if unclear else 'Source requires operator attention during an interval.',support=spans(note,UNCLEAR_CUE if unclear else ATTENTION_CUE)))
    return Conflicts(restrictions=restrictions)

def build_attention_map(source:str,bundle:SourceBundle,durations:DurationBundle,verified:Verification,conflicts:Conflicts,mode:str='inference')->AttentionPlan:
    blocked={i for r in conflicts.restrictions for i in r.target_ids};restriction_notes={r.note_id for r in conflicts.restrictions};steps=[]
    warnings={a.note_id for a in verified.links if a.validation!='verified'}
    for s,d in zip(bundle.steps,durations.steps):
        rest=d.minutes if d.eligible and s.id not in blocked else None
        timing=bool(WAITISH.search(s.source) and not AFTER_CUE.search(s.source) and not META.search(s.source))
        review=s.id in blocked or s.id in restriction_notes or s.id in warnings or (timing and not d.eligible)
        reason='Source restriction: '+', '.join(str(r.note_id) for r in conflicts.restrictions if s.id in r.target_ids) if s.id in blocked else d.reason
        if s.id in warnings:reason='Proposed association requires human review; it does not change source-supported timing.'
        evidence=[a for a in verified.links if a.note_id==s.id or a.target_id==s.id]
        steps.append(PlanStep(id=s.id,source=s.source,label=' '.join(s.source.split()[:10]),kind='hands_off' if rest is not None else 'review' if review else 'note' if re.match(r'^(?:#|notes?|preparation|SYSTEM)',s.source,re.I) else 'hands_on',fixed_minutes=d.minutes,rest_minutes=rest,rule_supported=d.eligible,review_needed=review,reason=reason,evidence=evidence))
    return AttentionPlan(steps=steps,links=verified.links,rest_windows=sum(s.rest_minutes is not None for s in steps),documented_rest_minutes=sum(s.rest_minutes or 0 for s in steps),review_needed=sum(s.review_needed for s in steps),engine='Local Gemma / '+MODEL+' · bounded Attention Agent',mode=mode,protocol=source)

def prepare_review_queue(plan:AttentionPlan)->ReviewQueue:
    items=[]
    for s in plan.steps:
        if not s.review_needed:continue
        monitoring=bool(ATTENTION_CUE.search(s.source) and not AFTER_CUE.search(s.source));conflict=bool(UNCLEAR_CUE.search(s.source))
        priority=1 if monitoring else 2 if conflict else 3 if s.evidence else 4 if s.fixed_minutes is None and WAITISH.search(s.source) else 5
        links=[a for a in s.evidence if a.note_id==s.id]
        passages=list(dict.fromkeys([s.source]+[a.target_source for a in links if a.target_source]))
        items.append(ReviewItem(id=f'source-{s.id}',source_ids=list(dict.fromkeys([s.id]+[a.target_id for a in links if a.target_id])),question=f'Review source {s.id}: “{s.source}”',priority=priority,reason=s.reason,impact='Source restrictions govern timer eligibility; association correction changes interpretation/display only.',proposal='; '.join(a.proposed+' / '+a.validation for a in links) or 'No accepted association',passages=passages))
    return ReviewQueue(items=sorted(items,key=lambda r:(r.priority,r.source_ids[0])))

class AttentionAgent:
    def __init__(self,source:str,mode='inference',infer:Callable= infer_pairs,clock:Callable=lambda:int(time.time()*1000)):
        self.id=str(uuid.uuid4());self.source=source;self.source_hash=digest(source);self.mode=mode;self.infer=infer;self.clock=clock
        self.phase=Phase.EMPTY;self.version=0;self.trace=[];self.decisions=[];self.confirmed=[];self.timer=None;self.reviews=ReviewQueue(items=[]);self.plan=None;self.bundle=None;self.raw_evidence=None
    def tool(self,name:str,fn:Callable,contract:type[Contract],ids:list[int])->Contract:
        started=time.perf_counter()
        try:
            raw=fn();result=contract.model_validate(raw.model_dump() if isinstance(raw,BaseModel) else raw)
            event=TraceEvent(seq=len(self.trace)+1,tool=name,status='completed',source_ids=ids,elapsed_ms=round((time.perf_counter()-started)*1000,3),result=({'version':result.version,'source_hash':result.source_hash,'trace_count':len(result.trace),'decision_count':len(result.decisions)} if isinstance(result,Receipt) else result.model_dump(mode='json')))
        except Exception as e:
            self.trace.append(TraceEvent(seq=len(self.trace)+1,tool=name,status='failed',source_ids=ids,elapsed_ms=round((time.perf_counter()-started)*1000,3),result={},error=str(e)))
            self.phase=Phase.FAILED;raise
        self.trace.append(event);return result
    def run(self):
        if self.phase!=Phase.EMPTY:raise ValueError('This run already started; create a new session to retry.')
        self.phase=Phase.ANALYZING
        try:
            self.bundle=self.tool('extract_source_steps',lambda:extract_source_steps(self.source),SourceBundle,[]);yield self.trace[-1]
            ids=[s.id for s in self.bundle.steps]
            durations=self.tool('parse_explicit_durations',lambda:parse_explicit_durations(self.bundle),DurationBundle,ids);yield self.trace[-1]
            def propose():
                labels,evidence=self.infer(self.source);self.raw_evidence=evidence;return Proposal(labels=labels,model=MODEL if evidence.get('calls') or evidence.get('response') else 'Source-only abstention / no model call')
            proposal=self.tool('propose_temporal_links',propose,Proposal,ids);yield self.trace[-1]
            def verify():
                result=verify_source_links(self.bundle,proposal)
                for c in (self.raw_evidence or {}).get('coverage',[]):
                    if c['outcome']!='model-abstention':continue
                    note=self.bundle.steps[c['note_id']-1]
                    result.links.append(Association(note_id=note.id,target_id=0,relation='unclear',source=note.source,target_source=None,proposed='none',validation='unresolved',support=[],reason='Focused model abstained on a temporal candidate. Review required; no link invented.'))
                return result
            verified=self.tool('verify_source_links',verify,Verification,ids);yield self.trace[-1]
            conflicts=self.tool('detect_conflicts',lambda:detect_conflicts(self.bundle),Conflicts,ids);yield self.trace[-1]
            self.plan=self.tool('build_attention_map',lambda:build_attention_map(self.source,self.bundle,durations,verified,conflicts,self.mode),AttentionPlan,ids);yield self.trace[-1]
            self.reviews=self.tool('prepare_review_queue',lambda:prepare_review_queue(self.plan),ReviewQueue,[s.id for s in self.plan.steps if s.review_needed]);yield self.trace[-1]
            self.phase=Phase.REVIEW
            self.tool('generate_handoff',self.handoff,Handoff,ids);yield self.trace[-1]
        except Exception:
            yield self.trace[-1]
    def handoff(self)->Handoff:
        cursor=(self.timer['source_id']+1) if self.phase==Phase.RETURN and self.timer and self.timer['status']=='completed' else 1
        next_step=next((s for s in (self.plan.steps if self.plan and self.phase not in [Phase.FAILED,Phase.STALE] else []) if s.id>=cursor and s.id not in self.confirmed),None)
        return Handoff(message="Welcome back. Here’s where you left off." if self.phase==Phase.RETURN else 'Ready for your source review.',next_source_id=next_step.id if next_step else None,next_source=next_step.source if next_step else None,confirmed_source_ids=list(self.confirmed),pending_reviews=[i for i in self.reviews.items if i.status=='pending'],timer=self.timer,changes=[d.model_dump() for d in self.decisions[-5:]])
    def decide(self,decision:Decision,expected_version:int)->Handoff:
        if expected_version!=self.version:raise ValueError('Stale session version; refresh the checkpoint before deciding.')
        if self.phase in [Phase.FAILED,Phase.STALE,Phase.EMPTY,Phase.ANALYZING]:raise ValueError('Session is not ready for decisions.')
        ids={s.id for s in self.plan.steps}
        if decision.source_id is not None and decision.source_id not in ids:raise ValueError('Unknown source occurrence')
        now=self.clock();kind=decision.kind
        if kind in ['confirm_step','reopen_step']:
            if decision.source_id is None:raise ValueError('Source ID required')
            if kind=='confirm_step' and decision.source_id not in self.confirmed:self.confirmed.append(decision.source_id)
            if kind=='reopen_step' and decision.source_id in self.confirmed:self.confirmed.remove(decision.source_id)
        elif kind=='acknowledge_review':
            item=next((r for r in self.reviews.items if r.id==decision.review_id),None)
            if not item:raise ValueError('Unknown review item')
            item.status='acknowledged'
        elif kind=='start_timer':
            if not decision.confirmed:raise ValueError('Explicit source confirmation required')
            if self.timer and self.timer['status']=='running':raise ValueError('Cancel the running timer first')
            s=next((s for s in self.plan.steps if s.id==decision.source_id),None)
            if not s or s.rest_minutes is None or s.id in self.confirmed:raise ValueError('This source is not timer eligible')
            duration=10000 if decision.demo else int(s.rest_minutes*60000)
            self.timer=dict(source_id=s.id,source=s.source,start_ms=now,end_ms=now+duration,duration_ms=duration,status='running',demo=decision.demo)
            self.phase=Phase.RUNNING
        elif kind in ['timer_finished','cancel_timer']:
            if not self.timer or self.timer['status']!='running':raise ValueError('No running timer')
            if kind=='timer_finished' and now<self.timer['end_ms']:raise ValueError('Source interval has not elapsed')
            self.timer['status']='completed' if kind=='timer_finished' else 'interrupted';self.timer['elapsed_ms']=max(0,now-self.timer['start_ms']);self.phase=Phase.RETURN
        elif kind in ['correct_link','reject_link']:
            if decision.source_id is None:raise ValueError('Source note ID required')
            if self.timer and self.timer['status']=='running':raise ValueError('Stop the running interval before correcting associations')
            note=self.bundle.steps[decision.source_id-1];old=[a.model_dump() for a in self.plan.links if a.note_id==note.id]
            if kind=='correct_link':
                if not decision.relation or decision.target_id not in wait_ids(self.bundle,note.id):raise ValueError('Choose an earlier original wait and a relation')
                target=self.bundle.steps[decision.target_id-1]
                replacement=Association(note_id=note.id,target_id=target.id,relation=decision.relation,source=note.source,target_source=target.source,proposed=f'{decision.relation}:{target.id}',validation='user-corrected',support=[],reason='User interpretation recorded; original source and timer restrictions unchanged.')
                self.plan.links=[a for a in self.plan.links if a.note_id!=note.id]+[replacement]
            else:
                for a in self.plan.links:
                    if a.note_id==note.id:a.validation='user-rejected';a.reason='User rejected this interpretation; source and timer restrictions unchanged.'
            for step in self.plan.steps:step.evidence=[a for a in self.plan.links if a.note_id==step.id or a.target_id==step.id]
            for review in self.reviews.items:
                if review.id==f'source-{note.id}':review.status='acknowledged'
            self.timer=None;self.phase=Phase.REVIEW
            self.recorded_correction={'previous':old,'updated':[a.model_dump() for a in self.plan.links if a.note_id==note.id]}
        elif kind=='source_changed':self.phase=Phase.STALE;self.timer=None
        self.version+=1;self.decisions.append(DecisionRecord(version=self.version,kind=kind,source_id=decision.source_id,at_ms=now,details={**decision.model_dump(),**(getattr(self,'recorded_correction',{}) if kind in ['correct_link','reject_link'] else {})}))
        h=self.tool('record_user_decision',self.handoff,Handoff,[decision.source_id] if decision.source_id else [])
        if kind in ['timer_finished','cancel_timer']:self.tool('generate_handoff',self.handoff,Handoff,ids=list(ids))
        return h
    def export(self)->Receipt:
        if not self.plan or not self.bundle or self.phase==Phase.FAILED:raise ValueError('No complete plan to export')
        return self.tool('export_session_receipt',lambda:Receipt(version=self.version,source_hash=self.source_hash,phase=self.phase.value,source_steps=self.bundle.steps,decisions=self.decisions,trace=list(self.trace),handoff=self.handoff()),Receipt,[s.id for s in self.bundle.steps])
    def snapshot(self)->dict:
        return dict(id=self.id,version=self.version,source_hash=self.source_hash,phase=self.phase.value,plan=self.plan.model_dump() if self.plan and self.phase not in [Phase.FAILED,Phase.STALE] else None,trace=[e.model_dump() for e in self.trace],reviews=self.reviews.model_dump(),confirmed=list(self.confirmed),timer=self.timer,handoff=self.handoff().model_dump())
    def resume(self,receipt:Receipt)->Handoff:
        if receipt.source_hash!=self.source_hash:raise ValueError('Checkpoint belongs to changed source')
        if not self.plan:raise ValueError('Analyze the same source before restoring decisions')
        if [s.model_dump() for s in receipt.source_steps]!=[s.model_dump() for s in self.bundle.steps]:raise ValueError('Checkpoint original passages differ')
        for record in receipt.decisions:
            if record.kind in ['correct_link','reject_link']:
                self.decide(Decision(**{k:v for k,v in record.details.items() if k in Decision.model_fields}),self.version)
        if receipt.handoff.timer:
            t=receipt.handoff.timer;step=next((s for s in self.plan.steps if s.id==t.get('source_id')),None)
            if not step or step.rest_minutes is None or t.get('source')!=step.source:raise ValueError('Checkpoint timer source is not eligible')
        confirmed=list(receipt.handoff.confirmed_source_ids)
        if any(i not in [s.id for s in self.plan.steps] for i in confirmed):raise ValueError('Checkpoint source ID mismatch')
        self.confirmed=confirmed
        self.timer=dict(receipt.handoff.timer) if receipt.handoff.timer else None
        if self.timer and self.timer['status']=='running':self.timer['status']='interrupted';self.timer['elapsed_ms']=max(0,self.clock()-self.timer['start_ms'])
        self.decisions=list(receipt.decisions);self.version=max(self.version,receipt.version)+1;self.phase=Phase.RETURN
        return self.tool('resume_from_checkpoint',self.handoff,Handoff,[s.id for s in self.plan.steps])

TOOL_CONTRACTS={name:cls.model_json_schema() for name,cls in [('extract_source_steps',SourceBundle),('parse_explicit_durations',DurationBundle),('propose_temporal_links',Proposal),('verify_source_links',Verification),('detect_conflicts',Conflicts),('build_attention_map',AttentionPlan),('prepare_review_queue',ReviewQueue),('generate_handoff',Handoff),('record_user_decision',Handoff),('resume_from_checkpoint',Handoff),('export_session_receipt',Receipt)]}
