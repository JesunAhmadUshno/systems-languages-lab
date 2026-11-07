# Level 3, Deep: systems-languages-lab

Status: DONE 2026-11-05. Compressed Deep scope (December Compression
Protocol): the single hardest capability per track.

- Track A, Go shape: a profile and fix bottleneck study. Executed
  on the Python Build reference; the Go pprof study design ships
  as UNEXECUTED source (see the Go section below).
- Track B, Rust shape: traits and generics sharing the checker
  rules. Ships as UNEXECUTED source with the cost note below.

Deep spec written first: DEEP-SPEC.md in this folder, with the
bottleneck hypothesis, the profiling method, the fix, and the
correctness invariant stated before the code ran.

## Toolchain finding, stated first

Rechecked on this VM on 2026-11-05: go is not found, rustc is not
found, and cargo is not found; g++ 13.3.0 and Python 3.12.3 are
present. Nothing was installed (FREE-ONLY run). So:

- The executed, measured study is Python: profile_deep.py profiles
  the Build service in level-2-build/service_build.py, and
  run_deep.py writes results_deep.json.
- The Go Deep track sits in go/ as a proper module project (go.mod,
  cmd/healthsvc/main.go, internal/profile/profile.go) carrying the
  pprof study design in code shape. It is labelled UNEXECUTED in
  every file: NOT compiled, NOT run, no profile captured here.
- The Rust Deep track sits in rust/ as a proper Cargo project
  (Cargo.toml, src/lib.rs, src/error.rs, src/tool.rs, src/rules.rs,
  src/checker.rs, src/main.rs, tests/checker_tests.rs) sharing the
  eight rules through a Rule trait. It is labelled UNEXECUTED in
  every file: NOT compiled, NOT run, NOT tested here.

No result in this level comes from the Go or Rust sources.

## The bottleneck study (executed, Python)

Workload, deterministic, generated in profile_deep.py from the
Build fixtures only: 200 endpoints cycling the 10 Build endpoints
with a deterministic latency offset, probed through the Build pool
(160 healthy, 40 unhealthy), then 20,000 requests cycling chat,
embed, vision, code, unknown.

cProfile over the baseline routing workload (696,002 calls, 1.856 s
under the profiler in the recorded run): run_routing_build took
1.856 s cumulative, route_build took 1.780 s cumulative (95.9
percent), list sort took 1.020 s cumulative across 16,000 sorts,
and the sort key lambda ran 640,000 times. The hypothesis held:
route_build filters every record and sorts the healthy candidates
on every request, repeating work whose answer cannot change while
the health records are fixed.

The fix: IndexedRouter in profile_deep.py. One linear build keeps,
per model, the best healthy record under the exact Build ordering
(lowest latency, name ascending tie break). A request is then one
dict lookup. The indexed timing below includes one index build per
timed batch, so the fix is charged for its own setup.

## Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

Method: time.perf_counter, 1 warmup run, 5 pooled repetitions of
the full 20,000 request workload, median batch time reported, same
process and machine for before and after.

| Measure | Baseline (Build route_build) | Indexed (Deep fix) |
| --- | --- | --- |
| Median batch time, 20,000 requests | 2.434 s | 0.0765 s |
| Batch times, seconds | 1.9081, 2.5962, 2.6068, 2.434, 1.9084 | 0.1301, 0.0765, 0.1065, 0.0316, 0.0619 |
| Routed | 16,000 of 20,000 | 16,000 of 20,000 (identical records) |
| Per endpoint | ep-0063-delta-chat 4000, ep-0014-alpha-embed 4000, ep-0007-epsilon-vision 4000, ep-0028-zeta-code 4000 | identical |

The median ratio for this recorded run is 31.8 times faster.
Timing variance note, stated honestly: this VM is shared and its
medians moved between study runs (a quieter run measured baseline
1.2304 s and indexed 0.0195 s). The direction and the order of
magnitude are stable; the exact ratio is a property of the run,
not a constant. The recorded run in results_deep.json is the one
quoted above.

