# Proposal: systems-languages-lab (P21)

Status: DRAFT, not locked. This repo is **not pre-registered**. The
scope below was committed on 2026-11-04 (commit 252ca81) before any
code, but it states scope and acceptance criteria, not hypotheses with
pass lines and an analysis plan, so it does not count as a locked
proposal. Every result in REPORT.md was produced without a locked
plan. A future confirmatory cycle locks its own PROPOSAL section with
a tag (proposal-v1) before it runs, and only then can the verdict move
past Functional.

This file brings together what used to live in SPEC.md (scope and
acceptance criteria), NOVELTY.md (proposed novelty), DOSSIER.md (past,
present, future) and ROADMAP.md (the v1.1 backlog). Their text is kept
below, moved unchanged apart from headings.

## Question

What do Go and Rust buy over Python for two small ML platform tools,
a model-endpoint health and routing service and an MCP tool-manifest
checker, and does profiling the routing service find a bottleneck that
can be removed without changing any routing decision?

## Scope (from SPEC.md, Wave 0 scaffold, 2026-11-04)

Phase skill: spec-driven-development (house engineering pipeline).
Scope and acceptance criteria below are the v2 section text.

Fleet node: BlackBoxV3. Wave: Wave 7.
Hiring evidence: 4 of 5 (register Category 2 holds 65 items; Go and Rust named at Apple, Microsoft, xAI) [confirmed, fleet and scoring pass 2026-11-04, or the decision pack for P23 to P29].

systems-languages-lab: NEW

Subject: systems languages for ML platform work: Go and Rust. Evidence: register Category 2 (65 items); items 78 to 82 name the two builds; Apple and Microsoft postings name Go; xAI and Microsoft name Rust [confirmed].
Track A, Go:
- Learn: one small Go service: the model endpoint health and routing service that P12's registry points at. Goroutines and channels run a real concurrent worker.
- Build: Go modules, formatting, and test tooling used as a native would; error handling and context cancellation done the Go way (register items 80, 128).
- Deep: profile the live service with pprof, remove one real bottleneck, publish the before and after (register item 129); one code-reading note on a section of a Go open source codebase (register item 132; Kubernetes platform code is Go).
Track B, Rust:
- Learn: one small Rust CLI in the P09 toolkit family: a tool manifest checker that reads MCP tool definitions and flags unsafe rules.
- Build: ownership and borrowing handled in real code; error handling with Result types and clean error chains (register items 81, 82, 130).
- Deep: traits and generics used to share real code across the CLI's checkers, with a short note on what Rust bought and what it cost against the same tool in Python (register item 131).
Fan-out: Book chapter "Two More Languages". Paper angle: none. This project publishes an essay instead (the pprof bottleneck story), and this file says so rather than dressing an essay as a paper. Course module: P21-systems-languages-lab.

### Acceptance criteria (scaffold level, from SPEC.md)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.

## Hypotheses (not locked)

These are the claims the work so far was built to test. They were
written after the scaffold, not locked before the results; REPORT.md
scores each one and shows the misses.

- H1, Go service: the health and routing service runs as real Go,
  with goroutines and channels doing the concurrent probe work, and
  reproduces the Python reference counts.
- H2, Rust checker: the manifest checker runs as real Rust, with
  ownership, borrowing and Result error chains, and reproduces the
  Python reference counts.
- H3, bottleneck (stated in level-3-deep/DEEP-SPEC.md before the fix
  code ran, committed in the same change as the results): route_build
  is the routing bottleneck, because it filters and sorts on every
  request.
- H4, fix correctness (DEEP-SPEC.md): an index removes the bottleneck
  with routing records identical to the baseline, as full lists.
- H5, Rust against Python cost note: a short, evidence-based note on
  what Rust bought and what it cost against the same checker in Python.

## Prior work

### Proposed novelty (from NOVELTY.md)

Status: DRAFT, PROPOSED. Not verified. This text does not move into any public post, paper, or profile until the Jev claim_check gate passes on the exact text.

#### Proposed claim

Against language tour examples in Go and Rust: this project aims to differ in the way its SPEC.md section text defines (a from-zero or self-hosted build, measured in public, on a named home fleet, with the failure modes written down). The exact difference is stated at the project's wave, after the prior art is re-read.

#### Prior art table

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| language tour examples in Go and Rust | See DOSSIER.md, Past | PROPOSED, see the claim above | NO MEASUREMENT YET |

#### Honest size

If the novelty proves small, this file will say so and name the real value instead (a cleaner reproduction, a better benchmark, a first public dataset). No novelty is invented to fill this section.

### Past (from DOSSIER.md)

Prior art for this project is named in NOVELTY.md (language tour examples in Go and Rust). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

### Present (from DOSSIER.md)

Current demand evidence: hiring value 4 of 5 (register Category 2 holds 65 items; Go and Rust named at Apple, Microsoft, xAI) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

### Related work (from docs/research-review.md, 2026-11-07)

The repo has no dated literature review, and NOVELTY.md is still an
unverified draft. The study's value is a small, fully reproducible
profile-and-fix worked example with a correctness invariant. It
follows standard practice from:
- Python standard library documentation, "The Python Profilers"
  (cProfile and pstats), the profiler used here;
- the Go blog, "Profiling Go Programs" (Russ Cox, 2011), and the
  runtime/pprof and net/http/pprof package documentation, which the
  UNEXECUTED Go study plan follows;
- The Rust Programming Language book, chapters on traits, generics
  and trait objects, which the UNEXECUTED Rule trait design follows.

## Design

The executed design is recorded in level-2-build/BUILD-SPEC.md and
level-3-deep/DEEP-SPEC.md (each written before its level's code, in
the same commit as the results). The Go pprof study design and the
Rust Rule trait design are in REPORT.md, Deep study record.

## Next cycle (the v1.1 backlog, from ROADMAP.md)

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

### Future (from DOSSIER.md)

The v1.1 backlog sits in "Next cycle" above (formerly ROADMAP.md): the
toolchain port, the Go pprof study run for real, the Go code
reading note, real HTTP probes and a real MCP manifest read, and
a dedicated node timing repeat. Any forecast about this field is
[unverified] unless a dated primary source is added here.
