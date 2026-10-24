from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1];D=R/'assets/v5';D.mkdir(exist_ok=True)
def text(x,y,s,size=24,color='#17352e',font='Georgia'):return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{color}">{html.escape(s)}</text>'
def svg(body,w=1600,h=900):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#f8f6f0"/>{body}</svg>'
body=text(70,74,'BENCHSLOTH / THE ATTENTION AGENT',18,font='monospace')+text(70,185,'Simple rules beat my lab AI.',64)+text(70,265,'So I rebuilt its attention span.',58,'#658674')+text(70,335,'LOCAL GEMMA · ORIGINAL SOURCES · HUMAN CONTROL',18,font='monospace')
for x,title,sub in [(70,'Read the source','Keep occurrence IDs'),(560,'Focus the question','One note, one candidate'),(1050,'Make a better return','Review, record, resume')]:body+=f'<rect x="{x}" y="400" width="450" height="135" fill="#e4ebdf" stroke="#bdcab5"/>'+text(x+22,450,title,31)+text(x+22,495,sub,17,font='monospace')
body+=text(70,620,'ORIGINAL EDITORIAL COVER / SYNTHETIC EVIDENCE / NOT A UI SCREENSHOT',14,font='monospace')
(D/'dev-cover.svg').write_text(svg(body,1600,672))
a=(R/'assets/v4/architecture.svg').read_text().replace('One model proposal call. Typed tools. Explicit state. No equipment control.','Focused source pairs. Bounded calls. Explicit abstention. Human control.').replace('Local Gemma','Focused Gemma');(D/'architecture.svg').write_text(a)
summary=json.loads((R/'evaluation/v5/final/summary.json').read_text());body=text(70,95,'Longer sources. A smaller question.',54)+text(70,148,'20 prospective synthetic cases /140 lines /22 reference links /18 eligible waits',19,font='monospace')
headers=[(85,'Same cases'),(640,'Exact links'),(855,'Extra'),(1030,'Waits'),(1260,'Exact workflows')]
for x,h in headers:body+=text(x,235,h,20,font='monospace')
for i,(method,label) in enumerate([('v4','V4 whole protocol'),('rules','Strong scoped rules'),('v5','V5 focused Gemma')]):
 y=275+i*125;m=summary[method]['total'];dark=method=='v5';color='#f8f6f0' if dark else '#17352e';body+=f'<rect x="70" y="{y}" width="1460" height="105" fill="{"#17352e" if dark else "#e4ebdf"}"/>'
 for x,value in [(85,label),(640,f'{m["tp"]}/22'),(855,str(m['fp'])),(1030,f'{m["correct_waits"]}/18'),(1260,f'{m["complete_workflows"]}/20')]:body+=text(x,y+65,value,29,color,'Georgia' if x==85 else 'monospace')
body+=text(70,745,'V5 and strongest rules tie. No incremental model accuracy advantage established.',20,font='monospace')+text(70,787,'V5:0 unsupported timer offers;2 valid waits conservatively blocked. Human n=0.',18,font='monospace')+text(70,831,'Assistant-authored, implementer-visible references. See length groups and all failures.',16,font='monospace');(D/'baseline-comparison.svg').write_text(svg(body))
body=text(70,90,'The same six-line source. Different task boundaries.',48)+text(70,143,'Exposed development example /not an unseen result',19,font='monospace')
for x,title,labels in [(70,'V4 whole-source output',['source3: none','source5: none']),(840,'V5 focused output',['source3: after:2','source5: after:4'])]:
 body+=f'<rect x="{x}" y="200" width="690" height="455" fill="#e4ebdf" stroke="#bdcab5"/>'+text(x+25,250,title,33)
 for j,t in enumerate(labels):body+=text(x+25,320+j*66,t,29,font='monospace')
 body+=text(x+25,505,'“After the first wait ends, rinse the slides.”',20)+text(x+25,550,'“After the second wait ends, record the slide',20)+text(x+25,582,'identifier.”',20)
body+=text(70,735,'Exact original passages remain unchanged; full IDs, raw calls and validation in evidence.',19,font='monospace')+text(70,790,'The separate deictic example still leaves its second target unresolved. No hidden repair.',17,font='monospace');(D/'attention-before-after.svg').write_text(svg(body))
print('Original graphics prepared')
