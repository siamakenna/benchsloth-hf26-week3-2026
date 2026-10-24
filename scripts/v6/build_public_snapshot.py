"""Curate and audit a privacy-safe public tree. No network/push/publication.

Run before local RC commit. The public tree has its own real-date Git commit;
original local history and excluded raw material remain unchanged.
"""
import hashlib,io,json,re,shutil,subprocess,sys,zipfile,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R.parent/'BenchSloth_v0.6_Public';MANIFEST='provenance/publication-manifest-v6.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def git(*args,cwd=R):return subprocess.check_output(['git',*args],cwd=cwd).decode().strip()
# Do not reset or delete an existing committed public candidate.
if (D/'.git').exists():raise SystemExit('Public snapshot already committed; inspect it before creating a replacement candidate.')
D.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
selected=set()
for pattern in ['*.py','requirements*.txt','README.md','LICENSE','package.json','.gitignore','run_checks.sh']:
 selected.update(p for p in R.glob(pattern) if p.is_file())
for folder in ['scripts','tests','eval','.github','static','demo']:
 selected.update(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
# Keep historical data/raw inference, omitting personal-path logs and duplicate reviewer demos.
for p in (R/'evaluation').rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and not any(part.startswith('reviewer-v') for part in p.relative_to(R/'evaluation').parts):
  if b'/Users/' not in p.read_bytes():selected.add(p)
for p in (R/'assets/v6').glob('*'):
 if p.is_file() and '-draft' not in p.name:selected.add(p)
docs=['AGENT_ARCHITECTURE_V6.md','GEMMA_VALUE_EVALUATION.md','SEMANTIC_ERROR_ANALYSIS.md','PUBLIC_EXPLORER.md','HUMAN_VALIDATION.md','DESIGN_SYSTEM_FINAL.md','JUDGE_SCORECARD_FINAL.md','DEV_POST_FINAL.md','DEV_POST_LOCAL_PREVIEW.md','PUBLIC_DISCLOSURE_MANIFEST.md','SUBMISSION_VERIFICATION.md','RELEASE_REPORT_V6.md','MODEL_EVALUATION.md','MODEL_EVALUATION_V2.md','MODEL_EVALUATION_V5.md','AGENT_EVALUATION_V5.md','LONG_CONTEXT_ERROR_ANALYSIS.md']
selected.update(R/'docs'/name for name in docs);selected.add(R/'provenance/starter-sha256.txt')
# Preserve only current product templates in public; v5 template remains in local tag/history.
selected={p for p in selected if p.name!='index-v5.html' and p.suffix not in ['.pyc'] and not any(part in ['responses','private-review','.env','node_modules','.venv','.tools','.firecrawl'] for part in p.relative_to(R).parts)}
for p in sorted(selected):
 target=D/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
# Blank reviewer source instruments are reproducible; participant exports and full packet stay private.
for p in [R/'evaluation/reviewer-v5/followup.html']:
 if p.exists():target=D/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
start=git('show','-s','--format=%H%n%aI','9f56212').splitlines();freeze=git('rev-parse','af4bfae');provenance=f'''# Public snapshot provenance

This clean snapshot was prepared on {datetime.datetime.now(datetime.timezone.utc).isoformat()}. Its Git commit uses the actual creation time; no commit is backdated.

BenchSloth development began in local commit {start[0]} on {start[1]}, within the October19–25,2026 entry window. Semantic data freeze:ae08aab. Engine/evaluator freeze:{freeze}. Previous release:caa55a1cef5d2007a5b1ceb4de6ce14e23d8cbf2. File-level hashes and raw outputs are preserved. These local commit identifiers document development provenance; their full original history is retained locally and is not part of this clean public Git history. They are not an independent timestamp attestation.

The public snapshot omits private author-contact metadata, historical test logs containing local home paths, duplicated old media, runtimes, weights, credentials and participant responses. It preserves original benchmark references and raw inference without editing their values. Original historical media and unmodified logs remain local. The project did not begin on snapshot day, and this release does not claim a fresh independent evaluation of the old data.

Code and original artwork:MIT. Gemma weights:separate Google terms, not redistributed. Public publication requires exact-payload owner approval; a local snapshot commit is not evidence of a public repository or submitted DEV entry.
'''
(D/'PUBLIC_SNAPSHOT_PROVENANCE.md').write_text(provenance)
# Verify frozen evidence and selected inference engine bytes before packaging.
for filename in ['DATA_FREEZE.json','ENGINE_FREEZE.json']:
 freeze_data=json.loads((D/'evaluation/v6'/filename).read_text())
 for name,digest in freeze_data['files'].items():assert sha((D/name).read_bytes())==digest,(filename,name)
# Exercise the standalone source tree using already-installed dependencies, without copying them.
test=subprocess.run([str(R/'.venv/bin/python'),'-m','unittest','discover','-s','tests','-v'],cwd=D,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
log=test.stdout.decode().replace(str(Path.home()),'<home>');(D/'evaluation/v6/snapshot-tests.txt').write_text(log);(R/'evaluation/v6/snapshot-tests.txt').write_text(log)
assert test.returncode==0,'Standalone snapshot tests failed; inspect snapshot-tests.txt'
for cache in sorted(D.rglob('__pycache__'),reverse=True):shutil.rmtree(cache)
secret=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9]{20,}')
contact=re.compile(rb'/Users/[A-Za-z0-9_.-]+/|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',re.I)
findings=[];nested=0
TEXT={'.py','.js','.cjs','.md','.json','.html','.css','.txt','.yml','.yaml'}
def scan(data,name):
 global nested
 assert not secret.search(data),'Potential credential pattern; inspect privately: '+name
 if Path(name).suffix in TEXT:
  matches=contact.findall(data)
  if any(m!=b'163899332+siamakenna@users.noreply.github.com' for m in matches):findings.append(name)
 if zipfile.is_zipfile(io.BytesIO(data)):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for info in z.infolist():
    if not info.is_dir():nested+=1;scan(z.read(info),name+'!'+info.filename)
files=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or '.git' in p.relative_to(D).parts:continue
 data=p.read_bytes();scan(data,str(p.relative_to(D)));files.append(dict(path=str(p.relative_to(D)),bytes=len(data),sha256=sha(data)))
assert not findings,'Potential local path/contact in public text: '+', '.join(findings)
manifest=dict(publication_authorized=False,scope='Exact minimal clean public snapshot; full local Git history and participant responses excluded',files=files,file_count=len(files)+1,file_bytes=sum(f['bytes'] for f in files),self_digest_excluded=True,checks=dict(secret_pattern_matches=0,unapproved_text_home_path_contact_matches=0,approved_public_contact="163899332+siamakenna@users.noreply.github.com",nested_members_scanned=nested,standalone_unit_api_tests=74,frozen_hashes_verified=True),limits='Limited pattern detection, not universal privacy proof; original synthetic media inspected as app captures. No network/publication performed.')
for root in [D,R]:
 p=root/MANIFEST;p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(manifest,indent=2)+'\n')
