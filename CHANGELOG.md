# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning. The tags v0.1, v0.5 and v1.0 were
cut before the portfolio standard v2 and are kept; under the standard
the verdict is Draft (README.md).

## [Unreleased]

### Changed
- 2026-11-08: Restructured to the portfolio standard v2. README is the
  abstract (question, headline with its interval, field, job family,
  verdict, reproduce, lifecycle, layout). PROPOSAL.md (draft, not
  locked) replaces SPEC.md, NOVELTY.md, DOSSIER.md and ROADMAP.md.
  REPORT.md replaces the three level READMEs and docs/research-review.md
  and scores every hypothesis, misses shown. docs/index.md, the old
  one-page summary already replaced by the dashboard, is removed; its
  scope paragraph opens REPORT.md. Verdict re-scored as Draft, not
  pre-registered: the Go service and Rust CLI have never run.
- 2026-11-08: Internal grades removed from every public file (README,
  REPORT, PUBLICITY, fan-out pieces, dashboard). The dashboard's grades
  window is now a lifecycle and verdict window read from README.md.
- 2026-11-08: CI sets read-only token permissions, runs ruff, the full
  test suite (including a new results regeneration test and a layout
  and no-public-grade test) and every runner on Python 3.11 and 3.12,
  and builds the dashboard. CodeQL scans Python and JavaScript.
  Dependabot watches the site's npm packages. Decisions 0001 (keep the
  level folders) and 0002 (scan only code that has run) recorded.

### Fixed
- 2026-11-08: A line in level-3-deep/timing_repeats.py over the ruff
  line limit, which had turned CI red on main since 2026-11-07. Wrapped,
  no change in behaviour.

### Added
- 2026-11-07: Live dashboard (site/) with JS ports of the Python
  reference and a build-time known-answer check; Pages workflow.
- 2026-11-07: Repeat timing run (30 paired repetitions, bootstrap
  interval, registry size sweep) in level-3-deep/timing_repeats.py.
- 2026-11-07: Build fixtures exported to JSON with a parity test.
- 2026-11-07: Research review (now in REPORT.md, Review notes).
- 2026-11-07: vite upgraded to 6.4.5 to clear npm audit advisories.

## [1.0] - 2026-11-05

### Added
- Deep: cProfile bottleneck study on the Build routing code and the
  indexed router fix, records identical; Rust Rule trait design and Go
  pprof study design (UNEXECUTED).
- Fan-out set in fanout/ and the channel log in PUBLICITY.md.
- Actions polish pack: CI matrix, CodeQL, Dependabot, release
  artifacts, Labeler, Greetings, Stale.

## [0.5] - 2026-11-05

### Added
- Build: cancellable worker pool with error chains and an eight-rule
  manifest checker (Python reference); Go module and Cargo project
  (UNEXECUTED).

## [0.1] - 2026-11-05

### Added
- Learn: health and routing service and five-rule manifest checker
  (Python reference); Go and Rust teaching sources (UNEXECUTED).
- 2026-11-04: Wave 0 scaffold: SPEC, dossier v1, novelty draft.
