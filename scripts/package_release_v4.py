"""Exact indexed payload plus bounded pattern scan of all reachable Git blob history.

Run after the release commit; generated receipt lives beside the archive to avoid
self-referential commit/archive hashes. Manifest deliberately excludes itself.
"""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
R=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
manifest_name='provenance/publication-manifest-v4.json'
secret=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9]{20,}')
paths=[p for p in git('ls-files','-z').decode().split('\0') if p and p!=manifest_name]
excluded=('.tools/','.venv/','.firecrawl/','node_modules/','assets/recordings/','.git/')
files=[]
for n in paths:
 assert not n.startswith(excluded),f'Excluded path indexed: {n}'
 assert Path(n).name not in ['.env','.env.local'],f'Environment file indexed: {n}'
 data=(R/n).read_bytes()
 assert not secret.search(data),f'Potential secret in indexed payload: {n}'
 files.append(dict(path=n,bytes=len(data),sha256=sha(data)))
# Scan all reachable blobs, including deleted historical content. Never print matches.
objects={line.split(b' ',1)[0].decode() for line in git('rev-list','--objects','--all').splitlines()};blobs=0
for oid in sorted(objects):
 if git('cat-file','-t',oid).strip()!=b'blob':continue
 blobs+=1;data=git('cat-file','blob',oid)
 assert not secret.search(data),'Potential secret in reachable historical blob; inspect privately before packaging.'
manifest=dict(publication_authorized=False,scope='Local release payload; exact source commit recorded in adjacent archive receipt. No .git included.',files=files,file_count=len(files),file_bytes=sum(f['bytes'] for f in files),excluded=list(excluded),scan='Indexed payload and all reachable Git blobs checked for private-key headers and common GitHub/OpenAI tokens. No matches; limited pattern scan, not universal sensitive-data detection.')
(R/manifest_name).write_text(json.dumps(manifest,indent=2)+'\n')
archive=R.parent/'BenchSloth_Week3_v0.4_RC.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(R/f['path'],'benchsloth-week3/'+f['path'])
 z.write(R/manifest_name,'benchsloth-week3/'+manifest_name)
receipt=dict(source_commit=git('rev-parse','HEAD').decode().strip(),archive=str(archive),archive_sha256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,files=len(files)+1,history_blobs_scanned=blobs,publication_authorized=False,tracked_worktree_matches_source_commit=subprocess.run(['git','diff','--quiet','HEAD','--'],cwd=R).returncode==0)
p=R.parent/'BenchSloth_v0.4_package-receipt.json';p.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
