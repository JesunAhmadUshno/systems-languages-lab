# DEEP-SPEC: systems-languages-lab (P21), Level 3 Deep (compressed)

Written first, before Deep code, per the house engineering pipeline.
Date: 2026-11-05. Sprint: Sprint 4 early pull, December Compression
Protocol. Compressed Deep: the single hardest capability per track,
built, tested, benchmarked, failure modes written; the rest of the
v2 Deep scope is the v1.1 backlog in ROADMAP.md at the repo root.

## SPEC source

SPEC.md Deep scope:
- Track A, Go: profile the live service with pprof, remove one real
  bottleneck, publish the before and after; one code reading note.
- Track B, Rust: traits and generics used to share real code across
  the CLI checkers, with a short note on what Rust bought and what
  it cost against the same tool in Python.

## Toolchain finding at cycle start (2026-11-05, rechecked)

- go: not found. rustc: not found. cargo: not found.
- g++ 13.3.0, gcc, and Python 3.12.3: present. Nothing is installed.
- Consequence, same as Learn and Build: the Go pprof study and the
  Rust traits study ship as proper layout sources labelled
  UNEXECUTED in every file. No compiled Go or Rust run is claimed.
- The executed, measured study is the Python reference: a profile
  and fix bottleneck study on the Build code (service_build.py).

## Bottleneck hypothesis (stated before the fix)

Hypothesis: on a larger registry, Build routing is the bottleneck.
route_build in level-2-build/service_build.py filters every health
record and sorts the healthy candidates on every single request,
so routing cost grows with registry size times request count, and
the sort repeats work whose answer cannot change while the health
records are fixed.

## Profiling method (stated before the fix)

- Workload: a deterministic expanded registry and request stream,
  generated in profile_deep.py from the Build fixtures only (no
  randomness, no wall time in the generation): 200 endpoints cycling
  the 10 Build endpoints with a deterministic latency offset, probed
  through the Build pool, then 20,000 requests cycling the models
  chat, embed, vision, code, unknown.
- Profiler: cProfile over the baseline routing workload, sorted by
  cumulative time, top functions recorded in the Deep README.
- Timing: time.perf_counter, one warmup run, then pooled batches:
  5 repetitions of the full workload, the median batch time is the
  reported figure for before and for after, on the same machine in
  the same process run. Timings live in a separate timing section
  of results_deep.json; they are not deterministic fields.

## The fix

IndexedRouter in profile_deep.py: built once from a fixed health
record set, it groups healthy records by model and keeps only the
best record per model under the exact Build ordering (lowest
latency, name ascending as tie break). Each request is then one
dict lookup. Construction is linear in the record count; routing
is constant time per request. The baseline path (Build functions,
unchanged) stays in the same module for the before measurement and
for the correctness comparison.

## Correctness invariant

Deep profiling workload outputs must match Build outputs exactly
on the same fixtures:
- On the Build fixtures (10 endpoints, 12 requests), the indexed
  router produces the identical routing records and summary as
  run_routing_build and summarise_routing_build.
- On the 200 endpoint, 20,000 request workload, the indexed router
  produces routing records identical to the baseline Build router
  on the same records and requests (compared as full lists in the
  tests and in the runner).
- Deterministic fields of results_deep.json (everything outside
  the timing section) are identical across two runs of run_deep.py.

## Rust design (UNEXECUTED source)

- Proper Cargo layout under rust/: Cargo.toml, src/lib.rs,
  src/error.rs, src/tool.rs, src/rules.rs, src/checker.rs,
  src/main.rs, tests/checker_tests.rs.
- Sharing design: a Rule trait (id, severity, applies to a borrowed
  Tool, returning bool). Eight rule structs, one per Build rule
  R1 to R8, implement the trait. Checker<R: Rule> is a generic
  single rule checker (static dispatch, monomorphised). The full
  eight rule checker is a CheckerSet holding trait objects
  (Vec<Box<dyn Rule>>, dynamic dispatch) so heterogeneous rules
  share one check_all path that returns owned CheckRecord values
  and propagates CheckError with the ? operator, reusing the Build
  error shape. The Deep README carries the short note on what the
  traits and generics buy and cost against the Python version.

## Go design (UNEXECUTED source)

- Proper module layout under go/: go.mod,
  cmd/healthsvc/main.go, internal/profile/profile.go.
- The sources carry the pprof study design in code shape:
  net/http/pprof imported for its side effects on a diagnostics
  listener, runtime/pprof CPU and heap capture helpers, and the
  exact before and after study steps as structured constants and
  comments: serve, load, capture CPU profile, read the top
  functions, apply the same index fix in Go shape, recapture, and
  compare. The Deep README states the study design in prose and
  states clearly that it was not run on this VM.

## Acceptance

- Full test suite passes locally (smoke plus Learn plus Build plus
  new Deep tests).
- cProfile evidence names the bottleneck before the fix is claimed.
- Before and after medians come from one real run of the runner on
  this VM; no timing is invented or copied from another project.
- Deterministic fields identical across two runs (verified in the
  runner record and in tests where timing is excluded).
- CI runs smoke, the full unit suite, and the Learn, Build, and
  Deep runners, in the existing CI style.
- No em dash in any touched file. No compiled Go or Rust claim.
