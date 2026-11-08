# Report: systems-languages-lab (P21)

Verdict: Draft, not pre-registered (see README.md). This report
records what ran, what it showed, and what is still missing. It brings
together the three level READMEs (Learn, Build, Deep), the
2026-11-07 research review and the DOSSIER ship state; their text is
kept below, moved unchanged apart from headings, with internal scoring
kept out of the public repo. In the moved text, SPEC.md, DOSSIER.md,
NOVELTY.md and ROADMAP.md now live in PROPOSAL.md, and "the level
README" means the matching record in this file.

## Scope, stated first

Systems languages for ML platform work, taught through a Python reference implementation. Plain scope, stated first: every executed level in this repo is Python standard library only, run on the Muse VM on 2026-11-05. The Go service sources and the Rust CLI sources ship in proper layout at every level and are labelled UNEXECUTED in every file: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. All health probes and tool manifests are scripted fixtures, authored for teaching. No real HTTP endpoint was served or probed, and no real MCP manifest file was read.

## Hypotheses scored

None of these was locked before its result (PROPOSAL.md says why), so
every line below is exploratory, not confirmatory.

| Hypothesis | Result | Evidence |
| --- | --- | --- |
| H1, Go service runs as real Go and reproduces the reference counts | MISS: not tested. No Go line has been compiled or run; go was not found on the build VM. | level-1-learn/go, level-2-build/go, level-3-deep/go (all labelled UNEXECUTED) |
| H2, Rust checker runs as real Rust and reproduces the reference counts | MISS: not tested. No Rust line has been compiled or run; rustc and cargo were not found. | level-1-learn/rust, level-2-build/rust, level-3-deep/rust (all labelled UNEXECUTED) |
| H3, route_build is the routing bottleneck (Python reference) | HELD. route_build held 1.780 of 1.856 s cumulative under cProfile (95.9 percent). | level-3-deep/results_deep.json, profile_top |
| H4, an index removes it with identical routing records | HELD. Full record lists identical on the 20,000-request workload (16,000 routed) and on the Build fixtures (11 of 12). Recorded run: median 2.434 s to 0.0765 s (31.8 times, 5 repetitions, no interval, shared VM). Repeat run: median paired ratio 37.84 times, 95 percent bootstrap interval 37.53 to 38.13, 30 repetitions, one aarch64 machine. | level-3-deep/results_deep.json, level-3-deep/results_deep_repeats.json |
| H5, Rust against Python cost note, evidence based | PARTIAL MISS. The note is written (Deep study record below) but rests on a design that never compiled, so it carries no measured evidence. | this file |

Scope items from the SPEC that are not done: the live Go pprof
profile, the Go code-reading note (register item 132), real HTTP
probes and a real MCP manifest read. They are the next cycle in
PROPOSAL.md.

## Where each headline number comes from

| Number | File | Command |
| --- | --- | --- |
| 95.9 percent | level-3-deep/results_deep.json (profile_top) | `python3 -c "import json;d=json.load(open('level-3-deep/results_deep.json'));t=float(d['profile_top'][0].split()[-2]);r=[l.split() for l in d['profile_top'] if '(route_build)' in l][0];print(round(float(r[3])/t*100,1))"` |
| 37.84 times, interval 37.53 to 38.13, 30 repetitions | level-3-deep/results_deep_repeats.json (paired) | `python3 -c "import json;p=json.load(open('level-3-deep/results_deep_repeats.json'))['paired'];print(p['repetitions'],p['median_paired_ratio'],p['bootstrap_ci95_median_ratio'])"` |
| records identical, 16,000 routed | level-3-deep/results_deep.json (deterministic) | `python3 -m unittest tests.test_results_regenerate -v` (regenerates the deterministic section and compares) |

Review note on the interval: the file stores each repetition's time
rounded to 4 decimals (the indexed arm takes about 3 ms). Recomputing
from those stored times gives a median paired ratio of 38.19 and a
bootstrap interval (seed 0, 10,000 resamples) of 37.24 to 38.31. The
recorded 37.84 and 37.53 to 38.13 were computed from the unrounded
times by level-3-deep/timing_repeats.py. The two agree to within
1 percent; the gap is the rounding. tests/test_results_regenerate.py
checks the stored median against the stored times within 2 percent.