Correctness, the Deep invariant: baseline and indexed routing
records are identical as full lists on the 20,000 request workload
and on the Build fixtures (11 of 12 routed; delta-chat 3,
alpha-embed 2, epsilon-vision 3, eta-code 3). The deterministic
section of results_deep.json repeated identical across two study
runs inside the runner (deterministic_repeat_identical true).

Honest file note: results_deep.json as a whole is NOT byte
identical across runs, because its timing section holds measured
wall times. Its deterministic section (counts, names, equality
flags, profile rows apart from their times) is the part verified
identical, and the runner checks that on every run.

## Repeat timing run (added 2026-11-07, different machine)

timing_repeats.py adds what the recorded run lacks, without touching
results_deep.json: 30 interleaved paired repetitions on the same
workload with a percentile bootstrap 95 percent interval on the
median paired ratio, and a registry size sweep from 50 to 800
endpoints. It ran on an aarch64 Linux machine with Python 3.12.3,
not the Muse VM, so its seconds are not comparable to the table
above; its ratios and scaling shape are the point. Output, with the
machine recorded: results_deep_repeats.json in this folder. The
sweep confirms the records stay identical at every size and that
baseline time grows with registry size while indexed time stays
flat (see the file for the numbers).

## Go pprof study design (UNEXECUTED, not run)

The design that would run on a machine with Go, in order, also
carried as StudySteps in go/internal/profile/profile.go:

1. Serve the Build health service with the diagnostics listener
   on: cmd/healthsvc registers net/http/pprof by import side
   effect on 127.0.0.1:6060 only, off the service listener.
2. Load: replay the same deterministic workload used here (200
   endpoints, 20,000 routing requests).
3. Capture before: a runtime/pprof CPU profile over the load
   (CaptureCPU helper), read with go tool pprof -top, record the
   top functions.
4. Fix: the same index in Go shape, a per model best endpoint map
   built once after probing, replacing the per request filter
   and sort in Route.
5. Capture after under the identical load, record the -top table
   and the pooled median wall times.
6. Compare: publish both tables beside the Python numbers,
   labelled as Go measured on that machine.
7. Heap: CaptureHeap before and after as a secondary check that
   the index does not grow memory per request.

This study was NOT run. No Go profile, Go timing, or Go result is
claimed anywhere in this level.

## Rust traits and generics (UNEXECUTED) and the cost note

Sharing design: a Rule trait (id, severity, applies to a borrowed
Tool). Eight structs, one per Build rule R1 to R8, implement it.
Checker<R: Rule> is generic over one rule type: static dispatch,
monomorphised, for hot single rule callers. CheckerSet holds
Vec<Box<dyn Rule>> trait objects: dynamic dispatch, so the eight
heterogeneous rules share one check and check_all path returning
owned CheckRecord values, with CheckError propagated by ?.

What Rust buys against the Python version: the rule set becomes
data with a compiler checked contract (a rule that misses a trait
method does not compile), severity travels with the rule instead
of a parallel dict that can drift, single rule hot paths pay no
dispatch cost under the generic form, and ownership makes the
borrow in, owned out data flow explicit at the type level.
What it costs: two dispatch shapes to understand instead of one
loop, Box and dyn boilerplate for the heterogeneous set, a longer
compile and borrow checker ramp for new contributors, and, in
this project today, the largest cost of all: it did not run here,
so unlike the Python checker it carries no measured evidence.

## Failure modes

- Index staleness: IndexedRouter is correct only for a fixed
  health record set. If endpoints are re-probed, the index must
  be rebuilt; routing from a stale index after a health change
  would keep sending traffic to a newly unhealthy endpoint. The
  class takes its records once, at construction, to make that
  contract visible.
