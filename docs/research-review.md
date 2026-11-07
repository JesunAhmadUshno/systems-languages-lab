# Research review: systems-languages-lab (P21)

Date: 2026-11-07. Scope: the whole repo at v1.0 plus the changes on the
site/live-dashboard branch. Graded against a doctoral research rubric,
where every gap is either fixed in this change or names the exact
compute or data it needs to close.

## Verdict

A clean, honest, reproducible engineering study with a narrow evidence
base. The executed evidence is Python only. The repo's headline thesis
is about Go and Rust, and no Go or Rust line has ever been compiled or
run. That gap dominates everything else and needs toolchains this
review was not allowed to install. Within its Python scope, the study
is well specified: hypothesis written before the fix, deterministic
workload, a record-equality correctness invariant, and recorded
results files. This change adds the statistics and scaling evidence
the recorded run lacked, plus a second-language reproduction (the JS
ports on the dashboard).

| Criterion | Grade (of 10) | State after this change |
| --- | --- | --- |
| Research question | 6 | Clear for the Python study; the Go/Rust question is unanswered |
| Hypotheses | 7 | Pre-stated in level-3-deep/DEEP-SPEC.md, falsifiable, held |
| Method | 7 | Deterministic workload, cProfile, paired timing, equality invariant |
| Baselines | 7 | Baseline is the shipped Build router; no alternative index designs compared |
| Statistics and uncertainty | 6 | Recorded run: 5 reps, no interval. Repeat run adds 30 paired reps and a bootstrap 95% interval |
| Reproducibility | 8 | Stdlib only, one command per level, CI runs every level, build-time cross-language check |
| Threats to validity | 6 | Stated in READMEs; external validity is low (scripted fixtures) |
| Related work | 3 | Short list below; no literature review, and no novelty is claimed |
| Limitations | 8 | Stated plainly in every README, on the dashboard and in the grades |

## Research question

What does profiling the Build routing service show, and does an index
remove the bottleneck without changing any routing decision? The
Python study answers that. The SPEC's broader question, what Go and
Rust buy for ML platform tooling compared with Python, is still open.
Remaining gap: needs a machine with Go 1.22 or later, rustc and cargo
(free toolchains, minutes to install), then ROADMAP item 1.

## Hypotheses

DEEP-SPEC.md states before the fix that route_build is the bottleneck
because it filters and sorts on every request. The recorded profile
supports it: route_build holds 1.780 of 1.856 s cumulative (95.9
percent). Fixed in this change: the profile_deep.py docstring said
"about 92 percent", which contradicted the recorded profile. It now
says 95.9 percent.

## Method

The workload is generated deterministically from the 10 Build
fixtures (200 endpoints, 20,000 requests). The fix is checked by full
record-list equality, not by sampling. Timing uses perf_counter with a
warmup. Fixed in this change: the dashboard's known-answer check
(site/src/lab.check.mjs, run by `npm run build`) re-implements
route_build, check_tool_build, the cancellable pool, the workload
generator and IndexedRouter in JavaScript. It reproduces every count
in results_learn.json, results_build.json and the deterministic
section of results_deep.json, which is an independent second
implementation of the logic. The manifest fields, which the results
files do not carry, are exported from TOOLS_BUILD to
level-2-build/fixtures_build.json, and tests/test_site_fixtures.py
fails if that export drifts.

## Baselines

The baseline is the real shipped router, which is the right
comparison. The speedup is close to what complexity predicts: the
baseline does a filter and sort per request, roughly O(n log n) in
registry size, while the index answers each request with a dict
lookup. Fixed in this change: level-3-deep/timing_repeats.py sweeps
registry size from 50 to 800 endpoints. In results_deep_repeats.json
the baseline median grows about 17.6 times over a 16 times larger
registry while the indexed median stays flat, with identical records
at every size. The dashboard plots this sweep and runs its own sweep
in the browser, labelled as browser timings.
Remaining gap (minor): alternative fixes such as caching only the
sort or a heap per model were not compared. They need no special
compute, but they are a design question for the owner, not a missing
measurement.

