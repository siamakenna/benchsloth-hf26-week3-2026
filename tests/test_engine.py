import json
import pathlib
import unittest
from app import fixed_duration, validate_model_output

ROOT = pathlib.Path(__file__).resolve().parents[1]
class EngineTest(unittest.TestCase):
    def test_duration_exact(self):
        for source, minutes in [("Wait 5 min", 5), ("Incubate for 2 hours", 120), ("Wait 0.5 h", 30)]:
            self.assertEqual(fixed_duration(source)[0], minutes)
    def test_ambiguous_must_not_start_timer(self):
        for source in ["Wash 3 times for 5 minutes each", "Incubate overnight", "Wait 10-15 min", "Wait about 30 min", "Incubate for 5 min then 20 min", "Wait until dry", "Wait 2 h or longer", "Wait 0 min"]:
            self.assertIsNone(fixed_duration(source)[0], source)
    def test_sample_has_3_timed_rest_windows_and_two_reviews(self):
        sample = json.loads((ROOT / 'eval/sample_prepared.json').read_text())
        result = validate_model_output(sample['protocol'], sample)
        self.assertEqual(result['documented_rest_minutes'], 110)
        self.assertEqual(result['rest_windows'], 3)
        self.assertEqual(result['review_needed'], 2)
    def test_hallucinated_line_rejected(self):
        text = '1. Wait for 5 min.\n2. Rinse.'
        sample = {'steps':[{'source':'1. Wait for 5 min.', 'label':'Wait', 'kind':'hands_off'}, {'source':'2. Heat the solution.', 'label':'Heat', 'kind':'hands_on'}]}
        with self.assertRaisesRegex(ValueError, 'source'):
            validate_model_output(text, sample)
    def test_dropped_or_reordered_rejected(self):
        text = '1. Wait for 5 min.\n2. Rinse.'
        with self.assertRaisesRegex(ValueError, 'covered'):
            validate_model_output(text, {'steps': []})
        with self.assertRaisesRegex(ValueError, 'source'):
            validate_model_output(text, {'steps':[{'source':'2. Rinse.', 'label':'Rinse', 'kind':'hands_on'}, {'source':'1. Wait for 5 min.', 'label':'Wait', 'kind':'hands_off'}]})
    def test_model_cannot_label_active_mixing_as_rest(self):
        source = 'Mix continuously for 30 minutes.'
        result = validate_model_output(source, {'steps':[{'source':source, 'label':'Mix','kind':'hands_off'}]})
        self.assertEqual(result['documented_rest_minutes'], 0)
        self.assertEqual(result['steps'][0]['kind'], 'review')
        self.assertTrue(result['steps'][0]['review_needed'])
    def test_interrupted_wait_not_admitted_as_rest(self):
        source = 'Incubate for 40 min, stirring occasionally.'
        result = validate_model_output(source, {'steps':[{'source':source, 'label':'Wait','kind':'hands_off'}]})
        self.assertEqual(result['documented_rest_minutes'], 0)
        self.assertTrue(result['steps'][0]['review_needed'])
    def test_time_not_silently_rebranded_rest(self):
        result = validate_model_output('Mix for 5 minutes', {'steps':[{'source':'Mix for 5 minutes', 'label':'Mix', 'kind':'hands_on'}]})
        self.assertEqual(result['documented_rest_minutes'], 0)
        self.assertIsNone(result['steps'][0]['rest_minutes'])

if __name__ == '__main__': unittest.main()
