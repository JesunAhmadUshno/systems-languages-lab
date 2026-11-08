"""Repeat timing study for the Deep fix: more repetitions and a size sweep.

The recorded Deep run (results_deep.json) used 5 repetitions on a shared VM
and one workload size. This script adds, without touching that file:
- 30 interleaved paired repetitions of baseline and indexed routing on the
  same 200 endpoint, 20,000 request workload, with a percentile bootstrap
  95 percent interval on the median paired ratio (10,000 resamples, seed 0);
- a sweep over registry sizes 50 to 800 endpoints (20,000 requests, 5
  repetitions each, median), to show how each arm scales.
Every run records the machine it ran on. Timings vary by machine and load.
Run: python3 level-3-deep/timing_repeats.py (about one to two minutes).
"""
import datetime
import json
import os
import platform
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import profile_deep as pd  # noqa: E402

sb = pd.sb
OUT = os.path.join(HERE, "results_deep_repeats.json")


def _time(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def paired_study(reps=30, resamples=10000, seed=0):
    records, _ = sb.run_probes_build(pd.make_workload_endpoints(), workers=4)
    requests = pd.make_workload_requests()
    base_fn = lambda: sb.run_routing_build(requests, records)  # noqa: E731
    idx_fn = lambda: pd.IndexedRouter(records).run_routing(requests)  # noqa: E731
    assert base_fn() == idx_fn()
    base_fn()
    idx_fn()
    base, idx = [], []
    for _ in range(reps):
        base.append(_time(base_fn))
        idx.append(_time(idx_fn))
    ratios = [b / i for b, i in zip(base, idx)]
    rng = random.Random(seed)
    boot = sorted(statistics.median(rng.choices(ratios, k=len(ratios))) for _ in range(resamples))
    return {
        "repetitions": reps,
        "baseline_times_s": [round(t, 4) for t in base],
        "indexed_times_s": [round(t, 4) for t in idx],
        "baseline_median_s": round(statistics.median(base), 4),
        "indexed_median_s": round(statistics.median(idx), 4),
        "median_paired_ratio": round(statistics.median(ratios), 2),
        "paired_ratio_min": round(min(ratios), 2),
        "paired_ratio_max": round(max(ratios), 2),
        "bootstrap_ci95_median_ratio": [round(boot[int(0.025 * resamples)], 2),
                                        round(boot[int(0.975 * resamples) - 1], 2)],
        "bootstrap": {"resamples": resamples, "seed": seed, "method": "percentile"},
    }


def sweep(sizes=(50, 100, 200, 400, 800), reps=5):
    requests = pd.make_workload_requests()
    out = []
    for n in sizes:
        records, _ = sb.run_probes_build(pd.make_workload_endpoints(n), workers=4)
        base_fn = lambda: sb.run_routing_build(requests, records)  # noqa: E731
        idx_fn = lambda: pd.IndexedRouter(records).run_routing(requests)  # noqa: E731
        identical = base_fn() == idx_fn()
        b = pd.time_median(base_fn, repetitions=reps)
        i = pd.time_median(idx_fn, repetitions=reps)
        out.append({"endpoints": n, "requests": len(requests), "records_identical": identical,
                    "baseline_median_s": b["median_s"], "indexed_median_s": i["median_s"]})
    return out


def main():
    results = {
        "recorded_on": datetime.date.today().isoformat(),
        "machine": {"platform": platform.platform(), "machine": platform.machine(),
                    "python": platform.python_version(), "cpu_count": os.cpu_count()},
        "method": "perf_counter; paired arms interleaved per repetition after one warmup each",
        "paired": paired_study(),
        "sweep": sweep(),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
        fh.write("\n")
    p = results["paired"]
    print("median paired ratio", p["median_paired_ratio"], "ci95", p["bootstrap_ci95_median_ratio"])
    for row in results["sweep"]:
        print(row)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
