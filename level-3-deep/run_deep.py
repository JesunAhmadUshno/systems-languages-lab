"""Runner for Level 3, Deep: profile and fix study on the Build code.

Writes results_deep.json beside this file. The deterministic
section (counts, names, equality flags) is identical across runs.
The timing section holds measured wall times and varies per run,
so the file as a whole is not byte identical; the runner verifies
the deterministic section across two in-process study runs instead.
Run: python3 run_deep.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import profile_deep as pd


def build_results():
    deterministic, timing = pd.run_study()
    det2, _timing2 = pd.run_study()
    return {
        "level": "3-deep",
        "executed_language": "python",
        "go_toolchain": "missing on this VM (go not found, rechecked 2026-11-05)",
        "rust_toolchain": "missing on this VM (rustc and cargo not found, rechecked 2026-11-05)",
        "deterministic": deterministic,
        "deterministic_repeat_identical": deterministic == det2,
        "timing": timing,
        "profile_top": pd.profile_baseline(
            pd.sb.run_probes_build(pd.make_workload_endpoints(), workers=4)[0],
            pd.make_workload_requests()).splitlines()[:40],
    }


def main():
    results = build_results()
    out_path = os.path.join(HERE, "results_deep.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    d = results["deterministic"]
    t = results["timing"]
    print("workload: %d endpoints, %d requests" % (d["workload"]["endpoints"], d["workload"]["requests"]))
    print("routing identical baseline vs indexed:", d["routing_records_identical"])
    print("build fixture identical:", d["build_fixture_routing_identical"])
    print("deterministic repeat identical:", results["deterministic_repeat_identical"])
    print("baseline median_s:", t["baseline"]["median_s"], "indexed median_s:", t["indexed"]["median_s"])
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
