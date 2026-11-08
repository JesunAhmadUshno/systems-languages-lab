// JS ports of the executed Python reference code, used by the live demos.
// Every function names the Python it mirrors. lab.check.mjs runs each port
// against the recorded results files during `npm run build`.

const byKey = (a, b) => a.latency_ms - b.latency_ms || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);

// level-1-learn/health_service.py route and level-2-build/service_build.py route_build:
// healthy endpoints for the model only, lowest latency first, name ascending tie break.
// Deliberately filters and sorts on every call, exactly like the Python baseline.
export function route(model, records) {
  const cands = records.filter((r) => r.model === model && r.healthy);
  if (!cands.length) return null;
  cands.sort(byKey);
  return cands[0].name;
}

// run_routing / run_routing_build
export function runRouting(models, records, routeFn = (m) => route(m, records)) {
  return models.map((model, i) => {
    const target = routeFn(model);
    return { request: i + 1, model, routed_to: target, routed: target !== null };
  });
}

const sortObj = (o) => Object.fromEntries(Object.entries(o).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));

// summarise_routing / summarise_routing_build
export function summariseRouting(recs) {
  const per = {};
  let routed = 0;
  for (const r of recs) if (r.routed) { routed++; per[r.routed_to] = (per[r.routed_to] || 0) + 1; }
  return { requests_total: recs.length, requests_routed: routed, requests_unrouted: recs.length - routed, per_endpoint: sortObj(per) };
}

// summarise_health / summarise_health_build
export function summariseHealth(records) {
  const by = {};
  for (const r of records) {
    const s = (by[r.model] ||= { total: 0, healthy: 0 });
    s.total++; if (r.healthy) s.healthy++;
  }
  return { endpoints_total: records.length, endpoints_healthy: records.filter((r) => r.healthy).length, by_model: sortObj(by) };
}

// level-3-deep/profile_deep.py IndexedRouter: one pass keeps the best healthy record per model.
export function indexedRouter(records) {
  const best = new Map();
  for (const r of records) {
    if (!r.healthy) continue;
    const cur = best.get(r.model);
    if (!cur || byKey(r, cur) < 0) best.set(r.model, r);
  }
  return (model) => { const r = best.get(model); return r ? r.name : null; };
}

// level-2-build/manifest_build.py check_tool_build, rules R1 to R8.
export function checkTool(tool, rules = null) {
  if (!tool || typeof tool !== 'object') throw new Error('validate tool: caused by: tool is not a mapping');
  if (!(tool.name || '').trim()) throw new Error('validate tool: caused by: tool name is missing');
  const f = [];
  if ((tool.permissions || []).some((p) => p === '*' || p.endsWith(':*'))) f.push('R1');
  if (tool.can_execute_shell && !(tool.shell_allowlist || []).length) f.push('R2');
  if (tool.network_access && !(tool.allowed_hosts || []).length) f.push('R3');
  if (tool.fs_write && !(tool.allowed_paths || []).length) f.push('R4');
  if (!(tool.description || '').trim()) f.push('R5');
  if (['', '*', 'latest'].includes((tool.version || '').trim())) f.push('R6');
  const rate = tool.rate_limit_per_min;
  if (rate === null || rate === undefined || rate > 1000) f.push('R7');
  if (!(tool.owner || '').trim()) f.push('R8');
  const out = f.sort();
  return rules ? out.filter((r) => rules.includes(r)) : out;
}

// check_all_build
export function checkAll(tools, severity) {
  return tools.map((t) => {
    const flags = checkTool(t);
    return { name: t.name, flags, flag_count: flags.length, safe: !flags.length, severities: [...new Set(flags.map((x) => severity[x]))].sort() };
  });
}

// summarise_build
export function summariseManifest(recs, ruleIds, severity) {
  const per_rule = Object.fromEntries(ruleIds.map((r) => [r, 0]));
  const per_severity = { high: 0, medium: 0, low: 0 };
  let total = 0, unsafe = 0;
  for (const r of recs) {
    total += r.flag_count; if (!r.safe) unsafe++;
    for (const f of r.flags) { per_rule[f]++; per_severity[severity[f]]++; }
  }
  return { tools_total: recs.length, tools_unsafe: unsafe, tools_safe: recs.length - unsafe, total_flags: total, flags_per_rule: per_rule, flags_per_severity: per_severity };
}

