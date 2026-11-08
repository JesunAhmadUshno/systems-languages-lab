"""Portfolio standard checks: the required files exist and no public file carries a grade.

There is no lock-hash test: the repo is not pre-registered (PROPOSAL.md says why).
"""
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["README.md", "PROPOSAL.md", "REPORT.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
            "docs/decisions/0001-keep-level-folders.md",
            "level-1-learn/results_learn.json", "level-2-build/results_build.json",
            "level-2-build/fixtures_build.json", "level-3-deep/results_deep.json",
            "level-3-deep/results_deep_repeats.json"]
# Internal grading never appears in a public file.
GRADE = re.compile(r"of 10,000|/ ?10,?000\b|Grade:|Grade \(of|grades? on record|house 10,000 scale|parseGrade")


class TestLayout(unittest.TestCase):
    def test_required_files_exist(self):
        missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
        self.assertEqual(missing, [], "missing: " + ", ".join(missing))

    def test_readme_opens_with_the_abstract(self):
        text = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
        for label in ("**Question.**", "**Headline.**", "**Field.**", "**Job family.**", "**Verdict.**"):
            self.assertIn(label, text)
        stages = re.findall(r"^- (\w+): ([A-Z]+)(?: \d{4}-\d{2}-\d{2})?$", text, re.M)
        self.assertEqual([s for s, _ in stages],
                         ["Question", "Proposal", "Baseline", "Build", "Evaluate", "Report", "Review", "Release"])

    def test_no_public_grade(self):
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        if not files:  # not a git checkout: scan the working tree
            files = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT)
                     if ".git" not in d and "node_modules" not in d for f in fs]
        hits = []
        for p in files:
            if p.startswith("tests/") or not p.endswith((".md", ".jsx", ".js", ".mjs", ".html", ".cff")):
                continue
            with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
                hits += [f"{p}: {m.group(0)}" for m in GRADE.finditer(fh.read())]
        self.assertEqual(hits, [], "grades are internal only")


if __name__ == "__main__":
    unittest.main()
