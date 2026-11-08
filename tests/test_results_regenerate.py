"""The committed results are regenerated from the code, without writing any file.

Learn, Build and the fixture export must match byte for byte. The Deep file's timing
section is measured wall time and changes per run, so only its deterministic section is
rebuilt and compared. The repeat timing file is checked for internal consistency: its
stored median paired ratio must follow from its stored times.
"""
import importlib.util
import json
import os
import statistics
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    sys.path.insert(0, os.path.join(ROOT, os.path.dirname(rel)))
    spec = importlib.util.spec_from_file_location(os.path.basename(rel)[:-3], os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def as_written(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def committed(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


class TestResultsRegenerate(unittest.TestCase):
    def test_learn(self):
        self.assertEqual(as_written(load("level-1-learn/run_learn.py").build_results()),
                         committed("level-1-learn/results_learn.json"))

    def test_build(self):
        self.assertEqual(as_written(load("level-2-build/run_build.py").build_results()),
                         committed("level-2-build/results_build.json"))

    def test_fixture_export(self):
        self.assertEqual(as_written(load("level-2-build/export_fixtures.py").build_export()),
                         committed("level-2-build/fixtures_build.json"))

    def test_deep_deterministic_section(self):
        deterministic, _timing = load("level-3-deep/profile_deep.py").run_study()
        recorded = json.loads(committed("level-3-deep/results_deep.json"))
        self.assertEqual(json.loads(json.dumps(deterministic)), recorded["deterministic"])
        self.assertTrue(recorded["deterministic"]["routing_records_identical"])

    def test_repeat_ratio_follows_from_stored_times(self):
        p = json.loads(committed("level-3-deep/results_deep_repeats.json"))["paired"]
        ratios = [b / i for b, i in zip(p["baseline_times_s"], p["indexed_times_s"])]
        self.assertEqual(len(ratios), p["repetitions"])
        # Stored times are rounded to 4 decimals (indexed is about 3 ms), so allow 2 percent.
        self.assertLess(abs(statistics.median(ratios) - p["median_paired_ratio"]) / p["median_paired_ratio"], 0.02)
        lo, hi = p["bootstrap_ci95_median_ratio"]
        self.assertTrue(lo <= p["median_paired_ratio"] <= hi)


if __name__ == "__main__":
    unittest.main()
