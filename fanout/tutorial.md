# Tutorial: P21 systems-languages-lab, course module

Module: P21-systems-languages-lab
By Jesun Ahmad Ushno
Date: 2026-11-05
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the systems-languages-lab repo, run all three
levels, run the test suite for each level, and read your own
results against the recorded v1.0 numbers. Every command below
was verified by running it in this fan-out cycle. The project
needs Python 3.11 or 3.12 and uses the standard library only
for every executed step. No Go or Rust toolchain, GPU, cluster,
or credential is needed, because no Go or Rust code runs here.

One scope fact governs every step: Go and Rust sources are UNEXECUTED at every level: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. Every executed level is a Python standard library reference only, run on the Muse VM. All health probes and tool manifests are scripted fixtures, authored for teaching: no real HTTP endpoint was served or probed, and no real MCP manifest file was read. The Deep speedup is an order of magnitude effect, not a constant: timing on a shared VM varies by run, and the exact ratio is a property of the recorded run.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/systems-languages-lab.git
cd systems-languages-lab
```

Optional smoke check, before the levels:

```text
python tests/test_smoke.py
```

Expected: scaffold smoke test: PASS, 8 files present.

## Step 1: Level 1, Learn, health routing and manifest checker

Read level-1-learn/README.md first.

```text
python level-1-learn/run_learn.py
python tests/test_learn_systems.py
```

Expected: health 4 of 6 endpoints healthy; routing 6 of 8
requests routed, 2 unrouted; manifest 4 of 6 tools unsafe, 7
total flags; 15 tests OK. The runner writes
level-1-learn/results_learn.json deterministically.

## Step 2: Level 2, Build, cancellable pool and extended checker

Read level-2-build/README.md and level-2-build/BUILD-SPEC.md.

```text
python level-2-build/run_build.py
python tests/test_build_systems.py
```

Expected: health 8 of 10 endpoints healthy; routing 11 of 12
requests routed, 1 unrouted; manifest 5 of 8 tools unsafe, 14
total flags; cancellation: cancelled, 10 skipped (the
pre-cancelled run); 22 tests OK. The runner writes
level-2-build/results_build.json deterministically.

## Step 3: Level 3, Deep, profile and fix bottleneck study

Read level-3-deep/README.md and level-3-deep/DEEP-SPEC.md.

```text
python level-3-deep/run_deep.py
python tests/test_deep_systems.py
```

Expected: workload 200 endpoints, 20000 requests; routing
identical baseline vs indexed: True; build fixture identical:
True; deterministic repeat identical: True; 9 tests OK. Your
baseline and indexed median seconds will differ from the
recorded 2.434 s and 0.0765 s: the Deep speedup is an order of
magnitude effect, not a constant, and timing on any machine
varies by run. The runner writes level-3-deep/results_deep.json;
its deterministic section should match, its timing section is
your machine's measurement.

## Step 4: Full suite

```text
python tests/test_smoke.py
python tests/test_learn_systems.py
python tests/test_build_systems.py
python tests/test_deep_systems.py
python -m unittest discover -s tests
```

Expected: 46 checks in total (15 Learn, 22 Build, 9 Deep), all
passing, plus the scaffold smoke test.

## If your numbers differ

Check the results files first. Learn and Build results carry
counts and names only, with no wall time, so they should match
the recorded v1.0 values exactly on the same code. Deep results
match in the deterministic section; the timing section is
expected to differ. A count difference means the code changed.
No difference can come from Go or Rust: those sources are
UNEXECUTED and no command above runs them.
