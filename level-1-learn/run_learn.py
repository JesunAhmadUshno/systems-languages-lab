"""Runner for Level 1, Learn: health service plus manifest checker.

Writes results_learn.json beside this file. The output holds counts and
names only: no wall time, no timestamps, so two runs produce a byte
identical file. Run: python3 run_learn.py (from this folder or the repo
root, the paths below are file relative).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import health_service as hs
import manifest_checker as mc


def build_results():
    health_records = hs.run_probes(hs.ENDPOINTS, workers=3)
    routing_records = hs.run_routing(hs.REQUEST_MODELS, health_records)
    tool_records = mc.check_all(mc.TOOLS)
    return {
        "level": "1-learn",
        "executed_language": "python",
        "go_toolchain": "missing on this VM (go not found, 2026-11-05)",
        "rust_toolchain": "missing on this VM (rustc not found, 2026-11-05)",
        "health": hs.summarise_health(health_records),
        "health_records": health_records,
        "routing": hs.summarise_routing(routing_records),
        "routing_records": routing_records,
        "manifest": mc.summarise(tool_records),
        "tool_records": tool_records,
    }


def main():
    results = build_results()
    out_path = os.path.join(HERE, "results_learn.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    h = results["health"]
    r = results["routing"]
    m = results["manifest"]
    print("health: %d of %d endpoints healthy" % (h["endpoints_healthy"], h["endpoints_total"]))
    print("routing: %d of %d requests routed, %d unrouted" % (r["requests_routed"], r["requests_total"], r["requests_unrouted"]))
    print("manifest: %d of %d tools unsafe, %d total flags" % (m["tools_unsafe"], m["tools_total"], m["total_flags"]))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