The repeat run was recorded on a different machine from the Muse VM
study, so its seconds are not comparable to the recorded run; only
its ratio and scaling shape are.

## Results at a glance (from the v1.0 README)

| Test | Result |
| --- | --- |
| Learn (Python reference, Muse VM, 2026-11-05) | Health worker 4 of 6 endpoints healthy; router 6 of 8 requests routed; manifest checker 4 of 6 tools unsafe, 7 flags. Full record in level-1-learn/results_learn.json. |
| Build (Python reference, Muse VM, 2026-11-05) | Cancellable pool 8 of 10 endpoints healthy, 2 classified errors, pre-cancelled run 0 probed and 10 skipped; router 11 of 12 requests routed; extended checker 5 of 8 tools unsafe, 14 flags across 8 rules. Full record in level-2-build/results_build.json. |
| Deep (Python reference, Muse VM, 2026-11-05) | Profile and fix study on 200 endpoints and 20,000 requests: route_build 95.9 percent of routing time under cProfile; indexed router median 2.434 s to 0.0765 s per batch (5 pooled repetitions, 1 warmup), routing records identical to baseline. Rust traits design and Go pprof design ship as UNEXECUTED sources. Full record in level-3-deep/results_deep.json. |

## Dashboard (from the v1.0 README)

The dashboard (built from site/) reruns the routing service, the manifest
checker, the cancellable pool and the Deep bottleneck race in the browser
with JS ports of the Python reference. A known-answer check inside
`npm run build` proves the ports reproduce every count in the three
results files. Browser timings are labelled as browser timings; Go and
Rust remain UNEXECUTED.

The old ladder, for reading the records below:

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Learn record (2026-11-05)

Status: DONE 2026-11-05. Scope for this level, from SPEC.md:

- Track A, Go: one small Go service: the model endpoint health and routing service that P12's registry points at. Goroutines and channels run a real concurrent worker.
- Track B, Rust: one small Rust CLI in the P09 toolkit family: a tool manifest checker that reads MCP tool definitions and flags unsafe rules.

### Toolchain finding, stated first

Checked on this VM on 2026-11-05 before choosing the track: g++ 13.3.0 and Python 3.12.3 are present; go is not found and rustc is not found. Installing a toolchain was not done (FREE-ONLY run, no new installs in this cycle). So neither SPEC language could be compiled or run here, and this level does not pretend otherwise:

- The executed, tested code is a Python stdlib reference implementation of both Learn ideas: health_service.py (worker pool, registry, router) and manifest_checker.py (five checker rules), with run_learn.py as the runner.
- The Go shape of Track A sits in go/health_service.go (goroutines, jobs and results channels, the same fixtures and routing rule) and the Rust shape of Track B sits in rust/manifest_checker.rs (a Tool struct, a check function returning rule ids). Both files are teaching sources only: NOT compiled, NOT run, and no result in this level comes from them. Compiling and testing them is Build level work for a node with the toolchains.

This substitution is the largest limit of this level, named, not hidden.

### What the code teaches

Health and routing (health_service.py). A registry holds 6 model endpoints (name, model, scripted probe outcome, scripted latency used only as a routing preference). A worker pool pulls probe jobs off a queue, the Python analogue of goroutines fed by channels, and returns health records on a second queue. Output is sorted by endpoint name, so the result is identical for any worker count (test enforced for 1, 3, and 4 workers). The router serves a request only from a healthy endpoint for that model: lowest scripted latency first, name ascending as tie break. An unhealthy endpoint is never routed to, even on a latency tie (gamma-chat ties beta-chat at 25 and is skipped, test enforced).

Manifest checker (manifest_checker.py). Five rules, each flag naming its rule: R1 wildcard permission ("*" or a ":*" suffix), R2 shell execution with an empty allowlist, R3 network access with an empty allowed hosts list, R4 file write with an empty allowed paths list, R5 missing description. A tool with any flag is unsafe. Scoping is the lesson: admin_tool can execute shell and write files, yet earns no R2 or R4 flag because both are scoped to an allowlist and a path list.

### Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

Health per endpoint: alpha-chat healthy (40), alpha-embed healthy (15), beta-chat healthy (25), beta-embed healthy (30), gamma-chat unhealthy (503 unavailable), gamma-vision unhealthy (probe timeout). Latency figures are scripted fixture values, not measured wall time.

