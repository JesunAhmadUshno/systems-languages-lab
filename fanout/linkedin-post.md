# LinkedIn post draft: P21 systems-languages-lab v1.0

Status: DRAFT NOT POSTED
Date drafted: 2026-11-05
Author: Jesun Ahmad Ushno
Rule for this platform: the link goes in the first comment, not in the
post body. The first comment line is at the end of this file.

## Post body

Systems languages decide whether ML platforms hold up. I built
the two shapes, a Go-style routing service and a Rust-style
manifest checker, and I am labelling the limit up front: the
executed code is a Python reference only.

systems-languages-lab v1.0 is done: Learn, Build, and Deep, all
open, Python standard library only for every executed step.

The scope, up front: Go and Rust sources are UNEXECUTED at
every level. The toolchains were missing on the build VM,
nothing was installed, and no Go or Rust code was compiled or
run. All probes and manifests are scripted fixtures. That
limit is in the post, not under it.

Learn: 4 of 6 endpoints healthy, 6 of 8 requests routed, 4 of
6 tools unsafe with 7 flags across 5 rules.

Build: 8 of 10 endpoints healthy, 11 of 12 requests routed, a
pre-cancelled run probing 0 and skipping 10, and 5 of 8 tools
unsafe with 14 flags across 8 rules.

Deep: on 200 endpoints and 20,000 requests, profiling put the
per-request filter and sort at 95.9 percent of routing time.
Indexing the best healthy endpoint per model once cut the
median batch from 2.434 s to 0.0765 s, with identical routing
records. That speedup is an order of magnitude effect, not a
constant: shared VM timing varies by run.

Grades, house scale: Learn 7,900, Build 7,800, Deep 7,900 of
10,000. 46 checks in total, plus the smoke test. The toolchain
port and the real Go pprof run are the first v1.1 items, and
they are not claimed here.

What did profiling last change in code you thought was fast
enough?

## First comment (post this as the first comment, per the standing rule)

Repo, releases v0.1, v0.5, and v1.0, and the full tutorial: https://github.com/JesunAhmadUshno/systems-languages-lab
