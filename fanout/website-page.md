# Website project page copy: systems-languages-lab

Site: jesunahmadushno.com
Status: COPY ONLY, draft for the project page. Dated 2026-11-05.
Nothing on any website was changed by this file.

## Headline

systems-languages-lab: Go and Rust shapes for ML platform work, executed as a Python reference and labelled honestly

## Summary

systems-languages-lab is an open systems languages study built
by Jesun Ahmad Ushno as project P21 in Roadmap v3. It builds a
model endpoint health and routing service in the shape of a Go
service, and a tool manifest checker in the shape of a Rust CLI,
three times: a small Learn version, a cancellable Build version
with structured errors, and a Deep profile and fix study. It
runs on the Python standard library only, for every executed
step.

One scope fact, stated plainly. Go and Rust sources are UNEXECUTED at every level: go, rustc, and cargo were not found on the build VM, nothing was installed, and no Go or Rust code was compiled, run, or tested. Every executed level is a Python standard library reference only, run on the Muse VM. All health probes and tool manifests are scripted fixtures, authored for teaching: no real HTTP endpoint was served or probed, and no real MCP manifest file was read. The Deep speedup is an order of magnitude effect, not a constant: timing on a shared VM varies by run, and the exact ratio is a property of the recorded run.

Status: v1.0, 2026-11-05. Learn, Build, and Deep are done.
Total tests: 46 checks, plus the scaffold smoke test.

## Results (Python reference only)

| Level | Scenario | Key result | Notes |
| --- | --- | --- | --- |
| Learn | 6 endpoints, 8 requests, 6 tools | 4 of 6 healthy, 6 of 8 routed, 4 of 6 tools unsafe, 7 flags | 5 checker rules; 15 checks |
| Build | 10 endpoints, 12 requests, 8 tools | 8 of 10 healthy, 11 of 12 routed, 5 of 8 tools unsafe, 14 flags | Pre-cancelled run 0 probed, 10 skipped; 22 checks |
| Deep | 200 endpoints, 20,000 requests | route_build 95.9 percent of routing time; indexed median 2.434 s to 0.0765 s, records identical | Speedup is order of magnitude, not a constant; 9 checks |

## Honest limits

- Python reference only: Go and Rust sources are UNEXECUTED.
- Scripted fixtures: no real HTTP probe, no real MCP manifest.
- No compiler, formatter, or linter check on the Go or Rust sources.
- Run on the Muse VM, not the assigned BlackBoxV3 fleet node.

## Links

- GitHub repo: https://github.com/JesunAhmadUshno/systems-languages-lab
- Release v0.1 (Learn): https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.1
- Release v0.5 (Build): https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.5
- Release v1.0 (Learn, Build, Deep): https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v1.0
- Tutorial: fanout/tutorial.md in the GitHub repo
- Blog post draft: fanout/blog-post.md in the GitHub repo

## License note

Code: Apache-2.0. Tutorials: CC BY 4.0.