| Model | Endpoints | Healthy |
| --- | --- | --- |
| chat | 3 | 2 |
| embed | 2 | 2 |
| vision | 1 | 0 |

Routing over the 8 runner requests (chat, chat, embed, vision, chat, embed, vision, chat), in order: beta-chat, beta-chat, alpha-embed, unrouted, beta-chat, alpha-embed, unrouted, beta-chat.

Manifest per tool: file_reader no flags (safe), shell_runner R1 and R2, web_fetch R3, code_writer R4 and R5, data_query no flags (safe), admin_tool R1 and R3.

| Rule | R1 | R2 | R3 | R4 | R5 | Total flags |
| --- | --- | --- | --- | --- | --- | --- |
| Flags | 2 | 1 | 2 | 1 | 1 | 7 |

Results claim: Learn ran in Python on the Muse VM (Go and Rust toolchains missing on this VM): the health worker found 4 of 6 endpoints healthy, the router routed 6 of 8 requests (beta-chat 4, alpha-embed 2, 2 vision requests unrouted), and the manifest checker flagged 4 of 6 tools unsafe with 7 total flags (R1 2, R2 1, R3 2, R4 1, R5 1), with 15 unit tests passing plus the scaffold smoke test.

Full machine readable record: results_learn.json in this folder (sha256 d65df4090d0be7a6). Determinism: two runs of run_learn.py produced a byte identical results_learn.json. The file holds counts and names only, no wall time and no timestamps. Tests: python3 -m unittest discover -s tests ran 15 tests OK (tests/test_learn_systems.py, hand computed expected values) and python3 tests/test_smoke.py printed scaffold smoke test PASS.

### Next

Build level: install free Go and Rust toolchains on the assigned node (a node software decision), compile go/health_service.go and rust/manifest_checker.rs, port the 15 tests to both tracks, then take the SPEC Build scope (Go modules, error handling and context cancellation the Go way; Rust ownership, borrowing, and Result error chains).

## Build record (2026-11-05)

Status: DONE 2026-11-05. Scope for this level, from SPEC.md:

- Track A, Go: Go modules, formatting, and test tooling used as a native
  would; error handling and context cancellation done the Go way.
- Track B, Rust: ownership and borrowing handled in real code; error
  handling with Result types and clean error chains.

Build spec written first: BUILD-SPEC.md in this folder, with the hand
computed test oracle stated before the code ran.

### Toolchain finding, stated first

Rechecked on this VM on 2026-11-05 before choosing the track: g++ 13.3.0
and Python 3.12.3 are present; go is not found, rustc is not found, and
cargo is not found. Nothing was installed (FREE-ONLY run). So:

- The executed, tested code is a Python stdlib reference implementation
  at Build level: service_build.py (a cancellable worker pool with
  structured error chains) and manifest_build.py (an eight rule checker
  with severities and chained validation errors), with run_build.py as
  the runner.
- The Go Build track sits in go/ as a proper module project (go.mod,
  cmd/healthsvc/main.go, internal/health/health.go and its table driven
  health_test.go): wrapped errors with fmt.Errorf and the %w verb,
  errors.Is checks, context.Context with cancellation and timeout, and
  a channel worker pool that selects on ctx.Done(). It is labelled
  UNEXECUTED in every file: NOT compiled, NOT run, NOT tested here.
- The Rust Build track sits in rust/ as a proper Cargo project
  (Cargo.toml, src/lib.rs, src/error.rs, src/checker.rs, src/main.rs,
  tests/checker_tests.rs): owned Tool values, borrowed checks returning
  owned records, Result with the ? operator, and a custom CheckError
  type implementing std::error::Error with a source() chain. It is
  labelled UNEXECUTED in every file: NOT compiled, NOT run, NOT tested
  here.

No result in this level comes from the Go or Rust sources.

### What the Build code adds over Learn

Service (service_build.py). The registry grows from 6 to 10 endpoints:
vision gains a healthy endpoint (epsilon-vision) and a new code model
arrives as a latency tie (eta-code and zeta-code, both 18, name wins).
The worker pool is cancellable: workers check a shared CancelToken
before each job, the analogue of selecting on ctx.Done(). A run with
the token cancelled before start probes nothing and counts 10 skips.
Probe failures return as records, not bare exceptions: each carries
its error kind (http_error or timeout) and its error chain, built by
ServiceError, which records each wrapping step like Go error wrapping.

