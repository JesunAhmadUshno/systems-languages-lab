"""Parity test for level-2-build/fixtures_build.json.

The live dashboard reads the Build fixtures from that JSON export. This
test fails if the export drifts from the Python constants it came from.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

import export_fixtures as ef  # noqa: E402


class TestSiteFixtures(unittest.TestCase):
    def test_export_matches_constants(self):
        with open(ef.OUT, encoding="utf-8") as fh:
            on_disk = json.load(fh)
        self.assertEqual(on_disk, json.loads(json.dumps(ef.build_export())))

    def test_export_sizes(self):
        data = ef.build_export()
        self.assertEqual(len(data["endpoints_build"]), 10)
        self.assertEqual(len(data["tools_build"]), 8)
        self.assertEqual(len(data["request_models_build"]), 12)


if __name__ == "__main__":
    unittest.main()
