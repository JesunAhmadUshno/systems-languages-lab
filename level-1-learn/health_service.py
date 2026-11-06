"""Model endpoint health and routing service: the Go Learn idea, executed
in Python.

SPEC Track A (Go) asks for a small service that P12's registry could point
at: a registry of model endpoints, health probes, and a router, with a
concurrent worker (goroutines and channels in Go).

This VM has no Go toolchain (checked 2026-11-05: go not found), so this file
is the executed reference implementation of the same logic in Python
stdlib. The worker pool uses threads plus queue.Queue, which is the closest
stdlib analogue of goroutines plus channels: jobs go in on a queue,
workers pull them, results come back on a second queue. The Go teaching
source sits beside this file in go/health_service.go and is labelled
unexecuted there and in the level README. No claim in this repo says the
Go source was compiled or run.

Probes are scripted, not network calls: each endpoint carries the probe
outcome a real HTTP probe would have returned (ok flag and a latency
figure). That keeps the run deterministic and offline. Routing and health
logic are the real logic; only the probe transport is a fixture.
"""
import queue
import threading

# Fixture registry. latency_ms is the scripted probe latency, used only
# as a routing preference value. It is not a measured wall time.
ENDPOINTS = [
    {"name": "alpha-chat", "model": "chat", "latency_ms": 40, "probe_ok": True, "probe_note": "200 ok"},
    {"name": "beta-chat", "model": "chat", "latency_ms": 25, "probe_ok": True, "probe_note": "200 ok"},
    {"name": "gamma-chat", "model": "chat", "latency_ms": 25, "probe_ok": False, "probe_note": "503 unavailable"},
    {"name": "alpha-embed", "model": "embed", "latency_ms": 15, "probe_ok": True, "probe_note": "200 ok"},
    {"name": "beta-embed", "model": "embed", "latency_ms": 30, "probe_ok": True, "probe_note": "200 ok"},
    {"name": "gamma-vision", "model": "vision", "latency_ms": 50, "probe_ok": False, "probe_note": "probe timeout"},
]

# Routing requests used by the runner and the tests, in order.
REQUEST_MODELS = ["chat", "chat", "embed", "vision", "chat", "embed", "vision", "chat"]


def probe_one(endpoint):
    """One scripted probe. Returns a health record for one endpoint."""
    return {
        "name": endpoint["name"],
        "model": endpoint["model"],
        "healthy": bool(endpoint["probe_ok"]),
        "latency_ms": endpoint["latency_ms"],
        "note": endpoint["probe_note"],
    }


def run_probes(endpoints, workers=3):
    """Probe every endpoint through a worker pool.

    Jobs travel on an input queue, results on an output queue. The
    returned list is sorted by endpoint name, so the result is identical
    for any worker count. That determinism is test enforced.
    """
    if workers < 1:
        raise ValueError("workers must be at least 1")
    jobs = queue.Queue()
    results = queue.Queue()
    for ep in endpoints:
        jobs.put(ep)

    def worker():
        while True:
            try:
                ep = jobs.get_nowait()
            except queue.Empty:
                return
            results.put(probe_one(ep))
            jobs.task_done()

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    out = []
    while not results.empty():
        out.append(results.get())
    out.sort(key=lambda r: r["name"])
    return out


def route(model, health_records):
    """Pick the endpoint for one request.

    Rule: healthy endpoints for the model only, lowest scripted latency
    first, name ascending as the tie break. Returns the endpoint name,
    or None when no healthy endpoint serves the model.
    """
    candidates = [r for r in health_records if r["model"] == model and r["healthy"]]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (r["latency_ms"], r["name"]))
    return candidates[0]["name"]


def run_routing(request_models, health_records):
    """Route a list of requests. Returns one record per request."""
    out = []
    for i, model in enumerate(request_models):
        target = route(model, health_records)
        out.append({"request": i + 1, "model": model, "routed_to": target, "routed": target is not None})
    return out


def summarise_health(health_records):
    by_model = {}
    for r in health_records:
        slot = by_model.setdefault(r["model"], {"total": 0, "healthy": 0})
        slot["total"] += 1
        if r["healthy"]:
            slot["healthy"] += 1
    return {
        "endpoints_total": len(health_records),
        "endpoints_healthy": sum(1 for r in health_records if r["healthy"]),
        "by_model": dict(sorted(by_model.items())),
    }


def summarise_routing(routing_records):
    per_endpoint = {}
    routed = 0
    for rec in routing_records:
        if rec["routed"]:
            routed += 1
            per_endpoint[rec["routed_to"]] = per_endpoint.get(rec["routed_to"], 0) + 1
    return {
        "requests_total": len(routing_records),
        "requests_routed": routed,
        "requests_unrouted": len(routing_records) - routed,
        "per_endpoint": dict(sorted(per_endpoint.items())),
    }