Checker (manifest_build.py). Rules R1 to R5 are unchanged from Learn.
Build adds R6 unpinned version, R7 excessive or missing rate limit
(above 1000 per minute), and R8 missing owner. Each rule has a severity
(high, medium, low) and the summary reports both views. Validation
raises ManifestError with a chain when a tool has no name, the analogue
of a Rust error type with a source chain. Duplicate names are reported.

### Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

| Area | Result |
| --- | --- |
| Health | 8 of 10 endpoints healthy; chat 3 of 4, embed 2 of 2, vision 1 of 2, code 2 of 2 |
| Errors | 2 total: http_error 1 (gamma-chat 503), timeout 1 (gamma-vision) |
| Cancellation | Pre-cancelled run: 0 probed, 10 skipped, status cancelled; full run: 10 probed, 0 skipped, status completed |
| Routing | 11 of 12 requests routed, 1 unrouted (unknown model); delta-chat 3, alpha-embed 2, epsilon-vision 3, eta-code 3 |
| Manifest | 5 of 8 tools unsafe, 3 safe, 14 flags; per rule R1 2, R2 1, R3 2, R4 1, R5 1, R6 3, R7 3, R8 1 |
| Severity | high 3, medium 6, low 5 (sums to 14) |

Routing order over the 12 runner requests: delta-chat, alpha-embed,
epsilon-vision, eta-code, delta-chat, epsilon-vision, eta-code,
alpha-embed, delta-chat, eta-code, epsilon-vision, unrouted.

Manifest per tool: file_reader no flags (safe), shell_runner R1 R2 R6
R7 R8, web_fetch R3, code_writer R4 R5 R6, data_query no flags (safe),
admin_tool R1 R3 R7, vision_tool R6 R7, scoped_writer no flags (safe).

Summary: Build ran in Python on the Muse VM (Go and Rust toolchains missing on this VM): the cancellable worker pool found 8 of 10 endpoints healthy with 2 classified errors (1 http_error, 1 timeout), a pre-cancelled run probed 0 and skipped 10, the router routed 11 of 12 requests (delta-chat 3, alpha-embed 2, epsilon-vision 3, eta-code 3), and the extended manifest checker flagged 5 of 8 tools unsafe with 14 total flags (R1 2, R2 1, R3 2, R4 1, R5 1, R6 3, R7 3, R8 1; severity high 3, medium 6, low 5), with 37 unit tests passing plus the scaffold smoke test.

Full machine readable record: results_build.json in this folder
(sha256 d5ac8507bed16e4b). Determinism: two runs of run_build.py
produced a byte identical results_build.json. The file holds counts
and names only, no wall time and no timestamps. Tests: python3 -m
unittest discover -s tests ran 37 tests OK (15 Learn tests in
tests/test_learn_systems.py plus 22 Build tests in
tests/test_build_systems.py, hand computed expected values) and
python3 tests/test_smoke.py printed scaffold smoke test PASS.

CI scope, as it stands now: the CI workflow (.github/workflows/ci.yml)
runs on a Python 3.11 and 3.12 matrix: ruff lint (scope in ruff.toml),
the scaffold smoke test, the Learn, Build, and Deep unit suites, and
the Learn, Build, and Deep runners. CodeQL runs separately
(.github/workflows/codeql.yml). When this level shipped, CI was a
single Python 3.12 job without CodeQL; the matrix, ruff, and CodeQL
arrived with the Actions polish pack. The local full suite stays a
co-gate. Bot reviews are advisory only and are never gates.

### Next

Deep level: on a node with the toolchains, compile and test both
tracks, then take the SPEC Deep scope (Go pprof profiling with a
before and after bottleneck fix and a code reading note; Rust traits
and generics shared across the checkers, with the Rust against Python
cost note). The v1.1 backlog for this project is that toolchain port
plus real HTTP probes and a real MCP manifest read.

## Deep study record

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

### Toolchain finding, stated first

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

### The bottleneck study (executed, Python)

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

### Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

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

### Repeat timing run (added 2026-11-07, different machine)

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

### Go pprof study design (UNEXECUTED, not run)

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

