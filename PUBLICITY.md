# PUBLICITY: systems-languages-lab (P21)

Publicity log under the documentation and publishing standard,
Section 7. Every finished level produces its written fan-out set.
Drafts are prepared by the loop. Actual social posting follows
the standing platform rules and gates. The loop itself never posts
to social.

Project state: v1.0, Learn, Build, and Deep done 2026-11-05,
46 checks passing plus the scaffold smoke test. Every executed level is a Python reference
only: Go and Rust sources are UNEXECUTED at every level, the
toolchains were missing on the build VM, all probes and manifests
are scripted fixtures, and the Deep speedup is an order of
magnitude effect, not a constant.

## Fan-out set (from the v1.0 README)

Written fan-out set for v1.0, in fanout/: blog post, tutorial,
website page copy, LinkedIn draft (held, not posted), paper
candidate brief (profile-and-fix bottleneck note; submission is
Jesun's tap, nothing submitted), and release notes covering
v0.1, v0.5, and v1.0. Every piece states plainly that Go and
Rust sources are UNEXECUTED, every executed level is a Python
reference only, all probes and manifests are scripted fixtures,
and the Deep speedup is an order of magnitude effect, not a
constant. Channel outcomes are logged in this file. Live dashboard (replaces the earlier one-page docs summary at the same URL): https://jesunahmadushno.github.io/systems-languages-lab/

Grading of each piece is kept internal and is not shown here.

## Actions polish pack (2026-11-05)

Applied through a pull request on 2026-11-05, following the Actions
polish pack standard. The pack adds: CI on a Python 3.11 and 3.12
matrix with a ruff lint step (the pre-existing CI steps preserved:
scaffold smoke test; plus per-level test and runner steps for Learn,
Build, and Deep, following the proven pack pattern), CodeQL
scanning, Dependabot for pip and GitHub Actions, a release workflow
that attaches a source tarball named
systems-languages-lab-<tag>.tar.gz to v* tag releases, Labeler,
Greetings (snake_case inputs for actions/first-interaction@v3:
repo_token, issue_message, pr_message), Stale in comment-only mode
(days-before-close: -1, never closes), and a docs summary page at
docs/index.md for GitHub Pages. Ruff scope is recorded in
ruff.toml (E, F, I, line-length 120). Ruff fixes in this pull
request were style only: 25 initial errors (12 E402 sibling imports
fixed with noqa markers, 12 E501 long lines wrapped or expanded with
no change to any value, 1 I001 import format fixed by ruff fix),
with no change to behaviour, to any imported name that is used, or
to any string value. Learn and Build results files stayed
byte-identical across the runners; the Deep results file differs
only in its timing section across runs by design, and its
timing-only diff was restored, so no results file changes in this
pull request. requirements.txt records the
standard-library-only fact for the executed Python (Go and Rust
unexecuted) so Dependabot pip has a manifest to watch.

| Channel | Outcome on 2026-11-05 |
| --- | --- |
| GitHub Pages | Docs page added at docs/index.md in this pull request. Pages enablement and live build status are verified after merge and recorded in the batch ledger; no live claim is made in this file before that check. |
| PyPI publishing | Held: needs a PyPI token, a new credential. Jesun's tap only. Not set up. |
| Social channels (LinkedIn, X, Facebook, Instagram, Threads) | Held: no posts made. The loop never posts to social; Threads waits for Jesun's tap per post under the standing gates. |

## v1.0 fan-out set (2026-11-05)

Written fan-out set prepared in this cycle, in fanout/. Every
piece states plainly that Go and Rust sources are UNEXECUTED
at every level, every executed level is a Python reference
only, all health probes and tool manifests are scripted
fixtures, and the Deep speedup is an order of magnitude
effect, not a constant. Every number is sourced from the repo
files (README.md, DOSSIER.md, the three level READMEs, and
the three results files). Tutorial commands were verified by
running them; the full suite (46 checks plus the scaffold
smoke test) passes, Learn and Build results files stayed
byte-identical across the runners, and the Deep results file
differs only in its timing section across runs by design, with
its timing-only diff restored.

Jev claim_check on the blog main results claim (extracted byte
exact from fanout/blog-post.md by script): model jev-1.13.0,
699 input tokens, 20 output tokens, question id supported,
noul 0.82, route REVIEW (claim_check bands: clear at 0.85 or
above, block at 0.10 or below, review between). Spec and
results are in the goal hidden_files
(jev-p21-fanout-claim-spec-2026-11-05.json and
jev-p21-fanout-claim-results-2026-11-05.json).

| Channel | Piece | Outcome on 2026-11-05 |
| --- | --- | --- |
| GitHub release v0.1 | Learn release | Live: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.1 |
| GitHub release v0.5 | Build release | Live: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v0.5 |
| GitHub release v1.0 | Learn, Build, Deep release | Live: https://github.com/JesunAhmadUshno/systems-languages-lab/releases/tag/v1.0 |
| GitHub Pages | Docs summary page | Live, built: https://jesunahmadushno.github.io/systems-languages-lab/ (legacy, main, /docs, verified HTTP 200 after the polish pack merge) |
| Repo (blog) | Blog post draft | fanout/blog-post.md, repo draft. Not posted to any blog platform. |
| Repo (tutorial) | Tutorial draft | fanout/tutorial.md, repo draft. Every command verified by running it in this cycle. |
| Repo (website) | Website page copy draft | fanout/website-page.md, copy only. No website was changed by this file. |
| LinkedIn | Post draft | fanout/linkedin-post.md, DRAFT NOT POSTED. Held: posting follows the standing platform rules; the link is carried as the first-comment line in the draft, per the LinkedIn rule. |
| Paper | Candidate brief | fanout/paper-candidate.md. Submission is Jesun's tap; nothing submitted, no venue contacted. |
| Repo (release notes) | Release notes | fanout/release-notes.md, covering v0.1, v0.5, and v1.0 with Python reference results and release links verified with gh release list. |
| X | Social post | Held: no post made. The loop never posts to social; drafts only under the standing platform rules. |
| Facebook | Social post | Held: no post made. Standing Facebook rule applies (no link in body or comments, keyword call to action by DM) and the loop never posts to social. |
| Instagram | Social post | Held: no post made. Standing Instagram rule applies (link in bio) and the loop never posts to social. |
| Threads | Social post | Held: awaiting Jesun's tap. Every Threads post needs his one-tap pre-approval, hash-locked on exact text and media. |
| Video | 3D playbook video | Held: flagship video production runs through the January engine queue. No video produced in this cycle. |
| Book | Book chapter | Held: chapter drafted from finished projects under the journey publishing plan; no chapter file is claimed in this cycle. |
