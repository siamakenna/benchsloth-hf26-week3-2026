/* No inference service is exposed by the static replay. Recorded answers carry
   the complete request/response and exact original source binding. */
let qaRecords={},qaEpoch=0,qaController=null;
const qaNode=(tag,value,cls)=>{const n=document.createElement(tag);if(value!==undefined)n.textContent=value;if(cls)n.className=cls;return n};
function clearQA(reason){qaEpoch++;qaController?.abort();qaController=null;const n=el('askAnswer');n.hidden=true;n.replaceChildren();el('askProgress').textContent=reason||'';el('askSubmit').disabled=false;}
function renderQA(record,origin){
 const root=el('askAnswer');root.hidden=false;root.replaceChildren();const a=record.answer;
 root.append(qaNode('span',origin+(a.route==='deterministic-retrieval'?' / deterministic source answer':''),'ask-mode'));
 root.append(qaNode('h3',record.question));
 root.append(qaNode('span',a.route==='gemma-relationship-selection'?'EXPERIMENTAL PROPOSAL / REVIEW REQUIRED':a.status==='answer'?'EVIDENCE SELECTED':a.status==='ambiguous'?'REVIEW REQUIRED':'NO ACCEPTED ANSWER','answer-status'+(a.status!=='answer'||a.route==='gemma-relationship-selection'?' review':'')));
 root.append(qaNode('p',a.answer));if(a.route==='gemma-relationship-selection')root.append(qaNode('p','This relationship layer did not establish an accuracy advantage over strong retrieval. Inspect the sources; no semantic proposal is automatically accepted into your plan.','qa-stale'));
 if(a.ambiguity)root.append(qaNode('p',a.ambiguity));
 for(const c of a.citations||[]){const block=qaNode('div',undefined,'ask-citation');block.append(qaNode('span','ORIGINAL SOURCE '+c.id,'micro'));block.append(qaNode('blockquote',c.excerpt));const b=qaNode('button','Open source '+c.id+' ↗','text-link');b.onclick=()=>{select(c.id,true);el('source-'+c.id)?.scrollIntoView({block:'center'})};block.append(b);root.append(block)}
 if(a.association){const l=a.association;root.append(qaNode('p','Proposed relationship: source '+l.note_id+' → '+(l.target_id?'source '+l.target_id:'unresolved target')+' / '+l.relation+'. This does not change the Attention Map.','caption'))}
 if(a.state_facts&&Object.keys(a.state_facts).length){root.append(qaNode('span','RECORDED SESSION FACTS','micro'));root.append(qaNode('pre',JSON.stringify(a.state_facts,null,2)))}
 root.append(qaNode('span','MODEL INTERPRETATION / READ ONLY','micro'));root.append(qaNode('p',a.interpretation));
 if(!a.verification.accepted)root.append(qaNode('p','Rejected: '+a.verification.reasons.join(' '),'qa-stale'));
 root.append(qaNode('p','Evidence identity checked. Semantic correctness still needs your review. '+Number(record.seconds||0).toFixed(2)+' s actual recorded request.','caption'));
 const review=qaNode('button','Open human review ↗','text-link');review.onclick=()=>scene('review');root.append(review);
 const details=document.createElement('details'),summary=qaNode('summary','Inspect real request, response & verification');details.append(summary,qaNode('pre',JSON.stringify(record,null,2)));root.append(details);
 root.dataset.epoch=qaEpoch;
}
function currentQA(){
 clearQA();const live=state.result?.mode==='inference';el('askMode').textContent=live?'Live Gemma inference · local only':'Recorded Gemma output · no new inference';el('askForm').hidden=!live;el('askPrompts').replaceChildren();
 const records=(qaRecords[selectedScenario]||[]).filter(r=>r.source_hash===state.session?.source_hash);
 if(!state.result){el('askMode').textContent='Load or analyze a source';return}
 if(!live){
  for(const r of records){const b=qaNode('button',r.question,'ask-prompt');b.setAttribute('aria-pressed','false');b.onclick=()=>{for(const n of el('askPrompts').children)n.setAttribute('aria-pressed','false');b.setAttribute('aria-pressed','true');renderQA(r,'Recorded Gemma output · captured local inference')};el('askPrompts').append(b)}
  if(!records.length)el('askProgress').textContent='No recorded questions match this source. Current session handoff remains available below.';
 }else{
  for(const q of ['Which instruction needs attention after this wait?','What is uncertain or missing?','What should I look at when I return?']){const b=qaNode('button',q,'ask-prompt');b.onclick=()=>{el('askQuestion').value=q;el('askQuestion').focus()};el('askPrompts').append(b)}
 }
}
el('askForm').onsubmit=async e=>{
 e.preventDefault();if(state.result?.mode!=='inference')return;const question=el('askQuestion').value.trim();if(!question)return;
 clearQA();const epoch=qaEpoch,revision=state.revision,version=state.session.version,id=state.session.id;qaController=new AbortController();el('askSubmit').disabled=true;const start=Date.now();const tick=setInterval(()=>{if(epoch===qaEpoch)el('askProgress').textContent='Selecting evidence with local Gemma · '+((Date.now()-start)/1000).toFixed(1)+' s elapsed'},100);
 try{const response=await fetch('/api/agent/session/'+id+'/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expected_version:version,question}),signal:qaController.signal});const r=await response.json();if(!response.ok)throw Error(typeof r.detail==='string'?r.detail:'Question failed');if(epoch!==qaEpoch||revision!==state.revision||version!==state.session.version)return;renderQA(r,'Live Gemma inference · actual local request');el('askProgress').textContent='Evidence checks complete. '+r.seconds.toFixed(2)+' s actual model request.'}
 catch(err){if(epoch===qaEpoch)el('askProgress').textContent=err.name==='AbortError'?'Question canceled; no answer accepted.':err.message}
 finally{clearInterval(tick);if(epoch===qaEpoch){qaController=null;el('askSubmit').disabled=false}}
};
el('askHandoff').onclick=()=>{
 clearQA();if(!state.session){el('askProgress').textContent='Load a source first.';return}const h=localHandoff(state.session),root=el('askAnswer');root.hidden=false;root.append(qaNode('span','Deterministic browser functionality · current session','ask-mode'));root.append(qaNode('h3','When you return.'));
 root.append(qaNode('p',h.timer?'Recorded browser interval: '+h.timer.status+'.':'No interval has ended in this visit.'));
 root.append(qaNode('p','User-confirmed source IDs: '+(h.confirmed_source_ids.join(', ')||'none')+'.'));
 if(h.next_source_id){const b=qaNode('button','Next original source '+h.next_source_id+' ↗','text-link');b.onclick=()=>{select(h.next_source_id,true);el('source-'+h.next_source_id)?.scrollIntoView({block:'center'})};root.append(b,qaNode('blockquote',h.next_source,'source-quote'))}
 root.append(qaNode('p',h.pending_reviews.length+' unresolved review question'+(h.pending_reviews.length===1?'':'s')+'.'));for(const q of h.pending_reviews)root.append(qaNode('p',q.question,'caption'));
 root.append(qaNode('p','Derived from source order and recorded decisions. No inference, observation of the experiment or physical completion is implied.','caption'));const b=qaNode('button','Open Return Handoff ↗','text-link');b.onclick=()=>showHandoff(false);root.append(b)
};
const v5ShowPlan=showPlan;showPlan=function(d){v5ShowPlan(d);currentQA()};
const v5ClearResult=clearResult;clearResult=function(message){clearQA();v5ClearResult(message);currentQA()};
const v5Decision=decision;decision=async function(d){const r=await v5Decision(d);clearQA('Session changed. Select a source question again or inspect the current handoff.');return r};
(async()=>{try{qaRecords=REPLAY?window.PREPARED_QUESTIONS||{}:await(await fetch('/api/questions')).json();currentQA();const requested=new URLSearchParams(location.search).get('scenario');if(['A','B','C'].includes(requested))await loadSample(requested)}catch{el('askProgress').textContent='Recorded questions unavailable. Current session facts remain accessible.'}})();
