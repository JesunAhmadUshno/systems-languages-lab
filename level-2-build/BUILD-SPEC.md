# BUILD-SPEC: systems-languages-lab (P21), Level 2 Build

Written first, before Build code, per the house engineering pipeline.
Date: 2026-11-05. Sprint: Sprint 4 early pull, December Compression Protocol.

## SPEC source

SPEC.md Build scope:
- Track A, Go: Go modules, formatting, and test tooling used as a native
  would; error handling and context cancellation done the Go way
  (register items 80, 128).
- Track B, Rust: ownership and borrowing handled in real code; error
  handling with Result types and clean error chains (register items
  81, 82, 130).

## Toolchain finding at cycle start (2026-11-05, rechecked)

- go: not found. rustc: not found. cargo: not found.
- g++ 13.3.0, gcc, and Python 3.12.3: present.
- Nothing is installed in this cycle (FREE-ONLY, no installs).
- Consequence: Go and Rust tracks ship as Build-grade sources in proper
  project layout, labelled UNEXECUTED in file and in this spec and in
  the level README. No compiled run is claimed for either track.
- The executed track is a Python stdlib reference implementation at
  Build level. Every measured number in results_build.json comes from
  that Python code, run on the Muse VM.

## Build design

### Python reference (executed)

- service_build.py: hardens the Learn health and routing service.
  - Registry grows from 6 to 10 endpoints (adds delta-chat, epsilon-vision,
    zeta-code, eta-code) so vision becomes routable and a new code model
    exercises a latency tie break.
  - A real worker pool (threads plus queues) with a shared cancellation
    token (threading.Event). Workers check the token before each job.
    A cancelled run probes nothing and reports every job as skipped.
  - Structured error chains: ServiceError carries a context string and
    a cause, and its chain list records each wrapping step. Probe
    failures are classified (http_error, timeout) and never raised as
    bare exceptions through the pool; they return as error records.
  - Routing stays: healthy only, lowest scripted latency, name tie break.
- manifest_build.py: extends the Learn checker from 5 rules to 8.
  - R1 to R5 unchanged from Learn.
  - R6 unpinned_version: version missing, empty, "*" or "latest".
  - R7 excessive_rate: rate limit missing or above 1000 per minute.
  - R8 missing_owner: owner empty or missing.
  - Each rule carries a severity (high, medium, low). The summary
    reports flags per rule and flags per severity.
  - Validation uses a ManifestError with a chain: a tool with no name
    raises a chained error instead of returning a silent record.
  - Duplicate tool names are reported as a list, not hidden.
  - Tool set grows from 6 to 8 (adds vision_tool and scoped_writer).
- run_build.py: runs both halves, writes results_build.json with
  counts and names only (no wall time, no timestamps), so two runs
  are byte identical.

### Go track (UNEXECUTED source)

- Layout a native would use: go.mod, cmd/healthsvc/main.go,
  internal/health/health.go, internal/health/health_test.go.
- Idiomatic Go: wrapped errors with fmt.Errorf and the %w verb,
  errors.Is and errors.As checks, context.Context passed as the first
  argument, context.WithTimeout and context.WithCancel, a worker pool
  over channels that stops on ctx.Done(), gofmt formatting (tabs),
  and table driven tests in the _test.go file.

### Rust track (UNEXECUTED source)

- Layout a native would use: Cargo.toml, src/lib.rs, src/error.rs,
  src/checker.rs, src/main.rs, tests/checker_tests.rs.
- Idiomatic Rust: ownership correct data flow (owned Tool values moved
  into the checker, borrowed slices read through references, results
  returned as owned values), Result with the ? operator, and a custom
  error type (CheckError) that implements std::error::Error with a
  source() chain, plus From conversions so ? composes.

## Hand computed expectations (test oracle, written before code runs)

Health: 10 endpoints, 8 healthy, 2 unhealthy (gamma-chat http_error,
gamma-vision timeout). By model: chat 3 of 4, embed 2 of 2, vision
1 of 2, code 2 of 2.
Routing: 12 requests, 11 routed, 1 unrouted (unknown model). Per
endpoint: delta-chat 3, alpha-embed 2, epsilon-vision 3, eta-code 3.
Route picks: chat delta-chat (20), embed alpha-embed (15), vision
epsilon-vision (35), code eta-code (18 tie, name before zeta-code).
Errors: 2 total, http_error 1, timeout 1, cancelled 0 in the full run.
Cancellation scenario: token cancelled before start, 0 probed,
10 skipped, status cancelled.
Manifest: 8 tools, 5 unsafe, 3 safe, 14 flags. Per rule: R1 2, R2 1,
R3 2, R4 1, R5 1, R6 3, R7 3, R8 1. Per severity: high 3, medium 6,
low 5. Per tool: file_reader 0, shell_runner R1 R2 R6 R7 R8,
web_fetch R3, code_writer R4 R5 R6, data_query 0, admin_tool
R1 R3 R7, vision_tool R6 R7, scoped_writer 0.

## Acceptance

- Full test suite passes locally (Learn tests plus new Build tests
  plus scaffold smoke).
- results_build.json byte identical across two runs of run_build.py.
- CI runs smoke, the full unit suite, the Learn runner, and the
  Build runner, when the existing CI pattern makes that safe.
- No em dash in any touched file. No invented result.
