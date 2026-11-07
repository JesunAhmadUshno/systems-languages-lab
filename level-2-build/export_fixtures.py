"""Export the Build fixtures to fixtures_build.json for the live dashboard.

The dashboard in site/ re-runs the Build checker and the Deep workload in
the browser. results_build.json carries only rule flags per tool, not the
manifest fields, and only name-sorted health records, not the registry
order the Deep workload cycles through. This export writes those inputs
straight from the Python constants, so nothing is retyped by hand.
tests/test_site_fixtures.py fails if the file drifts from the constants.
Run: python3 level-2-build/export_fixtures.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import manifest_build as mb  # noqa: E402
import service_build as sb  # noqa: E402

OUT = os.path.join(HERE, "fixtures_build.json")


def build_export():
    return {
        "source": "level-2-build/service_build.py and level-2-build/manifest_build.py",
        "endpoints_build": sb.ENDPOINTS_BUILD,
        "request_models_build": sb.REQUEST_MODELS_BUILD,
        "tools_build": mb.TOOLS_BUILD,
        "rule_ids_build": mb.RULE_IDS_BUILD,
        "severity": mb.SEVERITY,
    }


def main():
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(build_export(), fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
