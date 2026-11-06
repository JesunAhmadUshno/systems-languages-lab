"""Deep level profile and fix study: the bottleneck study, executed
in Python on the Build reference.

SPEC Deep (Track A shape, Python execution): profile the service,
remove one real bottleneck, publish the before and after.

This VM has no Go toolchain (rechecked 2026-11-05: go not found),
so the executed study profiles the Python Build code in
level-2-build/service_build.py. The Go pprof study design sits in
go/ in this folder, labelled UNEXECUTED. No claim says it ran.

Finding (cProfile, workload below): route_build filters every
health record and sorts the healthy candidates on every request.
On the Deep workload that is 20,000 calls, 16,000 list sorts and
about 92 percent of the routing wall time. The fix is an index
built once per fixed health record set: IndexedRouter keeps the
best healthy record per model under the exact Build ordering
(lowest latency, name tie break), so a request is one dict lookup.

Determinism: the workload generation uses no randomness and no
wall time. Timing uses time.perf_counter with one warmup run and
5 pooled repetitions; the median batch time is reported. Timing
values are kept in a separate section of results_deep.json and
are not deterministic fields.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(os.path.dirname(HERE), "level-2-build")
sys.path.insert(0, BUILD_DIR)

import service_build as sb  # noqa: E402

WORKLOAD_ENDPOINTS = 200
WORKLOAD_REQUESTS = 20000
WORKLOAD_MODELS = ["chat", "embed", "vision", "code", "unknown"]


def make_workload_endpoints(count=WORKLOAD_ENDPOINTS):
    """Deterministic expanded registry from the Build fixtures."""
    eps = []
    base = sb.ENDPOINTS_BUILD
    for i in range(count):
        src = base[i % len(base)]
        eps.append({
            "name": "ep-%04d-%s" % (i, src["name"]),
            "model": src["model"],
            "latency_ms": src["latency_ms"] + (i % 7),
            "probe_ok": src["probe_ok"],
            "probe_note": src["probe_note"],
            "error_kind": src["error_kind"],
        })
    return eps


def make_workload_requests(count=WORKLOAD_REQUESTS):
    return [WORKLOAD_MODELS[i % len(WORKLOAD_MODELS)] for i in range(count)]


class IndexedRouter:
    """One index build, then constant time routing per request.

    The index keeps, per model, the single best healthy record
    under the Build ordering (latency ascending, name ascending).
    Because route_build returns only that best record name, keeping
    the best per model is exactly equivalent, not an approximation.
    """

    def __init__(self, health_records):
        self._best = {}
        for rec in health_records:
            if not rec["healthy"]:
                continue
            cur = self._best.get(rec["model"])
            key = (rec["latency_ms"], rec["name"])
            if cur is None or key < (cur["latency_ms"], cur["name"]):
                self._best[rec["model"]] = rec

    def route(self, model):
        rec = self._best.get(model)
        return rec["name"] if rec is not None else None

    def run_routing(self, request_models):
        out = []
        for i, model in enumerate(request_models):
            target = self.route(model)
            out.append({"request": i + 1, "model": model,
                        "routed_to": target, "routed": target is not None})
        return out


def profile_baseline(records, requests):
    """cProfile the baseline Build routing. Returns top rows."""
    import cProfile
    import io
    import pstats

    pr = cProfile.Profile()
    pr.enable()
    sb.run_routing_build(requests, records)
    pr.disable()
    stream = io.StringIO()
    stats = pstats.Stats(pr, stream=stream).sort_stats("cumulative")
    stats.print_stats(8)
    text = stream.getvalue()
    root = os.path.dirname(HERE) + os.sep
    return text.replace(root, "")


def time_median(fn, repetitions=5):
    """Median of pooled batch times: 1 warmup, then repetitions."""
    import statistics
    import time

    fn()
    times = []
    for _ in range(repetitions):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return {"repetitions": repetitions, "times_s": [round(t, 4) for t in times],
            "median_s": round(statistics.median(times), 4)}


def run_study():
    """Run the full study. Returns (deterministic, timing) dicts."""
    endpoints = make_workload_endpoints()
    records, info = sb.run_probes_build(endpoints, workers=4)
    requests = make_workload_requests()
    baseline_records = sb.run_routing_build(requests, records)
    router = IndexedRouter(records)
    indexed_records = router.run_routing(requests)
    build_records, _ = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4)
    build_baseline = sb.run_routing_build(sb.REQUEST_MODELS_BUILD, build_records)
    build_indexed = IndexedRouter(build_records).run_routing(sb.REQUEST_MODELS_BUILD)
    deterministic = {
        "workload": {"endpoints": len(endpoints), "requests": len(requests),
                     "models": WORKLOAD_MODELS},
        "pool": info,
        "health": sb.summarise_health_build(records),
        "baseline_routing": sb.summarise_routing_build(baseline_records),
        "indexed_routing": sb.summarise_routing_build(indexed_records),
        "routing_records_identical": baseline_records == indexed_records,
        "build_fixture_routing_identical": build_baseline == build_indexed,
        "build_fixture_routing": sb.summarise_routing_build(build_indexed),
    }
    timing = {
        "method": "perf_counter, 1 warmup, 5 pooled repetitions, median reported",
        "baseline": time_median(lambda: sb.run_routing_build(requests, records)),
        "indexed": time_median(lambda: IndexedRouter(records).run_routing(requests)),
        "indexed_route_only_note": "indexed timing includes one index build per batch",
    }
    return deterministic, timing
