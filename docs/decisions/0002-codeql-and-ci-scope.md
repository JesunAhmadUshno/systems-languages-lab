# 0002: Scan and test only the code that has ever run

Date: 2026-11-08. Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

The repo holds Python (executed), JavaScript (the dashboard,
executed at build time), and Go and Rust sources that have never been
compiled. CodeQL for Go needs a working build, so adding Go or Rust to
CodeQL or CI would be the first time either track is compiled.

## Decision

CI and CodeQL cover Python and JavaScript. Go and Rust are added in
the change that first compiles and tests them (PROPOSAL.md, next
cycle item 1), so that first run is recorded on its own, with its
results, and not hidden inside a tooling change.

## Consequences

A syntax error in the Go or Rust sources is still not caught by CI,
as REPORT.md states under Failure modes.
