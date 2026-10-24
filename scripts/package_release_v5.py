"""Exact indexed payload, nested-ZIP and reachable-history pattern review.

Receipt beside archive avoids recursive commit/archive identity. No public action.
"""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile,io
R=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
manifest_name='provenance/publication-manifest-v5.json'
secret=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9]{20,}')
local=re.compile(rb'/Users/[^/\s]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',re.I)
paths=[p for p in git('ls-files','-z').decode().split('\0') if p and p!=manifest_name]
excluded=('.tools/','.venv/','.firecrawl/','node_modules/','assets/recordings/','.git/','private-review/','evaluation/reviewer-v5/responses/')
files=[];local_matches=[];nested=0

def scan(data,name,depth=0):
 global nested
 assert not secret.search(data),f'Potential secret pattern in {name}; inspect privately before publication'
 if local.search(data):local_matches.append(name)
 if depth<3 and zipfile.is_zipfile(io.BytesIO(data)):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for info in z.infolist():
    assert info.file_size<100_000_000,'Unexpected oversized nested archive member'
    if not info.is_dir():nested+=1;scan(z.read(info),name+'!'+info.filename,depth+1)
for n in paths:
 assert not n.startswith(excluded),f'Excluded path indexed: {n}'
 assert Path(n).name not in ['.env','.env.local'],f'Environment file indexed: {n}'
 data=(R/n).read_bytes();scan(data,n);files.append(dict(path=n,bytes=len(data),sha256=sha(data)))
objects={line.split(b' ',1)[0].decode() for line in git('rev-list','--objects','--all').splitlines()}
checks=subprocess.run(['git','cat-file','--batch-check=%(objectname) %(objecttype)'],cwd=R,input=('\n'.join(sorted(objects))+'\n').encode(),stdout=subprocess.PIPE,check=True).stdout
blob_ids=[line.split()[0] for line in checks.splitlines() if line.split()[1]==b'blob'];blobs=len(blob_ids)
batch=subprocess.run(['git','cat-file','--batch'],cwd=R,input=b'\n'.join(blob_ids)+b'\n',stdout=subprocess.PIPE,check=True).stdout;offset=0
for oid in blob_ids:
 end=batch.index(b'\n',offset);header=batch[offset:end].split();size=int(header[2]);data=batch[end+1:end+1+size];offset=end+1+size+1
 assert header[0]==oid and header[1]==b'blob'
 assert not secret.search(data),'Potential secret in reachable history; inspect privately before publication.'

manifest=dict(publication_authorized=False,scope='Exact local reviewed file payload; public upload and author-history disclosure require explicit approval. .git excluded from ZIP.',files=files,file_count=len(files),file_bytes=sum(f['bytes'] for f in files),excluded=list(excluded),scan='Indexed payload, nested source ZIP and reachable historical blobs checked for limited private-key/GitHub/OpenAI token patterns; no matches. Not universal sensitive-data detection.',local_path_or_contact_matches=sorted(set(local_matches)),sensitive_review='Matches include retained historical test-log machine paths and may include scanner-pattern literals; inspect the file list. No private protocol or human responses included. Git author contact metadata separately reviewed outside public payload; full-history push would disclose it.')
(R/manifest_name).write_text(json.dumps(manifest,indent=2)+'\n')
archive=R.parent/'BenchSloth_Week3_v0.5_RC.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(R/f['path'],'benchsloth-week3/'+f['path'])
 z.write(R/manifest_name,'benchsloth-week3/'+manifest_name)
receipt=dict(source_commit=git('rev-parse','HEAD').decode().strip(),release_tag='v0.5.0-rc1',archive=str(archive),archive_sha256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,files=len(files)+1,history_blobs_scanned=blobs,nested_members_scanned=nested,local_path_contact_match_count=len(set(local_matches)),publication_authorized=False,tracked_worktree_matches_source_commit=subprocess.run(['git','diff','--quiet','HEAD','--'],cwd=R).returncode==0)
p=R.parent/'BenchSloth_v0.5_package-receipt.json';p.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
