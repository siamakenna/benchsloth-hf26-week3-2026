from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[2];out=R/'assets/v6';out.mkdir(exist_ok=True)
def svg(w,h,body):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#F8F6F0"/>{body}</svg>'
def t(x,y,text,size=24,fill='#17352E',family='Georgia'):return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}">{html.escape(text)}</text>'
def rect(x,y,w,h,fill='#DDE9DE'):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="#BDCAB7"/>'
body=t(65,68,'BENCHSLOTH / THE ATTENTION AGENT',16,family='monospace')+t(65,165,'Give your attention',73)+t(65,245,'a plan.',83,fill='#658674')+t(65,326,'I stopped asking AI to do what',28)+t(65,367,'simple rules did better.',28)+t(65,430,'Original evidence. Visible uncertainty.',21)+t(65,466,'A clear handoff when you return.',21)+t(65,597,'LOCAL GEMMA · HUMAN REVIEW · SLOW & STEADY',15,family='monospace')
body+=rect(830,89,690,500,'#EFF2E8')+t(860,135,'THE ATTENTION MAP',16,family='monospace')+t(860,178,'01 / Original source',18)+t(860,217,'Wait 7 minutes.',30)+t(1390,217,'7 min',32)
body+='<path d="M870 245V346" stroke="#658674" stroke-width="2"/><circle cx="870" cy="264" r="7" fill="#17352E"/><circle cx="870" cy="345" r="7" fill="#F8F6F0" stroke="#658674"/>'
body+=t(897,270,'02 / After that wait, record the label.',22)+rect(855,375,640,155,'#FFFEF9')+t(877,410,'ASK BENCHSLOTH / EVIDENCE FIRST',13,family='monospace')+t(877,450,'Which earlier wait does source 2 refer to?',21)+t(877,488,'Source 1 + source 2 → inspect the relationship.',17)+t(860,565,'RECORDED OUTPUT / INTERACTIVE BROWSER',12,family='monospace')
(out/'dev-cover.svg').write_text(svg(1600,672,body))
body=t(45,58,'ONE AGENT. TWO KINDS OF AUTHORITY.',18,family='monospace')+t(45,112,'Evidence explains. Source rules decide the clock.',36)
boxes=[(45,175,300,125,'READ','Original source IDs + hash'),(395,175,300,125,'UNDERSTAND','Gemma evidence selection'),(745,175,300,125,'VERIFY','Exact quotes + review'),(45,365,300,125,'PLAN','Frozen source restrictions'),(395,365,300,125,'REST','User-confirmed interval'),(745,365,300,125,'RETURN','Recorded facts + source order')]
for x,y,w,h,head,copy in boxes:body+=rect(x,y,w,h)+t(x+20,y+37,head,15,family='monospace')+t(x+20,y+81,copy,18)
body+='<path d="M345 238H386M695 238H736M895 300V340H195V356M345 428H386M695 428H736" stroke="#658674" stroke-width="2" fill="none"/>'
body+=t(45,549,'Read-only semantic answers cannot start timers, amend procedures or certify physical work.',16)+t(45,585,'A valid citation proves source identity. Semantic correctness still needs review.',16)
(out/'architecture.svg').write_text(svg(1100,630,body))
p=R/'evaluation/v6/summary.json'
if p.exists():
 summary=json.loads(p.read_text());body=t(45,55,'THE SEMANTIC TEST / 24 SYNTHETIC QUESTIONS',16,family='monospace')+t(45,110,'Read the failures with the result.',39)
 for i,(k,name) in enumerate([('rules','Strong rules + retrieval'),('raw_gemma','Raw Gemma selection'),('verified_agent','Combined read-only agent')]):
  m=summary[k];y=180+i*105;body+=t(45,y,name,22)+rect(380,y-25,620,35,'#E6EADD')+rect(380,y-25,620*m['exact']/24,35,'#658674')+t(1025,y+1,f"{m['exact']}/24",23)
 body+=t(45,519,'Exact answer status + exact source IDs; extra evidence counts against every method.',16)+t(45,553,'Assistant-authored, implementer-visible references. Independent human n=0.',16)+t(45,586,'Question answering is read only; historical timer results are reported separately.',16)
 (out/'baseline-comparison.svg').write_text(svg(1140,630,body))
print('Wrote original SVG figures')
