# systems-languages-lab

**Question.** What do Go and Rust buy over Python for two small ML
platform tools, a model-endpoint health and routing service and an MCP
tool-manifest checker, and does profiling the routing service find a
bottleneck that can be removed without changing any routing decision?

**Headline.** No result yet on Go and Rust: their sources have never
been compiled or run. In the Python reference, route_build held 95.9
percent of routing time under cProfile, and a per-model index made
routing 37.8 times faster (median paired ratio over 30 repetitions,
95 percent bootstrap interval 37.5 to 38.1, one aarch64 machine) with
every routing record identical to the baseline.

**Field.** Software product. **Job family.** ML platform and
infrastructure engineering (Go and Rust).

**Verdict.** Draft, not pre-registered. The Python reference of both
tools runs end to end from one command and its tests pass in CI on
Python 3.11 and 3.12, but the system under study, the Go service and
the Rust CLI, has never been compiled or run, so Functional waits for
that first run. No plan was locked before the results, so the repo is
capped at Functional until a locked confirmatory cycle.

Live dashboard: https://jesunahmadushno.github.io/systems-languages-lab/

## Reproduce

```text
python3 -m unittest discover -s tests -v
python3 level-1-learn/run_learn.py && python3 level-2-build/run_build.py
cd site && npm ci && npm run build
```

Python 3 standard library only. The test run includes
tests/test_results_regenerate.py, which rebuilds the Learn and Build
results and the Build fixture export in memory and checks they match
the committed files byte for byte, and rebuilds the deterministic
section of the Deep results. `python3 level-3-deep/run_deep.py` reruns
the timed study, but it rewrites the recorded results_deep.json with
this machine's timings, so restore it afterwards with
`git checkout level-3-deep/results_deep.json`. The site build runs a
JavaScript known-answer check against every results file first.

Go and Rust: go, rustc and cargo were not on the build VM. Every Go
and Rust file is labelled UNEXECUTED and no result comes from them.

## Lifecycle

- Question: DONE 2026-11-04
- Proposal: OPEN
- Baseline: DONE 2026-11-05
- Build: OPEN
- Evaluate: OPEN
- Report: OPEN
- Review: OPEN
- Release: OPEN

Question: SPEC scaffold, commit 252ca81. Proposal: PROPOSAL.md is a
draft, never locked. Baseline: the Python reference of both tools and
the recorded Deep timing run. Build: the Go and Rust tracks are written
but never compiled. Release: the tags v0.1, v0.5 and v1.0 predate this
standard and are kept; they are not a v1.0 verdict under it.

## Layout

| Path | What it holds |
| --- | --- |
| PROPOSAL.md | Question, scope, hypotheses (not locked), prior work, next cycle (was SPEC.md, NOVELTY.md, DOSSIER.md, ROADMAP.md) |
| REPORT.md | Hypotheses scored with misses, where each number comes from, the Learn, Build and Deep records, review notes |
| level-1-learn/ | Python reference: health and routing service, five-rule manifest checker, runner; results_learn.json (results); Go and Rust teaching sources (UNEXECUTED) |
| level-2-build/ | Python reference: cancellable pool, eight-rule checker, runner, fixture export; results_build.json and fixtures_build.json (results); BUILD-SPEC.md (design); Go module and Cargo project (UNEXECUTED) |
| level-3-deep/ | Profile-and-fix study: profile_deep.py, run_deep.py, timing_repeats.py; results_deep.json and results_deep_repeats.json (evidence and results); DEEP-SPEC.md (design); Go pprof and Rust trait designs (UNEXECUTED) |
| tests/ | Unit tests per level, layout and no-public-grade test, results regeneration test, fixture parity test |
| docs/decisions/ | Records of hard-to-reverse choices |
| site/ | The live dashboard, built from the files above |
| fanout/, PUBLICITY.md | Drafted posts and the channel log (nothing posted) |

There is no separate experiments/ or results/ folder: each results
file is written by the runner beside its code and is the evidence
itself (docs/decisions/0001). There is no src/ for the same reason.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
