// Known-answer check, run by `npm run build` before vite: the JS ports in lab.js must
// reproduce every count in the three recorded results files and the REPORT.md figures.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as L from './lab.js';

const root = new URL('../../', import.meta.url);
const read = (p) => fs.readFileSync(new URL(p, root), 'utf8');
const json = (p) => JSON.parse(read(p));
const learn = json('level-1-learn/results_learn.json');
const build = json('level-2-build/results_build.json');
const deep = json('level-3-deep/results_deep.json');
const fx = json('level-2-build/fixtures_build.json');
const deepMd = L.section(read('REPORT.md'), 'Deep study record');
assert.ok(deepMd.length > 1000, 'REPORT.md Deep study record section');

// 1. Routing: Learn 6 of 8 (beta-chat 4, alpha-embed 2), Build 11 of 12, full record lists.
for (const [name, res] of [['learn', learn], ['build', build]]) {
  const models = res.routing_records.map((r) => r.model);
  const recs = L.runRouting(models, res.health_records);
  assert.deepEqual(recs, res.routing_records, `${name} routing records`);
  assert.deepEqual(L.summariseRouting(recs), res.routing, `${name} routing summary`);
  assert.deepEqual(L.summariseHealth(res.health_records), res.health, `${name} health summary`);
}
assert.equal(learn.routing.requests_routed, 6);
assert.equal(build.routing.requests_routed, 11);
assert.deepEqual(fx.request_models_build, build.routing_records.map((r) => r.model), 'fixture request order');

// 2. Manifest checker: 5 of 8 unsafe, 14 flags, high 3, medium 6, low 5, per-tool records.
const toolRecs = L.checkAll(fx.tools_build, fx.severity);
assert.deepEqual(toolRecs, build.tool_records, 'build tool records');
const man = L.summariseManifest(toolRecs, fx.rule_ids_build, fx.severity);
assert.deepEqual(man, build.manifest, 'build manifest summary');
assert.deepEqual([man.tools_unsafe, man.total_flags, man.flags_per_severity.high, man.flags_per_severity.medium, man.flags_per_severity.low], [5, 14, 3, 6, 5]);
// Learn's six tools are the first six Build tools under rules R1 to R5 only.
learn.tool_records.forEach((t, i) => assert.deepEqual(L.checkTool(fx.tools_build[i], ['R1', 'R2', 'R3', 'R4', 'R5']), t.flags, `learn ${t.name}`));

// 3. Cancellable pool: cancel at 0 -> 0 probed, 10 skipped, cancelled; never -> 10 probed, completed.
assert.deepEqual(L.simulatePool(fx.endpoints_build, 0).info, build.cancellation);
const full = L.simulatePool(fx.endpoints_build, null);
assert.deepEqual(full.info, build.pool);
assert.deepEqual(full.records, build.health_records, 'pool records incl. error chains');
assert.equal(L.chainString(build.health_records.find((r) => r.name === 'gamma-chat').error_chain), 'probe gamma-chat: caused by: probe transport failed: 503 unavailable');

// 4. Bottleneck race workload: 200 endpoints, 20,000 requests, 16,000 routed, records identical.
const w = deep.deterministic.workload;
const eps = L.makeWorkloadEndpoints(fx.endpoints_build, w.endpoints);
const recs = L.simulatePool(eps, null).records;
assert.deepEqual(L.summariseHealth(recs), deep.deterministic.health, 'deep health');
const reqs = L.makeWorkloadRequests(w.models, w.requests);
const base = L.runRouting(reqs, recs);
const idx = L.runRouting(reqs, recs, L.indexedRouter(recs));
assert.deepEqual(base, idx, 'baseline and indexed records identical');
assert.deepEqual(L.summariseRouting(base), deep.deterministic.baseline_routing);
assert.deepEqual(L.summariseRouting(idx), deep.deterministic.indexed_routing);
assert.equal(deep.deterministic.routing_records_identical, true);
const bfx = L.runRouting(fx.request_models_build, build.health_records, L.indexedRouter(build.health_records));
assert.deepEqual(L.summariseRouting(bfx), deep.deterministic.build_fixture_routing);
const t0 = Date.now();
const tm = L.timeMedian(() => L.runRouting(reqs, recs), 2, () => Date.now());
assert.equal(tm.times.length, 2);

