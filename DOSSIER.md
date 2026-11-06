# DOSSIER: systems-languages-lab (P21) v1, 2026-11-04

Written under the documentation and publishing standard (past, present, future). Updated at ship time.

## Past

Prior art for this project is named in NOVELTY.md (language tour examples in Go and Rust). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value 4 of 5 (register Category 2 holds 65 items; Go and Rust named at Apple, Microsoft, xAI) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

## Ship state (2026-11-05, v1.0)

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
plan, UNEXECUTED, not run). Grades: Learn 7,900 of 10,000, Build
7,800 of 10,000, Deep 7,900 of 10,000, each with itemized
deductions in its level README. Full suite at ship: 46 unit tests
plus the scaffold smoke test.

## Future

The v1.1 backlog sits in ROADMAP.md at the repo root: the
toolchain port, the Go pprof study run for real, the Go code
reading note, real HTTP probes and a real MCP manifest read, and
a dedicated node timing repeat. Any forecast about this field is
[unverified] unless a dated primary source is added here.