- Tie break drift: keeping only the best record per model is
  equivalent only because route_build returns a single name under
  the (latency, name) ordering. A future Build change that returns
  ranked lists would silently break the equivalence; the Deep
  tests compare full record lists to catch exactly that.
- Timing noise: medians on a shared VM vary by run (see the
  variance note). A ratio quoted without its batch times and
  method would overclaim; both are published here.
- Unexecuted tracks: the Go and Rust sources receive no compiler,
  formatter, or linter check on this VM. A syntax error in them
  would not be caught by this level tests or CI.
- Workload shape: the expanded registry is a deterministic
  generation from 10 authored fixtures, not a production
  registry; the bottleneck direction (per request sort) is a
  property of the code, the exact ratio is a property of the
  workload and the machine.

Summary: Deep ran in Python on the Muse VM (Go and Rust toolchains missing on this VM): cProfile on the deterministic workload of 200 endpoints and 20,000 requests put route_build at 1.780 of 1.856 seconds cumulative (95.9 percent), the indexed router fix cut the median routing batch from 2.434 seconds to 0.0765 seconds over 5 pooled repetitions with 1 warmup, baseline and indexed routing records were identical on the full workload (16,000 routed, 4,000 unrouted) and on the Build fixtures (11 of 12 routed), the deterministic section repeated identical across two runs, and the Rust traits and generics sources and the Go pprof study design ship labelled UNEXECUTED and were not compiled or run, with 46 unit tests passing plus the scaffold smoke test.

Full machine readable record: results_deep.json in this folder
(sha256 4aad645df27040e2). Tests: python3 -m unittest discover -s tests
ran 46 tests OK (15 Learn tests plus 22 Build tests plus 9 Deep
tests in tests/test_deep_systems.py, hand computed expected
values) and python3 tests/test_smoke.py printed scaffold smoke
test PASS.

CI scope, as it stands now: the CI workflow (.github/workflows/ci.yml)
runs on a Python 3.11 and 3.12 matrix: ruff lint (scope in ruff.toml),
the scaffold smoke test, the Learn, Build, and Deep unit suites, and
the Learn, Build, and Deep runners. CodeQL runs separately
(.github/workflows/codeql.yml). When this level shipped, CI was a
single Python 3.12 job without CodeQL; the matrix, ruff, and CodeQL
arrived with the Actions polish pack. The local full suite stays a
co-gate. Bot reviews are advisory only and are never gates.

## Grade: 7,900 of 10,000

Deductions, itemized, summing to 2,100:

- No Go execution: the pprof study is a design, not a run; no Go
  profile was captured and no Go bottleneck was removed, because
  the Go toolchain is missing on this VM (minus 700).
- No Rust execution: the traits and generics sources are not
  compiled or run and no trait, generic, or trait object code ran,
  because the Rust toolchain is missing on this VM (minus 500).
- Scripted fixtures at scale: the workload registry is generated
  from the 10 authored Build fixtures and no real HTTP endpoint
  was served or probed (minus 300).
- The Go and Rust sources receive no compiler, formatter, or
  linter check on this VM, so their syntax is unproven (minus 200).
- Timing noise on the shared VM: medians moved between study
  runs, so the speedup is an order of magnitude, not a precise
  constant (minus 200).
- Run executed on the Muse VM, not the assigned BlackBoxV3 fleet
  node (minus 100).
- The SPEC Deep code reading note on a Go open source codebase
  (register item 132) is outside the compressed scope and sits in
  the v1.1 backlog in ROADMAP.md (minus 100).

Zero-tolerance: PASS (no invented claim, no result claimed from
the unexecuted Go or Rust sources, no timing quoted that was not
measured in a recorded run, em dash count 0 in all touched files,
scaffold never graded as a build).

## Next

v1.1 backlog in ROADMAP.md at the repo root: the toolchain port
(compile and test both tracks, run the Go pprof study for real),
real HTTP probes, and the Go code reading note.
