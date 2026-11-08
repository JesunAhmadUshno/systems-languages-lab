"""Build level health and routing service: the Go Build idea, executed
in Python.

SPEC Track A (Go) Build asks for Go modules, native test tooling,
error handling, and context cancellation done the Go way.

This VM has no Go toolchain (rechecked 2026-11-05: go not found), so
this file is the executed Build reference in Python stdlib. The Go
Build source sits in go/ in this folder (proper module layout,
wrapped errors, context cancellation) and is labelled UNEXECUTED
there and in the REPORT.md. No claim says it was compiled or run.

Build hardening over Learn:
- A cancellation token shared by the pool. Workers check it before
  each job. A cancelled run probes nothing and counts skips.
- Structured error chains. ServiceError carries context and a cause
  and records each wrapping step in a chain list, the Python analogue
  of Go error wrapping with fmt.Errorf and the %w verb.
- Probe failures are classified (http_error, timeout) and returned
  as error records through the pool, not raised as bare exceptions.
- The registry grows to 10 endpoints and the router gains a vision
  route and a code model with a latency tie break.
"""
import queue
import threading


class ServiceError(Exception):
    """An error with a context string, a cause, and a chain list."""

    def __init__(self, context, cause=None):
        super().__init__(context)
        self.context = context
        self.cause = cause
        if isinstance(cause, ServiceError):
            self.chain = cause.chain + [context]
        elif cause is not None:
            self.chain = [str(cause), context]
        else:
            self.chain = [context]

    def __str__(self):
        return ": caused by: ".join(reversed(self.chain))


class CancelToken:
    """A shared cancellation signal, the analogue of context.Context."""

    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        self._event.set()

    @property
    def cancelled(self):
        return self._event.is_set()


# Build fixture registry. latency_ms is a scripted routing preference,
# not a measured wall time. error_kind is set only on failing probes.
ENDPOINTS_BUILD = [
    {
        "name": 'alpha-chat',
        "model": 'chat',
        "latency_ms": 40,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'beta-chat',
        "model": 'chat',
        "latency_ms": 25,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'gamma-chat',
        "model": 'chat',
        "latency_ms": 25,
        "probe_ok": False,
        "probe_note": '503 unavailable',
        "error_kind": 'http_error'
    },
    {
        "name": 'delta-chat',
        "model": 'chat',
        "latency_ms": 20,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'alpha-embed',
        "model": 'embed',
        "latency_ms": 15,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'beta-embed',
        "model": 'embed',
        "latency_ms": 30,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'gamma-vision',
        "model": 'vision',
        "latency_ms": 50,
        "probe_ok": False,
        "probe_note": 'probe timeout',
        "error_kind": 'timeout'
    },
    {
        "name": 'epsilon-vision',
        "model": 'vision',
        "latency_ms": 35,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'zeta-code',
        "model": 'code',
        "latency_ms": 18,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
    {
        "name": 'eta-code',
        "model": 'code',
        "latency_ms": 18,
        "probe_ok": True,
        "probe_note": '200 ok',
        "error_kind": None
    },
]

REQUEST_MODELS_BUILD = ["chat", "embed", "vision", "code", "chat", "vision",
                        "code", "embed", "chat", "code", "vision", "unknown"]


def probe_one_build(endpoint):
    """Probe one endpoint. Failures raise a chained ServiceError."""
    if not endpoint["probe_ok"]:
        base = ServiceError("probe transport failed: " + endpoint["probe_note"])
        raise ServiceError("probe " + endpoint["name"], cause=base)
    return {"name": endpoint["name"], "model": endpoint["model"],
            "healthy": True, "latency_ms": endpoint["latency_ms"],
            "note": endpoint["probe_note"], "error_kind": None,
            "error_chain": []}


def run_probes_build(endpoints, workers=4, token=None):
    """Probe every endpoint through a cancellable worker pool.

    Returns (records, info). Records are sorted by endpoint name, so
    the result is identical for any worker count. Info reports how
    many jobs were probed, skipped by cancellation, and the status.
    A probe failure becomes an unhealthy record with its error kind
    and chain, never an exception escaping the pool.
    """
    if workers < 1:
        raise ValueError("workers must be at least 1")
    if token is None:
        token = CancelToken()
    jobs = queue.Queue()
    results = queue.Queue()
    for ep in endpoints:
        jobs.put(ep)
    skipped = {"count": 0}
    lock = threading.Lock()

    def worker():
        while True:
            try:
                ep = jobs.get_nowait()
            except queue.Empty:
                return
            if token.cancelled:
                with lock:
                    skipped["count"] += 1
                jobs.task_done()
                continue
            try:
                results.put(probe_one_build(ep))
            except ServiceError as err:
                results.put({"name": ep["name"], "model": ep["model"],
                             "healthy": False, "latency_ms": ep["latency_ms"],
                             "note": ep["probe_note"],
                             "error_kind": ep["error_kind"],
                             "error_chain": err.chain})
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
    info = {"probed": len(out), "skipped": skipped["count"],
            "status": "cancelled" if skipped["count"] else "completed"}
    return out, info


def route_build(model, health_records):
    """Healthy only, lowest latency, name tie break. None if none."""
    cands = [r for r in health_records if r["model"] == model and r["healthy"]]
    if not cands:
        return None
    cands.sort(key=lambda r: (r["latency_ms"], r["name"]))
    return cands[0]["name"]


def run_routing_build(request_models, health_records):
    out = []
    for i, model in enumerate(request_models):
        target = route_build(model, health_records)
        out.append({"request": i + 1, "model": model,
                    "routed_to": target, "routed": target is not None})
    return out


def summarise_health_build(records):
    by_model = {}
    for r in records:
        slot = by_model.setdefault(r["model"], {"total": 0, "healthy": 0})
        slot["total"] += 1
        if r["healthy"]:
            slot["healthy"] += 1
    return {"endpoints_total": len(records),
            "endpoints_healthy": sum(1 for r in records if r["healthy"]),
            "by_model": dict(sorted(by_model.items()))}


def summarise_errors_build(records):
    per_kind = {}
    total = 0
    for r in records:
        if r["error_kind"]:
            total += 1
            per_kind[r["error_kind"]] = per_kind.get(r["error_kind"], 0) + 1
    return {"errors_total": total, "per_kind": dict(sorted(per_kind.items()))}


def summarise_routing_build(records):
    per_endpoint = {}
    routed = 0
    for rec in records:
        if rec["routed"]:
            routed += 1
            per_endpoint[rec["routed_to"]] = per_endpoint.get(rec["routed_to"], 0) + 1
    return {"requests_total": len(records), "requests_routed": routed,
            "requests_unrouted": len(records) - routed,
            "per_endpoint": dict(sorted(per_endpoint.items()))}
