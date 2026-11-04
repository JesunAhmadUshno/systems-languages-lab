# SPEC: systems-languages-lab (P21)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: BlackBoxV3. Wave: Wave 7.
Hiring evidence: 4 of 5 (register Category 2 holds 65 items; Go and Rust named at Apple, Microsoft, xAI) [confirmed, fleet and scoring pass 2026-11-04, or the decision pack for P23 to P29].

## Project section text (Roadmap v2, or the v3 candidate text for P23 to P29)

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

## Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.