// level-2-build/service_build.py run_probes_build with a CancelToken that fires after
// `cancelAfter` jobs (null = never). Sequential emulation of the token check: a worker
// checks the token before each job, a cancelled job counts as skipped.
export function simulatePool(endpoints, cancelAfter = null) {
  const out = [], order = [];
  let skipped = 0;
  endpoints.forEach((ep, i) => {
    if (cancelAfter !== null && i >= cancelAfter) { skipped++; order.push({ name: ep.name, state: 'skipped' }); return; }
    const rec = ep.probe_ok
      ? { name: ep.name, model: ep.model, healthy: true, latency_ms: ep.latency_ms, note: ep.probe_note, error_kind: null, error_chain: [] }
      : { name: ep.name, model: ep.model, healthy: false, latency_ms: ep.latency_ms, note: ep.probe_note, error_kind: ep.error_kind,
          error_chain: [`probe transport failed: ${ep.probe_note}`, `probe ${ep.name}`] };
    out.push(rec);
    order.push({ name: ep.name, state: rec.healthy ? 'ok' : 'error' });
  });
  out.sort((a, b) => (a.name < b.name ? -1 : 1));
  return { records: out, order, info: { probed: out.length, skipped, status: skipped ? 'cancelled' : 'completed' } };
}

// ServiceError.__str__: the chain read outermost first.
export const chainString = (chain) => [...chain].reverse().join(': caused by: ');

// level-3-deep/profile_deep.py make_workload_endpoints / make_workload_requests
export function makeWorkloadEndpoints(base, count) {
  return Array.from({ length: count }, (_, i) => {
    const s = base[i % base.length];
    return { name: `ep-${String(i).padStart(4, '0')}-${s.name}`, model: s.model, latency_ms: s.latency_ms + (i % 7), probe_ok: s.probe_ok, probe_note: s.probe_note, error_kind: s.error_kind };
  });
}
export const makeWorkloadRequests = (models, count) => Array.from({ length: count }, (_, i) => models[i % models.length]);

export const median = (xs) => { const s = [...xs].sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

// profile_deep.py time_median: 1 warmup, then `reps` timed repetitions, median reported.
export function timeMedian(fn, reps = 5, now = () => performance.now()) {
  fn();
  const times = [];
  for (let i = 0; i < reps; i++) { const t0 = now(); fn(); times.push(now() - t0); }
  return { times, median: median(times) };
}

// Ratio statistics from recorded batch times: median ratio and the paired per-repetition range.
export function ratioStats(base, idx) {
  const paired = base.map((b, i) => b / idx[i]);
  return { medianRatio: median(base) / median(idx), pairedMin: Math.min(...paired), pairedMax: Math.max(...paired), paired };
}

// Parses cProfile print_stats rows from results_deep.json profile_top.
export function parseProfile(lines) {
  const total = +(lines.join('\n').match(/in ([\d.]+) seconds/) || [])[1];
  const rows = [];
  for (const l of lines) {
    const m = l.match(/^\s*(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(.+)$/);
    if (m) rows.push({ ncalls: +m[1], tottime: +m[2], cumtime: +m[4], fn: m[6].trim() });
  }
  return { total, rows };
}

// Lifecycle lines "- Stage: STATUS date" and the verdict level from README.md.
export const parseLifecycle = (md) => [...md.matchAll(/^- (\w+): ([A-Z]+)(?: (\d{4}-\d{2}-\d{2}))?$/gm)].map((m) => m.slice(1));
export const parseVerdict = (md) => (md.match(/^\*\*Verdict\.\*\* ([^.]+)/m) || [])[1];

// Numbered list items ("1. ...") from a Markdown block, joined across wrapped lines.
export function parseNumbered(md) {
  return md.split(/\n(?=\d+\. )/).filter((b) => /^\d+\. /.test(b)).map((b) => b.replace(/^\d+\.\s+/, '').replace(/\s+/g, ' ').trim());
}

// Text of one "## heading" section of a Markdown file.
export function section(md, heading) {
  const i = md.indexOf(`## ${heading}`);
  if (i < 0) return '';
  const rest = md.slice(i + heading.length + 3);
  const j = rest.search(/\n## /);
  return (j < 0 ? rest : rest.slice(0, j)).trim();
}

// Go string slice literal `var StudySteps = []string{ "..." }` from profile.go.
export function parseGoSteps(src) {
  const body = src.slice(src.indexOf('StudySteps = []string{'), src.indexOf('}', src.indexOf('StudySteps = []string{')));
  return [...body.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((m) => m[1].replace(/^\d+\.\s*/, ''));
}

// Counts unittest methods in test sources.
export const countTests = (texts) => texts.reduce((n, t) => n + (t.match(/^\s*def test_/gm) || []).length, 0);

// Deep equality that ignores object key order (the results files are written with sorted keys).
const canon = (v) => (Array.isArray(v) ? v.map(canon) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canon(v[k])])) : v);
export const sameData = (a, b) => JSON.stringify(canon(a)) === JSON.stringify(canon(b));
