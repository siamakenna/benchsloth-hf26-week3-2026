/* BenchSloth revision state. epoch() adapted from FundPilot evidence-core.js.
   MIT License, Copyright (c) 2026 Makenna Rodriguez. See docs/LOCAL_REUSE_LICENSE.txt. */
(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.RevisionCore=api})(typeof window==='object'?window:this,function(){
'use strict';
function epoch(){let value=0;return Object.freeze({begin:()=>++value,invalidate:()=>{value++;},accepts:t=>Number.isInteger(t)&&t>0&&t===value})}
function rows(text){if(typeof text!=='string'||!text.trim()||text.length>100000)throw Error('Provide 1–100000 characters per version.');const a=text.split('\n').map(s=>s.trim()).filter(Boolean);if(a.length>512)throw Error('At most 512 original nonempty occurrences per version.');return a.map((source,i)=>Object.freeze({id:i+1,source}))}
function numbers(s){return s.match(/\d+(?:\.\d+)?/g)||[]}
function alerts(a,b){const f=[];const verbs=t=>(t.toLowerCase().match(/\b(read|record|write|log|inspect|check|photograph|capture|rinse|transfer|put|place|close|return|monitor|observe|watch)\b/g)||[]).map(x=>({write:'record',log:'record',check:'inspect',photograph:'image',capture:'image',observe:'monitor',watch:'monitor',place:'put'}[x]||x));if(JSON.stringify(verbs(a))!==JSON.stringify(verbs(b)))f.push('Action verb sequence changed');if(JSON.stringify(numbers(a))!==JSON.stringify(numbers(b)))f.push('Original numeric text changed');const n=s=>(s.match(/\b(no|not|never|only|must|may|optional|required)\b/gi)||[]).map(v=>v.toLowerCase());if(JSON.stringify(n(a))!==JSON.stringify(n(b)))f.push('Explicit restriction / negation wording changed');if(a!==b&&/\b(watch\w*|observ\w*|monitor\w*|attend\w*|unattended|leave|remain|stay|continuously|intermittently|throughout)\b/i.test(a+' '+b))f.push('Monitoring / attendance wording changed');const o=s=>(s.match(/\b(before|after|then|during|once|until)\b/gi)||[]).map(v=>v.toLowerCase());if(JSON.stringify(o(a))!==JSON.stringify(o(b)))f.push('Explicit order wording changed');return f}
function create(oldText,newText){const oldRows=Object.freeze(rows(oldText)),newRows=Object.freeze(rows(newText));const pairs=[];const used=new Set(),exact=new Map();for(const r of oldRows){const match=newRows.find(n=>!used.has(n.id)&&n.source===r.source);if(match){exact.set(r.id,match);used.add(match.id)}}
 // Exact occurrence alignment first, then same-position literal-diff cards. Never merge duplicate IDs.
 for(const r of oldRows){let n=exact.get(r.id);if(!n)n=newRows.find(n=>n.id===r.id&&!used.has(n.id));if(n)used.add(n.id);const flags=alerts(r.source,n?.source||'');if(n&&n.id!==r.id)flags.push('Original occurrence position changed / review order');pairs.push({id:'old-'+r.id+'-new-'+(n?.id||0),oldId:r.id,newId:n?.id||null,kind:n?.source===r.source&&n.id===r.id?'same':n?'changed':'review',flags,annotation:null})}
 for(const n of newRows)if(!used.has(n.id))pairs.push({id:'old-0-new-'+n.id,oldId:null,newId:n.id,kind:'review',flags:['Original source occurrence added'],annotation:null});
 return {oldText,newText,oldRows,newRows,pairs,pins:[],history:[],undo:[],oldHash:null,newHash:null,model:null,modelOrigin:null}
}
function passage(s,version,id){const a=version==='old'?s.oldRows:version==='new'?s.newRows:null;const r=a?.find(r=>r.id===id);if(!r)throw Error('Unknown version-qualified original source ID.');return r}
function pin(s,version,id){passage(s,version,id);if(s.pins.some(p=>p.version===version&&p.id===id))return;if(s.pins.length>=3)throw Error('Keep up to three version-qualified passages. Dismiss one first.');s.pins.push({version,id});s.undo.push({kind:'unpin',version,id});s.history.push({kind:'pin',version,id})}
function unpin(s,version,id){const i=s.pins.findIndex(p=>p.version===version&&p.id===id);if(i<0)return;const p=s.pins.splice(i,1)[0];s.undo.push({kind:'restore_pin',pin:p,index:i});s.history.push({kind:'unpin',version,id})}
function reorder(s,version,id,delta){const i=s.pins.findIndex(p=>p.version===version&&p.id===id);if(i<0)return;const j=Math.max(0,Math.min(s.pins.length-1,i+delta));const [p]=s.pins.splice(i,1);s.pins.splice(j,0,p);s.undo.push({kind:'reorder',version,id,index:i});s.history.push({kind:'move_pin',version,id})}
function annotate(s,pairId,choice,confirmed,rationale=""){if(!confirmed)throw Error('Human confirmation required.');if(!['approve_correspondence','keep_open','reject_correspondence'].includes(choice))throw Error('Unknown annotation.');const p=s.pairs.find(p=>p.id===pairId);if(!p)throw Error('Unknown original pair.');s.undo.push({kind:'annotation',pairId,before:p.annotation});p.annotation=choice;s.history.push({kind:'user_annotation',pairId,choice,oldHash:s.oldHash,newHash:s.newHash,oldId:p.oldId,newId:p.newId,rationale:String(rationale).slice(0,2000),contextEvidence:contextFor(s,p),recordedAt:new Date().toISOString(),sourceChanged:false,timerAuthority:false})}
function undo(s){const a=s.undo.pop();if(!a)return false;if(a.kind==='unpin')s.pins=s.pins.filter(p=>p.version!==a.version||p.id!==a.id);if(a.kind==='restore_pin')s.pins.splice(a.index,0,a.pin);if(a.kind==='annotation')s.pairs.find(p=>p.id===a.pairId).annotation=a.before;if(a.kind==='reorder'){const i=s.pins.findIndex(p=>p.version===a.version&&p.id===a.id);const [p]=s.pins.splice(i,1);s.pins.splice(a.index,0,p)}s.history.push({kind:'undo',action:a});return true}
function acceptModel(s,record,oldHash,newHash){if(s.oldHash!==oldHash||s.newHash!==newHash||record.old_hash!==oldHash||record.new_hash!==newHash)throw Error('Model response belongs to another revision pair.');for(const i of record.old_ids)passage(s,'old',i);for(const i of record.new_ids)passage(s,'new',i);if(!['same','action_change','monitoring_change','unclear','unrelated'].includes(record.classification))throw Error('Invalid semantic class.');s.model=structuredClone(record);return s.model}
function freshPreview(s){const lines=s.newRows,hash=s.newHash,steps=lines.map(r=>({id:r.id,source:r.source,label:r.source,kind:'note',review_needed:true,reason:'Fresh source revision. All intervals held for source review in static preview.',fixed_minutes:null,rest_minutes:null,evidence:[]}));const reviews={items:steps.filter(r=>!r.source.startsWith('#')).map(r=>({id:'source-'+r.id,source_ids:[r.id],status:'pending',question:'Review NEW source '+r.id+': '+r.source,passages:[r.source]}))};const plan={protocol:s.newText,steps,links:[],rest_windows:0,documented_rest_minutes:0,review_needed:steps.length,model_calls:0,engine:'Deterministic new-source preview / all intervals held',mode:'revision-preview'};const session={id:'revision-preview-'+hash,source_hash:hash,version:0,phase:'ready-for-review',confirmed:[],timer:null,decisions:[],reviews,trace:[],plan:structuredClone(plan),handoff:{next_source_id:steps.find(r=>!r.source.startsWith('#'))?.id||null,next_source:steps.find(r=>!r.source.startsWith('#'))?.source||null,pending_reviews:reviews.items,confirmed_source_ids:[],timer:null,changes:[]}};return {...plan,agent:session}}
function retire(s,reason){return {status:'stale',reason,oldHash:s.oldHash,newHash:s.newHash,oldText:s.oldText,newText:s.newText,history:structuredClone(s.history),timerAuthority:false}}
function impact(s,p){const a=p.oldId?passage(s,'old',p.oldId).source:'',b=p.newId?passage(s,'new',p.newId).source:'';const items=[];const add=(type,consequence)=>items.push({type,consequence,oldId:p.oldId,newId:p.newId,authority:'deterministic rule',timerAuthority:false});
 if(!p.newId)add('Deleted original occurrence','No NEW occurrence is paired here. Recheck any prior annotation; no deletion consequence beyond the text is inferred.');
 if(!p.oldId)add('Added original occurrence','Review this NEW instruction independently. No OLD permission applies.');
 const durations=t=>t.match(/\b\d+(?:\.\d+)?\s*(?:seconds?|minutes?|hours?|secs?|mins?)\b/gi)||[];
 if(JSON.stringify(durations(a))!==JSON.stringify(durations(b)))add('Explicit duration changed','Recheck the original duration. Any NEW interval requires a separate source review and timer confirmation.');
 if(p.flags.some(f=>f.includes('Monitoring')))add('Monitoring language changed','Recheck attendance wording before considering any break. This desk does not monitor laboratory work.');
 if(p.flags.some(f=>f.includes('position')||f.includes('order')||f.includes('sequence')))add('Order / action needs rechecking','Only literal order and action wording are flagged. No causal dependency is inferred.');
 if(p.kind!=='same')add('Unresolved semantic correspondence','Display pairing is provisional. Confirm correspondence or abstain after inspecting both originals.');
 return items}
function contextFor(s,p){
 const result=[];
 for(const version of ['old','new']){const id=version==='old'?p.oldId:p.newId,all=version==='old'?s.oldRows:s.newRows;if(!id)continue;
  let section=null;for(const r of all){if(r.source.startsWith('#'))section=r;if(r.id===id)break}
  const matches=all.filter(r=>r.id===id||r.id===id-1||r.id===id+1||r.id===section?.id||/\b(?:throughout|all steps|entire (?:protocol|procedure)|at all times)\b/i.test(r.source)||[...r.source.matchAll(/\b(?:source|line)\s+(\d+)\b/gi)].some(m=>Number(m[1])===id));
  for(const r of matches)result.push({version,id:r.id,source:r.source,reason:r.id===id?'selected evidence':r.id===section?.id?'section heading':Math.abs(r.id-id)===1?'adjacent context; scope unverified':'explicit source reference; meaning requires review',restriction:/\b(must|never|not|unless|only|keep|continuously)\b/i.test(r.source)});
 }
 return result;
}
function continuity(s,p,archives=[]){
 const records=[];
 for(const a of archives){
  const active=new Map();
  for(const e of a.history||[]){if(e.kind==='user_annotation'){const stack=active.get(e.pairId)||[];stack.push(e);active.set(e.pairId,stack)}else if(e.kind==='undo'&&e.action?.kind==='annotation')active.get(e.action.pairId)?.pop()}
  for(const e of a.history||[]){
   if(e.kind!=='user_annotation')continue;
   const sourceId=a.newHash===s.oldHash?e.newId:a.oldHash===s.oldHash?e.oldId:null;
   if(sourceId!==p.oldId||!sourceId)continue;
   const current=active.get(e.pairId)?.at(-1)===e;
   records.push({...structuredClone(e),status:current?'stale / recheck required':'historical / undone or superseded',sourceId,exactTextUnchanged:!!p.newId&&passage(s,'old',p.oldId).source===passage(s,'new',p.newId).source,timerAuthority:false,permissionTransferred:false});
  }
 }
 return records;
}
return {contextFor,continuity,epoch,rows,alerts,create,passage,pin,unpin,reorder,annotate,undo,acceptModel,retire,impact,freshPreview};
});
