import json,sys,time,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from semantic_v6 import ask,baseline
split=sys.argv[1] if len(sys.argv)>1 else 'development';out=R/'evaluation/v6'/('dev-run' if split=='development' else 'final-run');out.mkdir(exist_ok=True)
freeze=json.loads((R/'evaluation/v6/DATA_FREEZE.json').read_text())
for f,h in freeze['files'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
cases=json.loads((R/'evaluation/v6'/f'{split}.json').read_text())['cases']
for c in cases:
 path=out/(c['id']+'.json')
 if path.exists():continue
 b=baseline(c['source'],c['question'])
 try:r=ask(c['source'],c['question'])
 except Exception as e:r=dict(error=str(e))
 path.write_text(json.dumps(dict(case=c,rules=b,gemma=r),indent=2)+'\n');print(c['id'],b['status'],r.get('proposal'),r.get('error',''),flush=True)