### Rust traits and generics (UNEXECUTED) and the cost note

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

### Failure modes

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

### Next

v1.1 backlog in ROADMAP.md at the repo root: the toolchain port
(compile and test both tracks, run the Go pprof study for real),
real HTTP probes, and the Go code reading note.

## Review notes (research review, 2026-11-07)

### Review summary

A clean, honest, reproducible engineering study with a narrow evidence
base. The executed evidence is Python only. The repo's headline thesis
is about Go and Rust, and no Go or Rust line has ever been compiled or
run. That gap dominates everything else and needs toolchains this
review was not allowed to install. Within its Python scope, the study
is well specified: hypothesis written before the fix, deterministic
workload, a record-equality correctness invariant, and recorded
results files. This change adds the statistics and scaling evidence
the recorded run lacked, plus a second-language reproduction (the JS
ports on the dashboard).

### Research question

What does profiling the Build routing service show, and does an index
remove the bottleneck without changing any routing decision? The
Python study answers that. The SPEC's broader question, what Go and
Rust buy for ML platform tooling compared with Python, is still open.
Remaining gap: needs a machine with Go 1.22 or later, rustc and cargo
(free toolchains, minutes to install), then ROADMAP item 1.

### Hypotheses

DEEP-SPEC.md states before the fix that route_build is the bottleneck
because it filters and sorts on every request. The recorded profile
supports it: route_build holds 1.780 of 1.856 s cumulative (95.9
percent). Fixed in this change: the profile_deep.py docstring said
"about 92 percent", which contradicted the recorded profile. It now
says 95.9 percent.

### Method

The workload is generated deterministically from the 10 Build
fixtures (200 endpoints, 20,000 requests). The fix is checked by full
record-list equality, not by sampling. Timing uses perf_counter with a
warmup. Fixed in this change: the dashboard's known-answer check
(site/src/lab.check.mjs, run by `npm run build`) re-implements
route_build, check_tool_build, the cancellable pool, the workload
generator and IndexedRouter in JavaScript. It reproduces every count
in results_learn.json, results_build.json and the deterministic
section of results_deep.json, which is an independent second
implementation of the logic. The manifest fields, which the results
files do not carry, are exported from TOOLS_BUILD to
level-2-build/fixtures_build.json, and tests/test_site_fixtures.py
fails if that export drifts.

### Baselines

The baseline is the real shipped router, which is the right
comparison. The speedup is close to what complexity predicts: the
baseline does a filter and sort per request, roughly O(n log n) in
registry size, while the index answers each request with a dict
lookup. Fixed in this change: level-3-deep/timing_repeats.py sweeps
registry size from 50 to 800 endpoints. In results_deep_repeats.json
the baseline median grows about 17.6 times over a 16 times larger
registry while the indexed median stays flat, with identical records
at every size. The dashboard plots this sweep and runs its own sweep
in the browser, labelled as browser timings.
Remaining gap (minor): alternative fixes such as caching only the
sort or a heap per model were not compared. They need no special
compute, but they are a design question for the owner, not a missing
measurement.

### Statistics and uncertainty

The recorded run has 5 repetitions on a shared VM: baseline 1.91 to
2.61 s, indexed 0.032 to 0.130 s, and no interval. An earlier run gave
a different ratio (1.2304 s / 0.0195 s). Fixed in this change:
- the dashboard computes the median ratio (31.8x) and the paired
  per-rep ratio range (14.7x to 77.0x) from times_s, instead of
  quoting a constant;
- timing_repeats.py adds 30 interleaved paired repetitions with a
  percentile bootstrap 95 percent interval on the median paired
  ratio (10,000 resamples, seed 0). Recorded on 2026-11-07 on an
  aarch64 machine with Python 3.12.3: median paired ratio 37.84x, 95%
  CI 37.53x to 38.13x. This is a different machine from the study VM,
  so its seconds are not comparable to the recorded run, and the file
  records the machine.
Remaining gap: a quiet, dedicated-node rerun of the original study
(ROADMAP item 6, the assigned BlackBoxV3). It needs about two minutes
on that node and the owner's decision to replace the recorded
results_deep.json.

### Reproducibility

