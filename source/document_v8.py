"""Full-document v8 storage and bounded retrieval; never a model context budget.
Raw text is immutable. IDs count nonempty occurrences, including headings/duplicates.
Literal references describe review scope, not experimental causal dependencies.
"""
import hashlib,re
MAX_LINES=512
MAX_CHARS=100000
WAIT=re.compile(r'\b(?:wait|incubat\w*|rest|hold|settle|overnight)\b',re.I)
WAIT_OCCURRENCE=re.compile(r'^(?:(?:\d+[.)]|[-*])\s*)?(?:wait|incubate|rest|hold|settle)\b',re.I)
DURATION=re.compile(r'\b\d+(?:\.\d+)?(?:\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)?\s*(?:s(?:ec(?:ond)?s?)?|m(?:in(?:ute)?s?)?|h(?:ou)?rs?|hours?|days?)\b|\bovernight\b',re.I)
MONITOR=re.compile(r'\b(?:monitor\w*|watch\w*|observ\w*|continuously|periodically|every\s+\d+|unattended|do not leave|don.t leave)\b',re.I)
CONDITION=re.compile(r'\b(?:if|unless|until|optional|either)\b',re.I)
RESTRICT=re.compile(r'\b(?:must|never|not|only|avoid|keep|kept|fresh|cold|ice|unless|until|before|prior|continuously|monitor\w*|pressure)\b',re.I)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def document(source):
 if not isinstance(source,str) or not source.strip() or len(source)>MAX_CHARS:raise ValueError('Provide 1–100000 characters of original source.')
 rows=[];offset=0;section=None
 for physical,line in enumerate(source.splitlines(keepends=True),1):
  clean=line.strip()
  if clean:
   if len(rows)>=MAX_LINES:raise ValueError('Maximum 512 original nonempty occurrences; nothing accepted or truncated.')
   heading=bool(re.match(r'^#{1,6}\s|^(?:materials|reagents|equipment|procedure|protocol|notes|warnings|preparation|purification|staining)\s*:?$',clean,re.I))
   ident=len(rows)+1
   if heading:section=ident
   start=offset+line.index(clean)
   rows.append(dict(id=ident,source=clean,start=start,end=start+len(clean),physical_line=physical,section_id=section,is_heading=heading))
  offset+=len(line)
 return dict(source=source,source_hash=digest(source),rows=rows,nonempty_occurrences=len(rows),omitted_occurrences=0)
def source_bundle(source):return [dict(id=r['id'],source=r['source']) for r in document(source)['rows']]
def references(rows,row):
 earlier=[r for r in rows if r['id']<row['id'] and WAIT_OCCURRENCE.search(r['source']) and DURATION.search(r['source']) and not r['is_heading']]
 explicit=[int(m) for m in re.findall(r'\b(?:source|line)\s+(\d+)\b',row['source'],re.I)]
 ids=explicit.copy();basis='explicit original source IDs' if ids else 'unresolved scope'
 for ordinal,n in [('first',0),('second',1),('third',2)]:
  if re.search(r'\b'+ordinal+r'\s+(?:wait|interval|hold|incubation)\b',row['source'],re.I):
   if len(earlier)>n:ids.append(earlier[n]['id']);basis='ordinal resolved across complete original document'
   else:return dict(ids=[],missing=[],resolved=False,basis='ordinal has no original occurrence',cross_section=False)
 ids=list(dict.fromkeys(ids));known={r['id']:r for r in rows};missing=[i for i in ids if i not in known]
 cross=any(known[i]['section_id']!=row['section_id'] for i in ids if i in known)
 return dict(ids=[i for i in ids if i in known],missing=missing,resolved=bool(ids) and not missing,basis=basis,cross_section=cross)
def context_windows(source,ids,radius=2,max_chars=6000):
 d=document(source);rows=d['rows'];lookup={r['id']:r for r in rows}
 if not ids or any(type(i)is not int or i not in lookup for i in ids):raise ValueError('Unknown global source ID; no context substituted.')
 required=list(dict.fromkeys(ids));wanted=set(required)
 for i in required:
  wanted.update(range(max(1,i-radius),min(len(rows),i+radius)+1))
  if lookup[i]['section_id']:wanted.add(lookup[i]['section_id'])
 selected=[];budget=0
 for i in required+[j for j in sorted(wanted)if j not in required]:
  r=lookup[i];size=len(r['source'])
  if budget+size>max_chars:
   if i in required:raise ValueError('Selected original passages exceed bounded context budget; select a smaller source span.')
   continue
  selected.append(r);budget+=size
 return dict(source_hash=d['source_hash'],rows=sorted(selected,key=lambda r:r['id']),omitted_context_ids=sorted(wanted-{r['id']for r in selected}),context_characters=budget,timer_authority=False)
def wait_classification(row,rows):
 s=row['source'];tokens=DURATION.findall(s);classes=[];ref=references(rows,row)
 if tokens and MONITOR.search(s):classes.append('explicitly_monitored_period')
 if (tokens or WAIT.search(s)) and CONDITION.search(s):classes.append('conditional_wait')
 if re.search(r'\d\s*(?:-|–|—|to)\s*\d.*(?:min|hour|hr|sec|day)',s,re.I):classes.append('duration_range')
 if re.search(r'\b(?:during|while|before|after|prior to|meanwhile)\b',s,re.I):classes.append('overlapping_preparation_or_dependency')
 if tokens and re.search(r'\b(?:centrifug\w*|spin|run|elut\w*|dialy\w*|shak\w*|rotat\w*|fplc|akta|chromatograph\w*)\b',s,re.I):classes.append('equipment_running_supervision_unknown')
 if WAIT.search(s) and tokens:classes.append('explicit_wait_with_source_evidence')
 if (tokens or WAIT.search(s)) and (not tokens or re.search(r'\b(?:overnight|about|approximately|or)\b|\?|~|±',s,re.I)):classes.append('unresolved_or_unsupported_duration')
 return dict(source_id=row['id'],classes=classes,original_duration_tokens=tokens,reference=ref,restriction_candidate=bool(RESTRICT.search(s)),timer_authority=False,human_label=None)
