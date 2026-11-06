# Two Languages, One Python Reference: What a Profile Found

By Jesun Ahmad Ushno
Date: 2026-11-05
Status: DRAFT, written fan-out for P21 systems-languages-lab v1.0. Not posted.

## The problem

ML platform work runs on systems languages: Go services that route
to model endpoints, Rust tools that check configuration before it
can do damage. This project teaches both shapes by building them
three times, small, working, then profiled, instead of touring
syntax.

Repository: https://github.com/JesunAhmadUshno/systems-languages-lab

## Honest scope, stated first

Go and Rust sources are UNEXECUTED at every level: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. Every executed level is a Python standard library reference only, run on the Muse VM. All health probes and tool manifests are scripted fixtures, authored for teaching: no real HTTP endpoint was served or probed, and no real MCP manifest file was read. The Deep speedup is an order of magnitude effect, not a constant: timing on a shared VM varies by run, and the exact ratio is a property of the recorded run.

## What was built

Learn: a Python reference for a Go-shaped health and routing
service (worker pool, registry, router) and a Rust-shaped tool
manifest checker (5 rules). Health 4 of 6 endpoints healthy,
router 6 of 8 requests routed, checker 4 of 6 tools unsafe with
7 flags. Grade 7,900 of 10,000.

Build: a cancellable worker pool with structured error chains
and an extended 8 rule checker with severities, still in Python.
Health 8 of 10 endpoints healthy with 2 classified errors, a
pre-cancelled run probing 0 and skipping 10, router 11 of 12
requests routed, checker 5 of 8 tools unsafe with 14 flags.
Grade 7,800 of 10,000.

Deep: a profile and fix bottleneck study in Python, a Rust Rule
trait sharing design as UNEXECUTED source, and a Go pprof study
design as UNEXECUTED source. Grade 7,900 of 10,000.

## The main result

On the Python reference runs, Learn found 4 of 6 endpoints healthy and routed 6 of 8 requests, Build found 8 of 10 endpoints healthy and routed 11 of 12 requests, and the Deep indexed router cut the median routing batch from 2.434 s to 0.0765 s on 200 endpoints and 20,000 requests with routing records identical to baseline, all in Python only on the Muse VM with Go and Rust sources unexecuted.

In detail. Learn routing, in order over 8 requests: beta-chat,
beta-chat, alpha-embed, unrouted, beta-chat, alpha-embed,
unrouted, beta-chat. The two unrouted requests are vision, whose
only endpoint is unhealthy. Build routing: 11 of 12 routed
(delta-chat 3, alpha-embed 2, epsilon-vision 3, eta-code 3), 1
unrouted for an unknown model. Deep: cProfile over the baseline
workload (696,002 calls, 1.856 s under the profiler) put
route_build at 1.780 s cumulative, 95.9 percent of routing time,
because it filters and sorts healthy candidates on every
request. The indexed router builds the best healthy record per
model once, then answers each request with one dict lookup, and
is charged for that build in its timing. Routed 16,000 of
20,000 in both routers, with identical records.

The speedup sentence needs its caveat in the same breath: the
median ratio in the recorded run is 31.8 times, batch times were
1.9081, 2.5962, 2.6068, 2.434, and 1.9084 s baseline against
0.1301, 0.0765, 0.1065, 0.0316, and 0.0619 s indexed, and a
quieter run measured different medians. The direction and the
order of magnitude are stable; the exact ratio is not a
constant, and no piece in this set treats it as one.

## The verdict

The Python reference proves the routing and checking rules and
finds a real bottleneck shape: repeated sorting of a fixed
answer. It does not prove Go concurrency, Rust ownership, or
any compiled behaviour. That proof is the first v1.1 item,
named in ROADMAP.md: compile both tracks on a node with the
toolchains and run the Go pprof study for real.

## Limits

- Python reference only: Go and Rust sources are UNEXECUTED.
- Scripted fixtures: no real HTTP probe, no real MCP manifest.
- Small authored fixtures at Learn and Build (6 to 10 endpoints).
- Timing noise on a shared VM: order of magnitude, not constant.
- Run on the Muse VM, not the assigned BlackBoxV3 fleet node.

## Future

The v1.1 backlog is ROADMAP.md in the repo: the toolchain port,
the Go pprof study run for real, the Go code reading note, real
HTTP probes and a real MCP manifest read, and a dedicated node
timing repeat. None of that is claimed as done.

Tests: 46 checks in total (15 Learn, 22 Build, 9 Deep), plus
the scaffold smoke test.
