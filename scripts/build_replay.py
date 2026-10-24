"""Build a dependency-free static replay; never substitutes for a model request."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from attention import sample_plan as sample
prepared=sample()
(ROOT/'static/sample.json').write_text(json.dumps(prepared,indent=2)+'\n')
s=(ROOT/'static/index.html').read_text().replace('const REPLAY = false','const REPLAY = true')
s=s.replace('<script>','<script>\nwindow.PREPARED_SAMPLE = '+json.dumps(prepared).replace('<','\\u003c')+';\n',1)
(ROOT/'demo/index.html').write_text(s)
print('Built demo/index.html: prepared output only; no API or inference')