// 5. Recorded profile and timing: 95.9% share, median ratio 31.8x as REPORT.md states.
const prof = L.parseProfile(deep.profile_top);
const rb = prof.rows.find((r) => r.fn.includes('(route_build)'));
assert.equal(prof.total, 1.856);
assert.equal((rb.cumtime / prof.total * 100).toFixed(1), '95.9');
assert.ok(new RegExp(`\\(${(rb.cumtime / prof.total * 100).toFixed(1).replace('.', '\\.')}\\s+percent\\)`).test(deepMd), 'README share');
const rs = L.ratioStats(deep.timing.baseline.times_s, deep.timing.indexed.times_s);
assert.equal(L.median(deep.timing.baseline.times_s), deep.timing.baseline.median_s);
assert.equal(L.median(deep.timing.indexed.times_s), deep.timing.indexed.median_s);
assert.equal(rs.medianRatio.toFixed(1), '31.8');
assert.ok(deepMd.includes(`${rs.medianRatio.toFixed(1)} times faster`), 'README ratio');
assert.ok(rs.pairedMin < rs.medianRatio && rs.medianRatio < rs.pairedMax);
assert.ok(/quieter run measured baseline\s+([\d.]+) s and indexed ([\d.]+) s/.test(deepMd), 'variance note');

// 6. Lifecycle, verdict, test counts and the next cycle parsed from README.md, REPORT.md and PROPOSAL.md.
const readme = read('README.md');
assert.deepEqual(L.parseLifecycle(readme).map((s) => s[0]), ['Question', 'Proposal', 'Baseline', 'Build', 'Evaluate', 'Report', 'Review', 'Release']);
assert.ok(L.parseVerdict(readme), 'README verdict line');
const levelTests = ['test_learn_systems.py', 'test_build_systems.py', 'test_deep_systems.py'].map((f) => read(`tests/${f}`));
assert.equal(L.countTests(levelTests), +deepMd.match(/ran (\d+) tests OK/)[1], 'test count vs REPORT.md Deep record');
assert.equal(L.parseNumbered(L.section(read('PROPOSAL.md'), 'Next cycle (the v1.1 backlog, from ROADMAP.md)')).length, 6);
assert.equal(L.parseGoSteps(read('level-3-deep/go/internal/profile/profile.go')).length, 7);

assert.ok(L.sameData(L.summariseRouting(L.runRouting(learn.routing_records.map((r) => r.model), learn.health_records)), learn.routing), 'UI match flag');
assert.ok(L.sameData(man, build.manifest) && !L.sameData(man, learn.manifest), 'UI match flag manifest');
// 7. Repeat timing study (results_deep_repeats.json): ratios recomputed from the stored times.
const rep = json('level-3-deep/results_deep_repeats.json');
const rr = L.ratioStats(rep.paired.baseline_times_s, rep.paired.indexed_times_s);
const pairedMedian = L.median(rr.paired);
assert.ok(Math.abs(pairedMedian - rep.paired.median_paired_ratio) / rep.paired.median_paired_ratio < 0.02, `repeat median ratio ${pairedMedian}`);
assert.ok(rep.paired.bootstrap_ci95_median_ratio[0] <= rep.paired.median_paired_ratio && rep.paired.median_paired_ratio <= rep.paired.bootstrap_ci95_median_ratio[1]);
assert.equal(rep.paired.baseline_times_s.length, rep.paired.repetitions);
assert.ok(rep.sweep.every((r) => r.records_identical), 'sweep records identical');
console.log('lab ok', { learnRouted: learn.routing.requests_routed, buildRouted: build.routing.requests_routed, unsafe: man.tools_unsafe, flags: man.total_flags,
  deepRouted: L.summariseRouting(idx).requests_routed, share: (rb.cumtime / prof.total * 100).toFixed(1), ratio: rs.medianRatio.toFixed(1),
  pairedRange: [rs.pairedMin.toFixed(1), rs.pairedMax.toFixed(1)], nodeBatchMs: Date.now() - t0 });
