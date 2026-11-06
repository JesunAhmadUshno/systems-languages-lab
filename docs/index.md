# systems-languages-lab

Systems languages for ML platform work, taught through a Python reference implementation. Plain scope, stated first: every executed level in this repo is Python standard library only, run on the Muse VM on 2026-11-05. The Go service sources and the Rust CLI sources ship in proper layout at every level and are labelled UNEXECUTED in every file: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. All health probes and tool manifests are scripted fixtures, authored for teaching. No real HTTP endpoint was served or probed, and no real MCP manifest file was read.

- Learn: Python reference for a Go-shaped health and routing service and a Rust-shaped manifest checker. Health worker 4 of 6 endpoints healthy; router 6 of 8 requests routed; manifest checker 4 of 6 tools unsafe, 7 flags across 5 rules. 15 checks. Grade 7,900 of 10,000.
- Build: cancellable worker pool and extended checker in Python. 8 of 10 endpoints healthy, 2 classified errors, pre-cancelled run 0 probed and 10 skipped; router 11 of 12 requests routed; extended checker 5 of 8 tools unsafe, 14 flags across 8 rules. 22 checks. Grade 7,800 of 10,000.
- Deep: profile and fix bottleneck study in Python on 200 endpoints and 20,000 requests. route_build was 95.9 percent of routing time under cProfile; the indexed router median was 2.434 s to 0.0765 s per batch (5 pooled repetitions, 1 warmup), routing records identical to baseline. The speedup is an order of magnitude effect, not a constant: timing on a shared VM varies by run. Rust traits design and Go pprof design ship as UNEXECUTED sources. 9 checks. Grade 7,900 of 10,000.

Tests: 46 checks in total (15 Learn, 22 Build, 9 Deep), plus the scaffold smoke test.

Grades on record (of 10,000): Learn 7,900, Build 7,800, Deep 7,900.

Every number above is already published in this repo (README.md, DOSSIER.md, and the three level READMEs and results files) and reproduced by the runners in this repo, checked in CI. The v1.1 backlog in ROADMAP.md names the toolchain port, the real Go pprof run, and the real probes that would replace the scripted fixtures and the unexecuted sources.

Releases: https://github.com/JesunAhmadUshno/systems-languages-lab/releases