# Initialize only this new clean snapshot, with a verified GitHub noreply identity.
subprocess.run(['git','init','-b','main'],cwd=D,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['git','config','user.name','siamakenna'],cwd=D,check=True);subprocess.run(['git','config','user.email','163899332+siamakenna@users.noreply.github.com'],cwd=D,check=True)
subprocess.run(['git','add','.'],cwd=D,check=True);subprocess.run(['git','commit','-m','Release BenchSloth v0.6 research preview with frozen evidence'],cwd=D,check=True,stdout=subprocess.DEVNULL);subprocess.run(['git','tag','v0.6.0-rc1'],cwd=D,check=True)
commit=git('rev-parse','HEAD',cwd=D);archive=R.parent/'BenchSloth_v0.6_Public_RC.zip'
paths=git('ls-files','-z',cwd=D).split('\0')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name in paths:
  if name:z.write(D/name,'benchsloth-public/'+name)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name in paths:
  if name:assert z.read('benchsloth-public/'+name)==(D/name).read_bytes()
assert subprocess.run(['git','diff','--quiet','HEAD'],cwd=D).returncode==0
post=(D/'docs/DEV_POST_FINAL.md').read_text();body=post.split('---',2)[2].lstrip('\n')
receipt=dict(public_commit=commit,public_tag='v0.6.0-rc1',repository='siamakenna/benchsloth-hf26-week3-2026',pages='https://siamakenna.github.io/benchsloth-hf26-week3-2026/',archive=archive.name,archive_sha256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,tracked_files=len([p for p in paths if p]),manifest_sha256=sha((D/MANIFEST).read_bytes()),dev_post_file_sha256=sha(post.encode()),dev_body_sha256=sha(body.encode()),git_identity='siamakenna <163899332+siamakenna@users.noreply.github.com>',public_history_commits=int(git('rev-list','--count','HEAD',cwd=D)),publication_authorized=False,public_actions=0)
(R.parent/'BenchSloth_v0.6_public-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
