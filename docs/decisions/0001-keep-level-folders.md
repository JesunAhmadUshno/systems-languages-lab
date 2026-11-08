# 0001: Keep the level folders as the code and results folders

Date: 2026-11-08. Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

The portfolio standard v2 puts code in src/, raw evidence in
experiments/ and scored results in results/. This repo grew as three
level folders (level-1-learn, level-2-build, level-3-deep), each
holding its code, its Go and Rust sources, its design spec and the
results file its runner writes. The tags v0.1, v0.5 and v1.0, their
release tarballs, the tests, the fan-out pieces and the dashboard all
cite these paths.

## Decision

Keep the three folders and their file names. The README layout table
maps each folder to its role. Each results file stays beside the
runner that writes it; it is both the evidence and the result, so
there is no separate experiments/ or results/ folder. The level
READMEs are folded into REPORT.md.

## Consequences

No path cited by a release, a test or the dashboard breaks. The cost
is that folder names describe the old ladder rather than the content.
A later change can move them into src/ if the Go and Rust toolchain
work makes that worth it.