Strong. Python stdlib only. `python3 -m unittest discover -s tests`
runs 48 tests (the original 46 plus the 2 fixture-parity tests), and
each runner rewrites its results file. CI runs a Python 3.11 and 3.12
matrix with ruff, and CodeQL runs separately. Fixed in this change:
the Build and Deep READMEs said there was "no CI matrix and no
CodeQL". They now describe the CI as it is. The dashboard rebuilds
from the committed files and fails its build if any reproduced count
drifts.

### Threats to validity

- Construct: the Go and Rust claims rest on Python analogues: threads
  and queues for goroutines, an Event for context cancellation, lists
  for Result chains. Remaining gap: the toolchains above.
- Internal: shared-VM noise in the recorded run. Partly addressed by
  the repeat run. A dedicated node is still needed (see above).
- External: probes and manifests are scripted fixtures. No HTTP
  endpoint was served and no real MCP manifest was read. Remaining
  gap: ROADMAP item 4 needs a local HTTP server (free, seconds) and
  real MCP tool manifest files. No paid compute is needed, but it is
  new feature scope for a later version.
- Compilability: the Go and Rust sources get no compiler, formatter or
  linter check. Remaining gap: go vet, gofmt, cargo fmt, cargo clippy
  and cargo test on a node with the toolchains, which takes minutes.

### Related work

The repo has no dated literature review, and NOVELTY.md is still an
unverified draft. This review claims no novelty. The study's value is
a small, fully reproducible profile-and-fix worked example with a
correctness invariant. It follows standard practice from:
- Python standard library documentation, "The Python Profilers"
  (cProfile and pstats), the profiler used here;
- the Go blog, "Profiling Go Programs" (Russ Cox, 2011), and the
  runtime/pprof and net/http/pprof package documentation, which the
  UNEXECUTED Go study plan follows;
- The Rust Programming Language book, chapters on traits, generics
  and trait objects, which the UNEXECUTED Rule trait design follows.
Remaining gap: a dated prior-art pass in DOSSIER.md Past and the
owner's claim-check gate on NOVELTY.md. That needs reading time and
the owner's decision, not compute. The SPEC's Go code-reading note
(register item 132, ROADMAP item 3) is the same kind of work.

### Limitations

Stated plainly in the level READMEs, ROADMAP.md and on the
dashboard. The dashboard labels the recorded profile and timings as a
recorded replay, labels its own race as "your browser, this run", and
marks every Go and Rust file UNEXECUTED.

### Summary of changes in this branch

1. Fixed the profile_deep.py docstring share (92 to 95.9 percent).
2. Corrected the stale CI sentences in the Build and Deep READMEs.
3. Added level-2-build/fixtures_build.json, its export script, and a
   parity test.
4. Added a build-time cross-language known-answer check for every
   number the dashboard computes.
5. Added the repeat timing run: 30 paired reps, a bootstrap interval
   and a size sweep, recorded with its machine.
6. Added the dashboard (site/) and a Pages workflow.

## Ship state (from DOSSIER.md, 2026-11-05, v1.0)

Learn, Build, and compressed Deep are DONE. All levels executed
as a Python stdlib reference on the Muse VM (Python 3.12.3); the
Go and Rust toolchains were missing on that VM at every level, so
the Go and Rust tracks ship as proper layout sources labelled
UNEXECUTED in every file, and no compiled run is claimed for them.
Deep evidence: a cProfile bottleneck study on the Build routing
code (route_build at 95.9 percent of routing time on a 200
endpoint, 20,000 request deterministic workload), an indexed
router fix (median batch 2.434 s to 0.0765 s in the recorded run,
routing records identical to baseline), a Rust Rule trait sharing
design (generic Checker plus trait object CheckerSet, UNEXECUTED),
and a Go pprof study design (net/http/pprof wiring plus capture
plan, UNEXECUTED, not run). Full suite at ship: 46 unit tests
plus the scaffold smoke test.

## Threats and limits in one place

- The system under study never ran. Every executed result is the
  Python reference; the Go and Rust claims rest on Python analogues.
- Scripted fixtures: no real HTTP endpoint was served or probed and no
  real MCP manifest file was read.
- Timing: the recorded run is 5 repetitions on a shared VM; the repeat
  run is one machine. No number here is a claim about any other host.
- Not pre-registered: hypotheses and results were committed together.
- Software product profile not met: no coverage report, no secret scan
  in CI, and no input validation on real (untrusted) manifests.
