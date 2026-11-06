# ROADMAP: systems-languages-lab (P21), v1.1 backlog

v1.0 shipped 2026-11-05: Learn, Build, and compressed Deep DONE
(executed Python reference; Go and Rust sources labelled
UNEXECUTED at every level, toolchains missing on the build VM).

The rest of the v2 Deep scope, named here as the v1.1 backlog:

1. Toolchain port: on a node with go, rustc, and cargo, compile,
   format check (gofmt, cargo fmt), lint, and test both tracks at
   every level, and fix what the compilers find.
2. Go pprof study, run for real: execute the study design in
   level-3-deep (serve with the pprof listener, replay the
   workload, capture before and after CPU and heap profiles,
   publish both go tool pprof -top tables with the Go timings
   labelled as measured on that machine).
3. Go code reading note: one note on a section of a Go open
   source codebase (SPEC register item 132; Kubernetes platform
   code is Go), the Deep item deferred by the compressed scope.
4. Real probes: serve a real HTTP health endpoint and probe it,
   and read a real MCP tool manifest file, replacing the scripted
   fixtures at Learn, Build, and Deep.
5. Ranked routing: if routing ever needs ranked candidate lists
   instead of a single best endpoint, extend IndexedRouter to
   keep a sorted per model list and re-prove record equality.
6. Larger real workloads: repeat the Deep timing study on a
   dedicated node (the assigned BlackBoxV3) so the medians carry
   no shared VM noise, and publish the comparison.
