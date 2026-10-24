import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from semantic_v6 import ask
questions={'A':['Which instruction follows the wait?','Which earlier wait does source 2 refer to?','What temperature is specified?'],'B':['Which wait does source 3 refer to?','What remains unspecified?','What concentration is specified?'],'C':['Which earlier wait does source 9 refer to?','Which earlier wait does source 3 refer to?','What equipment model is specified?']};result={};out=R/'evaluation/v6/demo-questions';out.mkdir(exist_ok=True)
for key,qs in questions.items():
 d=json.loads((R/'static'/f'scenario-v5-{key}.json').read_text());result[key]=[]
 for i,q in enumerate(qs,1):
  p=out/f'{key}{i}.json'
  if not p.exists():
   r=ask(d['protocol'],q);r['capture_note']='Selected demonstration question, not a held-out evaluation case. Original model and deterministic routes preserved.';p.write_text(json.dumps(r,indent=2)+'\n');print(key,i,r['answer']['status'],r['answer']['source_ids'],flush=True)
  result[key].append(json.loads(p.read_text()))
(R/'static/questions-v6.json').write_text(json.dumps(result,indent=2)+'\n')
