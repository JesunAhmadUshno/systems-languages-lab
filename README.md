# systems-languages-lab

Systems languages for ML platform work: a Go service and a Rust CLI.

Status: Learn DONE 2026-11-05, Build DONE 2026-11-05, and Deep DONE 2026-11-05, v1.0 (all executed in Python; Go and Rust toolchains missing on the build VM, see the level READMEs).
Project: P21. Fleet node: BlackBoxV3. Wave: Wave 7.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Benchmarks

| Test | Result |
| --- | --- |
| Learn (Python reference, Muse VM, 2026-11-05) | Health worker 4 of 6 endpoints healthy; router 6 of 8 requests routed; manifest checker 4 of 6 tools unsafe, 7 flags. Full record in level-1-learn/results_learn.json. |
| Build (Python reference, Muse VM, 2026-11-05) | Cancellable pool 8 of 10 endpoints healthy, 2 classified errors, pre-cancelled run 0 probed and 10 skipped; router 11 of 12 requests routed; extended checker 5 of 8 tools unsafe, 14 flags across 8 rules. Full record in level-2-build/results_build.json. |
| Deep (Python reference, Muse VM, 2026-11-05) | Profile and fix study on 200 endpoints and 20,000 requests: route_build 95.9 percent of routing time under cProfile; indexed router median 2.434 s to 0.0765 s per batch (5 pooled repetitions, 1 warmup), routing records identical to baseline. Rust traits design and Go pprof design ship as UNEXECUTED sources. Full record in level-3-deep/results_deep.json. |

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
