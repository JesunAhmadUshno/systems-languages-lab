# Level 1, Learn: systems-languages-lab

Status: DONE 2026-11-05. Scope for this level, from SPEC.md:

- Track A, Go: one small Go service: the model endpoint health and routing service that P12's registry points at. Goroutines and channels run a real concurrent worker.
- Track B, Rust: one small Rust CLI in the P09 toolkit family: a tool manifest checker that reads MCP tool definitions and flags unsafe rules.

## Toolchain finding, stated first

Checked on this VM on 2026-11-05 before choosing the track: g++ 13.3.0 and Python 3.12.3 are present; go is not found and rustc is not found. Installing a toolchain was not done (FREE-ONLY run, no new installs in this cycle). So neither SPEC language could be compiled or run here, and this level does not pretend otherwise:

- The executed, tested code is a Python stdlib reference implementation of both Learn ideas: health_service.py (worker pool, registry, router) and manifest_checker.py (five checker rules), with run_learn.py as the runner.
- The Go shape of Track A sits in go/health_service.go (goroutines, jobs and results channels, the same fixtures and routing rule) and the Rust shape of Track B sits in rust/manifest_checker.rs (a Tool struct, a check function returning rule ids). Both files are teaching sources only: NOT compiled, NOT run, and no result in this level comes from them. Compiling and testing them is Build level work for a node with the toolchains.

This substitution is the largest grade deduction below, named, not hidden.

## What the code teaches

Health and routing (health_service.py). A registry holds 6 model endpoints (name, model, scripted probe outcome, scripted latency used only as a routing preference). A worker pool pulls probe jobs off a queue, the Python analogue of goroutines fed by channels, and returns health records on a second queue. Output is sorted by endpoint name, so the result is identical for any worker count (test enforced for 1, 3, and 4 workers). The router serves a request only from a healthy endpoint for that model: lowest scripted latency first, name ascending as tie break. An unhealthy endpoint is never routed to, even on a latency tie (gamma-chat ties beta-chat at 25 and is skipped, test enforced).

Manifest checker (manifest_checker.py). Five rules, each flag naming its rule: R1 wildcard permission ("*" or a ":*" suffix), R2 shell execution with an empty allowlist, R3 network access with an empty allowed hosts list, R4 file write with an empty allowed paths list, R5 missing description. A tool with any flag is unsafe. Scoping is the lesson: admin_tool can execute shell and write files, yet earns no R2 or R4 flag because both are scoped to an allowlist and a path list.

## Results (measured 2026-11-05, Muse VM, Python 3.12.3, stdlib only)

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

## Grade: 7,900 of 10,000

Deductions, itemized, summing to 2,100:

- No Go execution: the Track A service is not in Go and no goroutine ran, because the Go toolchain is missing on this VM (minus 700).
- No Rust execution: the Track B checker is not in Rust and no ownership or borrowing code ran, because the Rust toolchain is missing on this VM (minus 500).
- Scripted probes and fixtures: no real HTTP health endpoint was served or probed, and no real MCP manifest file was read (minus 400).
- Small authored fixtures: 6 endpoints, 8 requests, and 6 tool manifests, all hand written for teaching (minus 300).
- The concurrent worker is a thread and queue analogue, not goroutines and channels, so no Go concurrency behaviour is evidenced (minus 100).
- Run executed on the Muse VM, not the assigned BlackBoxV3 fleet node (minus 100).

Zero-tolerance: PASS (no invented claim, no result claimed from the unexecuted Go or Rust sources, em dash count 0 in all touched files, scaffold never graded as a build).

## Next

Build level: install free Go and Rust toolchains on the assigned node (a node software decision), compile go/health_service.go and rust/manifest_checker.rs, port the 15 tests to both tracks, then take the SPEC Build scope (Go modules, error handling and context cancellation the Go way; Rust ownership, borrowing, and Result error chains).
