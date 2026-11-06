"""Runner for Level 2, Build: hardened service plus extended checker.

Writes results_build.json beside this file. The output holds counts
and names only: no wall time, no timestamps, so two runs produce a
byte identical file. Run: python3 run_build.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import manifest_build as mb
import service_build as sb


def build_results():
    records, info = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4)
    routing = sb.run_routing_build(sb.REQUEST_MODELS_BUILD, records)
    token = sb.CancelToken()
    token.cancel()
    _cancelled_records, cancel_info = sb.run_probes_build(
        sb.ENDPOINTS_BUILD, workers=4, token=token)
    tool_records = mb.check_all_build(mb.TOOLS_BUILD)
    return {
        "level": "2-build",
        "executed_language": "python",
        "go_toolchain": "missing on this VM (go not found, rechecked 2026-11-05)",
        "rust_toolchain": "missing on this VM (rustc and cargo not found, rechecked 2026-11-05)",
        "health": sb.summarise_health_build(records),
        "health_records": records,
        "routing": sb.summarise_routing_build(routing),
        "routing_records": routing,
        "errors": sb.summarise_errors_build(records),
        "pool": info,
        "cancellation": cancel_info,
        "manifest": mb.summarise_build(tool_records),
        "tool_records": tool_records,
        "duplicate_names": mb.find_duplicates(mb.TOOLS_BUILD),
    }


def main():
    results = build_results()
    out_path = os.path.join(HERE, "results_build.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    h = results["health"]
    r = results["routing"]
    m = results["manifest"]
    print("health: %d of %d endpoints healthy" % (h["endpoints_healthy"], h["endpoints_total"]))
    print("routing: %d of %d requests routed, %d unrouted" % (r["requests_routed"], r["requests_total"], r["requests_unrouted"]))
    print("manifest: %d of %d tools unsafe, %d total flags" % (m["tools_unsafe"], m["tools_total"], m["total_flags"]))
    print("cancellation: %s, %d skipped" % (results["cancellation"]["status"], results["cancellation"]["skipped"]))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
