#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m compileall -q app.py attention.py server.py
python -m unittest discover -s tests -v
python eval/evaluate.py
python - <<'PY'
from fastapi.testclient import TestClient
from app import app
c = TestClient(app)
for endpoint in ('/', '/api/sample', '/api/health'):
    r = c.get(endpoint)
    print('HTTP', r.status_code, endpoint)
    assert r.status_code == 200
assert c.get('/api/sample').json()['mode'] == 'illustrative-prepared-example'
PY
if command -v node >/dev/null 2>&1; then
  tmp_js="$(mktemp "${TMPDIR:-/tmp}/benchsloth-check-XXXXXX.js")"
  python - "$tmp_js" <<'PY'
from pathlib import Path
import re,sys
html=Path('static/index.html').read_text()
js=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
Path(sys.argv[1]).write_text(js)
PY
  node --check "$tmp_js"
  rm -f "$tmp_js"
  echo "Front-end JavaScript syntax: OK"
fi
