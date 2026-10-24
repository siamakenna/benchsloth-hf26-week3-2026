"""Reproducible timing-guardrail eval (NOT an LLM model-accuracy claim)."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import fixed_duration, infer_local_model, validate_model_output

root = Path(__file__).parent
cases = json.loads((root/'timing_gold.json').read_text())
correct = []
for case in cases:
    observed, reason = fixed_duration(case['text'])
    correct.append(observed == case['minutes'])
    if observed != case['minutes']:
        print('MISMATCH',repr(case['text']),case['minutes'],observed,reason)
print(json.dumps({'evaluation':'deterministic timing parser only', 'cases':len(cases), 'correct':sum(correct),'accuracy':sum(correct)/len(cases)},indent=2))
if '--live' in sys.argv:
    # Live LLM evaluation: evaluates exact line coverage only, not semantic validity.
    sample=json.loads((root/'sample_prepared.json').read_text())
    try:
        output = validate_model_output(sample['protocol'], infer_local_model(sample['protocol']))
        print(json.dumps({'evaluation':'actual local model', 'model':output['engine'], 'accepted':True,
             'step_count':len(output['steps']), 'hands_off_count':sum(s['kind']=='hands_off' for s in output['steps']),
             'timed_rest_windows':output['rest_windows'], 'review_required':output['review_needed']},indent=2))
    except Exception as exc:
        print(json.dumps({'evaluation':'actual local model','accepted':False,'error':str(exc)}))
        raise SystemExit(1)
