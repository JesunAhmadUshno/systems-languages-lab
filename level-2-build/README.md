# Level 2, Build: systems-languages-lab

Status: DONE 2026-11-05. Scope for this level, from SPEC.md:

- Track A, Go: Go modules, formatting, and test tooling used as a native
  would; error handling and context cancellation done the Go way.
- Track B, Rust: ownership and borrowing handled in real code; error
  handling with Result types and clean error chains.

Build spec written first: BUILD-SPEC.md in this folder, with the hand
computed test oracle stated before the code ran.

## Toolchain finding, stated first

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

## What the Build code adds over Learn

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

## Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

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

## Grade: 7,800 of 10,000

Deductions, itemized, summing to 2,200:

- No Go execution: the Track A Build source is not compiled or run and
  no goroutine, channel, or context ran, because the Go toolchain is
  missing on this VM (minus 700).
- No Rust execution: the Track B Build source is not compiled or run
  and no ownership, borrowing, or Result code ran, because the Rust
  toolchain is missing on this VM (minus 500).
- Scripted probes and fixtures: no real HTTP health endpoint was served
  or probed, and no real MCP manifest file was read (minus 400).
- Small authored fixtures: 10 endpoints, 12 requests, and 8 tool
  manifests, all hand written for teaching (minus 300).
- The Go and Rust sources receive no compiler, formatter, or linter
  check on this VM, so their syntax and formatting are unproven
  (minus 200).
- Run executed on the Muse VM, not the assigned BlackBoxV3 fleet
  node (minus 100).

Zero-tolerance: PASS (no invented claim, no result claimed from the
unexecuted Go or Rust sources, em dash count 0 in all touched files,
scaffold never graded as a build).

## Next

Deep level: on a node with the toolchains, compile and test both
tracks, then take the SPEC Deep scope (Go pprof profiling with a
before and after bottleneck fix and a code reading note; Rust traits
and generics shared across the checkers, with the Rust against Python
cost note). The v1.1 backlog for this project is that toolchain port
plus real HTTP probes and a real MCP manifest read.
