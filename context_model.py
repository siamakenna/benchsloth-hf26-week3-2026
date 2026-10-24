"""Bounded per-note contexts. Original source IDs are reconstructed after inference.

At most two earlier wait occurrences per semantic note, eight notes and 180 seconds.
No new prompt or weights; never pretend a skipped model call occurred.
"""
import re,time
from attention import infer_semantics,request_for,META
from attention_agent import extract_source_steps,wait_ids
MAX_LINES=12;MAX_NOTES=8;BUDGET_SECONDS=180

def infer_contexts(source):
 start=time.perf_counter();bundle=extract_source_steps(source)
 if len(bundle.steps)>MAX_LINES:raise ValueError('Live Attention Agent currently supports up to 12 nonempty source lines.')
 candidates=[]
 # Use the same candidate selection as the frozen semantic adapter, with a preceding
 # sentinel only to avoid its first-line clamp when inspecting a later source note.
 for note in bundle.steps:
  if note.id==1 or META.search(note.source):continue
  props=request_for('Wait for 1 minutes.\n'+note.source)['format']['properties']['2']['enum']
  if len(props)<=1:continue
  previous=wait_ids(bundle,note.id)
  if not previous:continue
  if len(previous)>2:raise ValueError('More than two earlier waits in a semantic context. Split the source and review the remaining context manually.')
  candidates.append((note,previous))
 if len(candidates)>MAX_NOTES:raise ValueError('Too many semantic notes for this bounded run.')
 labels={str(s.id):'none' for s in bundle.steps};calls=[]
 for note,previous in candidates:
  if time.perf_counter()-start>BUDGET_SECONDS:raise RuntimeError('Attention Agent stopped at its overall model budget; no partial plan accepted.')
  local=[bundle.steps[i-1].source for i in previous]+[note.source]
  raw,evidence=infer_semantics('\n'.join(local));mapping={str(i+1):global_id for i,global_id in enumerate(previous+[note.id])}
  value=raw[str(len(local))]
  if value!='none':
   relation,target=value.split(':');global_target=0 if target=='0' else mapping.get(target)
   if global_target is None or global_target>=note.id:raise ValueError('Context model returned an invalid original-source target.')
   labels[str(note.id)]=f'{relation}:{global_target}'
  calls.append({'source_note_id':note.id,'context_source_ids':previous+[note.id],'local_to_original_ids':mapping,**evidence})
 return labels,{'calls':calls,'combined_labels':labels,'wall_seconds':time.perf_counter()-start,'model_calls':len(calls),'scope':'Actual per-note Gemma calls; original source remains whole. Noncandidate lines receive none without model invention.'}
