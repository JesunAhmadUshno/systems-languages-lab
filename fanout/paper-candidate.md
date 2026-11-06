# Paper candidate brief: profile-and-fix bottleneck note for per-request routing

Project: P21 systems-languages-lab
Status: CANDIDATE, brief dated 2026-11-05
Submission note: submission is Jesun's tap. Nothing is submitted by
this brief, and no venue has been contacted.

## Working title

Profile first, then index: a bottleneck note on per-request
filter and sort in a model endpoint router, measured on a
Python reference

## Candidate claim, in one line

On a deterministic 200 endpoint, 20,000 request workload, a
Python router that filters and sorts healthy candidates on
every request spends 95.9 percent of its routing time in that
one function, and replacing it with a per-model best endpoint
index cuts the median batch time by an order of magnitude with
identical routing records; the claim is this measured
profile-and-fix result on the Python reference, not any Go or
Rust performance, because the Go and Rust sources are
UNEXECUTED.

## Scope, stated first

Go and Rust sources are UNEXECUTED at every level: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. Every executed level is a Python standard library reference only, run on the Muse VM. All health probes and tool manifests are scripted fixtures, authored for teaching: no real HTTP endpoint was served or probed, and no real MCP manifest file was read. The Deep speedup is an order of magnitude effect, not a constant: timing on a shared VM varies by run, and the exact ratio is a property of the recorded run. The SPEC records no paper angle for this project: it
publishes an essay instead (the pprof bottleneck story), and
this brief follows that ruling in substance. It is a bottleneck
note candidate, shaped like a short paper brief so the numbers
and limits are reviewer ready, not a claim that a paper exists.

## Abstract draft

Based only on the measured v1.0 results recorded in the repo.
Scope limits are stated inside the abstract, not after it.

Model endpoint routers often repeat fixed work per request.
This candidate reports a three level open study of a health
and routing service and a tool manifest checker, executed as a
Python standard library reference on the Muse VM. Learn:
4 of 6 endpoints healthy, 6 of 8 requests routed, 4 of 6 tools
unsafe with 7 flags. Build: a cancellable pool, 8 of 10
endpoints healthy, 11 of 12 requests routed, 5 of 8 tools
unsafe with 14 flags. Deep profiled the Build router with
cProfile on a deterministic workload of 200 endpoints and
20,000 requests generated from the Build fixtures: route_build
took 1.780 s of 1.856 s cumulative (95.9 percent), with 16,000
sorts and 640,000 sort key calls. The fix, an indexed router
keeping the best healthy record per model under the exact
Build ordering, cut the pooled median batch time from 2.434 s
to 0.0765 s over 5 repetitions with 1 warmup, with baseline
and indexed routing records identical as full lists (16,000
routed, 4,000 unrouted). The speedup is an order of magnitude
effect, not a constant: medians moved between study runs on
the shared VM. Go and Rust sources at every level are
UNEXECUTED, all probes and manifests are scripted fixtures,
and no real HTTP endpoint or MCP manifest was used. The
candidate claims the profile-and-fix method and its measured
Python result on this workload, nothing about compiled
languages.

## Method outline

1. Learn and Build reference. Worker pool over scripted probe
   fixtures, lowest latency healthy routing with name tie
   break, and a 5 then 8 rule manifest checker.
2. Workload. 200 endpoints cycling the 10 Build endpoints with
   a deterministic latency offset; 20,000 requests cycling
   chat, embed, vision, code, unknown.
3. Profile. cProfile over the baseline routing workload; the
   hypothesis (per-request filter and sort dominates) stated
   in DEEP-SPEC.md before the run.
4. Fix. IndexedRouter: one linear build of the best healthy
   record per model; one dict lookup per request; the timing
   includes one index build per batch.
5. Correctness. Full record list equality on the workload and
   on the Build fixtures, asserted by the Deep tests.

## Results table

Python reference, 2026-11-05, Muse VM, from the level
READMEs and results files in the repo.

| Item | Result |
| --- | --- |
| Learn | 4 of 6 healthy, 6 of 8 routed, 4 of 6 tools unsafe, 7 flags |
| Build | 8 of 10 healthy, 11 of 12 routed, 5 of 8 tools unsafe, 14 flags |
| Deep profile | route_build 1.780 of 1.856 s cumulative, 95.9 percent |
| Deep timing | Median 2.434 s to 0.0765 s per 20,000 request batch, 5 pooled repetitions, 1 warmup |
| Tests | 46 checks in total, plus the scaffold smoke test |

## Limits a reviewer will raise, stated first

- Python only: no Go or Rust execution, profile, or timing.
- Scripted fixtures at scale: the workload registry is
  generated from 10 authored fixtures.
- Timing noise: the ratio is run dependent; order of
  magnitude only, never a constant.
- Single workload shape and a single best endpoint rule; a
  ranked candidate router would break the index equivalence.
- Index staleness: the index is correct only for a fixed
  health record set and must be rebuilt after re-probing.

## What would strengthen the candidate

Each item is v1.1 backlog in ROADMAP.md, not done work: run
the Go pprof study for real on the same workload, repeat the
timing study on a dedicated node, and probe a real HTTP
endpoint instead of scripted fixtures.

## Venue note

No venue is named as submitted or contacted. Venue choice and
any submission click are Jesun's tap only.
