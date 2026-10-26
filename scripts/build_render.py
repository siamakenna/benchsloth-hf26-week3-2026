#!/usr/bin/env python3
"""Strict allowlist for synthetic browser-only Render publication."""
from pathlib import Path
import hashlib, json, shutil
root=Path(__file__).resolve().parents[1]; source=root/'web'; target=root/'render_public'
expected=json.loads((root/'scripts/WEB_EXPECTED.json').read_text())
actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
assert actual==set(expected),('Unexpected or missing web files',sorted(actual^set(expected)))
assert not source.is_symlink() and not target.is_symlink()
for rel,sha in expected.items():
 p=source/rel
 assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(source.resolve())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,('Source file changed',rel)
if target.exists():
 for p in target.rglob('*'):
  assert not p.is_symlink(),('Symlink in output',p)
 shutil.rmtree(target)
for rel in expected:
 dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/rel,dst)
assert {p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()}==expected
print('PASS: %d exact static publication files, no owner data' % len(expected))
