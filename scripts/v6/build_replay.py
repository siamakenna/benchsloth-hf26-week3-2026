from pathlib import Path
import json,shutil,zipfile
R=Path(__file__).resolve().parents[2];d=R/'demo';d.mkdir(exist_ok=True)
# Remove generated duplicate media only; original historical assets stay local.
for version in ['v4','v5']:
 old=d/'assets'/version
 if old.exists():
  for p in old.rglob('*'):
   if p.is_file():
    original=R/'assets'/version/p.relative_to(old)
    assert original.exists() and original.read_bytes()==p.read_bytes(), 'Historical media copy differs; preserve before rebuilding.'
  shutil.rmtree(old)
scenarios={k:json.loads((R/'static'/f'scenario-v5-{k}.json').read_text()) for k in 'ABC'}
questions=json.loads((R/'static/questions-v6.json').read_text()) if (R/'static/questions-v6.json').exists() else {}
summary=json.loads((R/'evaluation/v6/summary.json').read_text()) if (R/'evaluation/v6/summary.json').exists() else {}
s=(R/'static/index.html').read_text().replace('const REPLAY = false','const REPLAY = true');inject='\n'.join('window.'+k+'='+json.dumps(v).replace('<','\\u003c')+';' for k,v in [('PREPARED_SCENARIOS',scenarios),('PREPARED_QUESTIONS',questions),('PREPARED_EVALUATION',summary)]);s=s.replace('<script>','<script>\n'+inject,1);(d/'index.html').write_text(s)
(d/'product').mkdir(exist_ok=True)
for name in ['product-v6.css','intelligence-v6.js']:shutil.copy2(R/'static'/name,d/'product'/name)
for version in ['v6']:
 for p in (R/'assets'/version).glob('*'):
  if p.suffix in ['.png','.svg','.webm','.pdf'] and '-draft' not in p.name:
   target=d/'assets'/version/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
with zipfile.ZipFile(d/'downloads/benchsloth-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in [*R.glob('*.py'),*R.glob('requirements*.txt'),R/'LICENSE',*(R/'static').glob('*')]:
  if p.is_file() and p.name!='index-v5.html':z.write(p,'benchsloth/'+str(p.relative_to(R)))
 z.writestr('benchsloth/README.md','# Optional core source snapshot\n\nFor the complete project, scripts and evidence use the reviewed public repository after publication. Gemma weights and runtimes are separate. Local app: uvicorn server_v6:app --host 127.0.0.1 --port 8772. MIT code; separate Google Gemma terms.\n')
print('Built self-contained replay with',sum(map(len,questions.values())),'recorded questions')
