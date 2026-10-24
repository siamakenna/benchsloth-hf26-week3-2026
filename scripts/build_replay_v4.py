"""Self-contained recorded-agent replay plus relative local media, no server required."""
import json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sample=json.loads((R/'static/agent-sample.json').read_text())
p=R/'evaluation/v4/holdout-4b/summary.json';evaluation=json.loads(p.read_text()) if p.exists() else {'status':'Prospective run not completed; no score claimed.'}
source=(R/'static/index.html').read_text().replace('const REPLAY = false','const REPLAY = true')
source=source.replace('<script>','<script>\nwindow.PREPARED_SAMPLE='+json.dumps(sample).replace('<','\\u003c')+';\nwindow.PREPARED_EVALUATION='+json.dumps(evaluation).replace('<','\\u003c')+';\n',1)
(R/'demo/index.html').write_text(source)
video=R/'assets/v4/demo-captioned.webm'
if video.exists():
 target=R/'demo/assets/v4/demo-captioned.webm';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(video,target)
print('Built recorded replay:',len(source.encode()),'bytes; actual trace nodes:',len(sample['agent']['trace']))
