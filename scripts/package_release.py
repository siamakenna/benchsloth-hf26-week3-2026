"""Package only reviewed Git-index files, never ignored runtimes or credentials."""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
paths=[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if p]
manifest_name='provenance/publication-manifest-v2.json'
excluded_prefixes=('.tools/','.venv/','.firecrawl/','node_modules/','assets/recordings/')
secret=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9]{20,}')
files=[]
for name in paths:
 if name==manifest_name:continue
 assert not name.startswith(excluded_prefixes),name
 data=(ROOT/name).read_bytes()
 assert not secret.search(data),f'Possible secret in {name}'
 files.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest={'destination':'siamakenna/benchsloth-hf26-week3-2026 (public; approval pending)','file_count':len(files),'file_bytes':sum(f['bytes'] for f in files),'excluded':list(excluded_prefixes),'secret_scan':'No private-key headers or common GitHub/OpenAI secret patterns observed; not a guarantee of all possible sensitive data. Human-facing publication scope in docs/PUBLICATION_PACKAGE.md.','files':files}
(ROOT/manifest_name).write_text(json.dumps(manifest,indent=2)+'\n')
archive=ROOT.parent/'BenchSloth_Week3_Rescue_RC2.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(ROOT/f['path'],'benchsloth-week3/'+f['path'])
 z.write(ROOT/manifest_name,'benchsloth-week3/'+manifest_name)
print(json.dumps({'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files)+1,'bytes':archive.stat().st_size,'ignored_data_included':False},indent=2))