## Statistics and uncertainty

The recorded run has 5 repetitions on a shared VM: baseline 1.91 to
2.61 s, indexed 0.032 to 0.130 s, and no interval. An earlier run gave
a different ratio (1.2304 s / 0.0195 s). Fixed in this change:
- the dashboard computes the median ratio (31.8x) and the paired
  per-rep ratio range (14.7x to 77.0x) from times_s, instead of
  quoting a constant;
- timing_repeats.py adds 30 interleaved paired repetitions with a
  percentile bootstrap 95 percent interval on the median paired
  ratio (10,000 resamples, seed 0). Recorded on 2026-11-07 on an
  aarch64 machine with Python 3.12.3: median paired ratio 37.84x, 95%
  CI 37.53x to 38.13x. This is a different machine from the study VM,
  so its seconds are not comparable to the recorded run, and the file
  records the machine.
Remaining gap: a quiet, dedicated-node rerun of the original study
(ROADMAP item 6, the assigned BlackBoxV3). It needs about two minutes
on that node and the owner's decision to replace the recorded
results_deep.json.

## Reproducibility

Strong. Python stdlib only. `python3 -m unittest discover -s tests`
runs 48 tests (the original 46 plus the 2 fixture-parity tests), and
each runner rewrites its results file. CI runs a Python 3.11 and 3.12
matrix with ruff, and CodeQL runs separately. Fixed in this change:
the Build and Deep READMEs said there was "no CI matrix and no
CodeQL". They now describe the CI as it is. The dashboard rebuilds
from the committed files and fails its build if any reproduced count
drifts.

## Threats to validity

- Construct: the Go and Rust claims rest on Python analogues: threads
  and queues for goroutines, an Event for context cancellation, lists
  for Result chains. Remaining gap: the toolchains above.
- Internal: shared-VM noise in the recorded run. Partly addressed by
  the repeat run. A dedicated node is still needed (see above).
- External: probes and manifests are scripted fixtures. No HTTP
  endpoint was served and no real MCP manifest was read. Remaining
  gap: ROADMAP item 4 needs a local HTTP server (free, seconds) and
  real MCP tool manifest files. No paid compute is needed, but it is
  new feature scope for a later version.
- Compilability: the Go and Rust sources get no compiler, formatter or
  linter check. Remaining gap: go vet, gofmt, cargo fmt, cargo clippy
  and cargo test on a node with the toolchains, which takes minutes.

## Related work

The repo has no dated literature review, and NOVELTY.md is still an
unverified draft. This review claims no novelty. The study's value is
a small, fully reproducible profile-and-fix worked example with a
correctness invariant. It follows standard practice from:
- Python standard library documentation, "The Python Profilers"
  (cProfile and pstats), the profiler used here;
- the Go blog, "Profiling Go Programs" (Russ Cox, 2011), and the
  runtime/pprof and net/http/pprof package documentation, which the
  UNEXECUTED Go study plan follows;
- The Rust Programming Language book, chapters on traits, generics
  and trait objects, which the UNEXECUTED Rule trait design follows.
Remaining gap: a dated prior-art pass in DOSSIER.md Past and the
owner's claim-check gate on NOVELTY.md. That needs reading time and
the owner's decision, not compute. The SPEC's Go code-reading note
(register item 132, ROADMAP item 3) is the same kind of work.

## Limitations

Stated plainly in the level READMEs, the grades, ROADMAP.md and on the
dashboard. The dashboard labels the recorded profile and timings as a
recorded replay, labels its own race as "your browser, this run", and
marks every Go and Rust file UNEXECUTED.

## Summary of changes in this branch

1. Fixed the profile_deep.py docstring share (92 to 95.9 percent).
2. Corrected the stale CI sentences in the Build and Deep READMEs.
3. Added level-2-build/fixtures_build.json, its export script, and a
   parity test.
4. Added a build-time cross-language known-answer check for every
   number the dashboard computes.
5. Added the repeat timing run: 30 paired reps, a bootstrap interval
   and a size sweep, recorded with its machine.
6. Added the dashboard (site/) and a Pages workflow.
