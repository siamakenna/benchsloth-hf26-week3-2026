"""Original vector editorial art and architecture, not third-party imagery."""
from pathlib import Path
import html,json
R=Path(__file__).resolve().parents[1];A=R/'assets/v4'
def write(name,content): (A/name).write_text(content)
base='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><rect width="1600" height="900" fill="#f8f6f0"/>'
cover=base+'<g fill="#17352e"><text x="76" y="80" font-family="monospace" font-size="17" letter-spacing="3">BENCHSLOTH / THE ATTENTION HANDOFF</text><path d="M76 110H1524" stroke="#bfcbbc"/><text x="76" y="240" font-family="Georgia" font-size="78" letter-spacing="-3">Less clock-watching.</text><text x="76" y="336" font-family="Georgia" font-size="78" letter-spacing="-3" fill="#658674">A better way back.</text><text x="80" y="395" font-family="monospace" font-size="18">LOCAL GEMMA · SOURCE EVIDENCE · HUMAN DECISIONS</text></g>'
for i,(title,quote,badge) in enumerate([('01 / THE SOURCE','Wait for 5 minutes.','EXACT ORIGINAL WORDS'),('02 / THE AGENT','Extract → propose → verify → review','INSPECTABLE TOOL OUTPUTS'),('03 / THE RETURN','The next original step. Your recorded state.','NO EXPERIMENT OBSERVED')]):
 y=475+i*102;cover+=f'<rect x="80" y="{y}" width="1438" height="80" fill="{"#e5ecde" if i<2 else "#17352e"}" stroke="#bdcbb3"/><text x="103" y="{y+28}" font-family="monospace" font-size="13" fill="{"#52665b" if i<2 else "#cbdcc2"}">{title}</text><text x="103" y="{y+57}" font-family="Georgia" font-size="25" fill="{"#17352e" if i<2 else "#f8f6f0"}">{html.escape(quote)}</text><text x="1479" y="{y+46}" text-anchor="end" font-family="monospace" font-size="12" fill="{"#52665b" if i<2 else "#cbdcc2"}">{badge}</text>'
cover+='<path d="M1110 160C1240 130 1350 165 1480 130" fill="none" stroke="#658674" stroke-width="3"/><path d="M1210 155C1190 185 1220 227 1267 220C1310 218 1337 181 1310 153" fill="#bdac92" stroke="#17352e" stroke-width="3"/><ellipse cx="1255" cy="193" rx="32" ry="26" fill="#f8f6f0" stroke="#17352e" stroke-width="2"/><path d="M1230 185L1245 195M1280 185L1265 195" stroke="#658674" stroke-width="11" stroke-linecap="round"/><path d="M1236 189L1242 192M1271 192L1277 189M1248 204Q1255 209 1262 204" fill="none" stroke="#17352e" stroke-width="2"/><text x="80" y="860" font-family="monospace" font-size="12" fill="#52665b">ORIGINAL EDITORIAL ILLUSTRATION / NOT A UI SCREENSHOT · RESEARCH PREVIEW</text></svg>'
write('dev-cover.svg',cover)
labels=[('Source','Original occurrence IDs'),('Deterministic code','Exact durations + restrictions'),('Local Gemma','Proposed temporal links'),('Verifier','Cue spans + target checks'),('Human review','Visible queue + confirmation'),('Browser session','Timer + recorded decisions'),('Return Handoff','Next source + unresolved items')]
graph=base+'<text x="70" y="80" font-family="Georgia" font-size="48" fill="#17352e">A bounded agent. An inspectable handoff.</text><text x="70" y="127" font-family="monospace" font-size="17" fill="#52665b">One model proposal call. Typed tools. Explicit state. No equipment control.</text>'
for i,(name,sub) in enumerate(labels):
 x=80+(i%4)*380;y=220+(i//4)*260
 graph+=f'<rect x="{x}" y="{y}" width="322" height="150" fill="{"#17352e" if i==6 else "#e7eddf"}" stroke="#aabda1"/><text x="{x+23}" y="{y+37}" font-family="monospace" font-size="14" fill="{"#c8d9bd" if i==6 else "#52665b"}">0{i+1}</text><text x="{x+23}" y="{y+77}" font-family="Georgia" font-size="28" fill="{"#f8f6f0" if i==6 else "#17352e"}">{name}</text><text x="{x+23}" y="{y+114}" font-family="monospace" font-size="12" fill="{"#c8d9bd" if i==6 else "#52665b"}">{html.escape(sub)}</text>'
 graph+=f'<text x="{x+334}" y="{y+86}" font-family="Georgia" font-size="30" fill="#658674">{ "→" if i%4!=3 and i!=6 else "" }</text>'
graph+='<path d="M1380 389V430H240V464" stroke="#658674" fill="none" stroke-width="2"/><text x="80" y="800" font-family="monospace" font-size="17" fill="#52665b">The model cannot create durations, clear restrictions, start timers, or perform laboratory steps.</text></svg>'
write('architecture.svg',graph)
summary=json.loads((R/'evaluation/v4/holdout-4b/summary.json').read_text())
table=base+'<text x="70" y="100" font-family="Georgia" font-size="55" fill="#17352e">What changed on the same 32 cases?</text><text x="70" y="150" font-family="monospace" font-size="18" fill="#52665b">67 source lines · 22 gold links · 18 eligible waits · synthetic, assistant-labeled data</text>'
headers=['Approach','Correct links','Wrong links','Eligible waits','Unsupported']
xs=[90,650,870,1080,1340]
for x,h in zip(xs,headers):table+=f'<text x="{x}" y="250" font-family="monospace" font-size="19" fill="#52665b">{h}</text>'
for i,(key,title) in enumerate([('rules','Strengthened rules'),('v2','Earlier Gemma policy'),('agent','Attention Agent')]):
 m=summary['metrics'][key];y=340+i*130
 table+=f'<rect x="70" y="{y-55}" width="1460" height="108" fill="{"#17352e" if key=="agent" else "#e7eddf"}"/>'
 vals=[title,str(m['link_tp'])+'/22',str(m['link_fp']),str(m['correct_waits'])+'/18',str(m['unsupported_eligibility'])+'/67']
 for x,v in zip(xs,vals):table+=f'<text x="{x}" y="{y+9}" font-family="{"Georgia" if x==90 else "monospace"}" font-size="30" fill="{"#f8f6f0" if key=="agent" else "#17352e"}">{v}</text>'
table+='<text x="80" y="795" font-family="monospace" font-size="16" fill="#52665b">Perfect on this small set does not establish general reliability. Human trials: 0.</text></svg>'
write('baseline-comparison.svg',table)
print('Wrote three original SVG illustrations')
