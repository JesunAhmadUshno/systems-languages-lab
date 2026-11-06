# Release notes: systems-languages-lab (P21)

One section per release line. Every number below comes from the
level README of that release and the release text on GitHub,
verified with gh release list on 2026-11-05. Every executed
release is a Python reference only: Go and Rust sources are
UNEXECUTED at every level, all probes and manifests are
scripted fixtures, and the Deep speedup is an order of
magnitude effect, not a constant. The full release text lives
on the GitHub releases page:
https://github.com/JesunAhmadUshno/systems-languages-lab/releases

## v0.1, Learn (2026-11-05)

- What shipped: a Python reference for a health and routing
  service and a 5 rule manifest checker, plus Go and Rust
  teaching sources labelled UNEXECUTED, 15 checks and the
  scaffold smoke test.
- Python reference result: 4 of 6 endpoints healthy, router
  6 of 8 requests routed (beta-chat 4, alpha-embed 2, 2 vision
  requests unrouted), checker 4 of 6 tools unsafe with 7 flags.
- Level grade: 7,900 of 10,000.
- Release: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.1

## v0.5, Build (2026-11-05)

- What shipped: a cancellable worker pool with structured
  error chains and an extended 8 rule checker with severities,
  plus proper Go module and Rust Cargo projects labelled
  UNEXECUTED, 22 new checks (37 checks in total with Learn at
  that point, counting Learn and Build test files).
- Python reference result: 8 of 10 endpoints healthy, 2
  classified errors, pre-cancelled run 0 probed and 10
  skipped, router 11 of 12 requests routed, checker 5 of 8
  tools unsafe with 14 flags (severity high 3, medium 6, low 5).
- Level grade: 7,800 of 10,000.
- Release: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.5

## v1.0, Learn, Build, and Deep (2026-11-05)

- What shipped: a profile and fix bottleneck study in Python,
  a Rust Rule trait sharing design and a Go pprof study design
  as UNEXECUTED sources, and written failure modes, plus 9 new
  checks (46 checks in total, plus the scaffold smoke test).
  The rest of the v2 scope is named in ROADMAP.md as the v1.1
  backlog.
- Python reference result: on 200 endpoints and 20,000
  requests, route_build was 95.9 percent of routing time under
  cProfile; the indexed router median was 2.434 s to 0.0765 s
  per batch (5 pooled repetitions, 1 warmup), routing records
  identical to baseline. The speedup is an order of magnitude
  effect, not a constant.
- Level grade: 7,900 of 10,000.
- Release: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v1.0

## Held channels

- Social posts for every release above: HELD under the standing
  platform rules. The loop prepares drafts and never posts;
  Threads needs Jesun's one tap per post.
- The v1.1 backlog lives in ROADMAP.md: the toolchain port,
  the Go pprof study run for real, the Go code reading note,
  real HTTP probes and a real MCP manifest read, ranked
  routing, and larger real workloads on a dedicated node.
