import { useMemo, useState, useEffect, useCallback, useId } from 'react';
import learn from '../../level-1-learn/results_learn.json';
import build from '../../level-2-build/results_build.json';
import deep from '../../level-3-deep/results_deep.json';
import fx from '../../level-2-build/fixtures_build.json';
import learnMd from '../../level-1-learn/README.md?raw';
import buildMd from '../../level-2-build/README.md?raw';
import deepMd from '../../level-3-deep/README.md?raw';
import roadmapMd from '../../ROADMAP.md?raw';
import profileGo from '../../level-3-deep/go/internal/profile/profile.go?raw';
import * as L from './lab.js';

const REPO = 'https://github.com/JesunAhmadUshno/systems-languages-lab';
const blob = (p) => `${REPO}/blob/main/${p}`;
const fmt = (n) => Math.round(n).toLocaleString('en-US');
const testSources = import.meta.glob('../../tests/test_*.py', { query: '?raw', import: 'default', eager: true });
const sources = import.meta.glob('../../level-*/{go,rust}/**/*', { query: '?raw', import: 'default', eager: true });
const TEST_COUNT = L.countTests(Object.values(testSources));
const PROFILE = L.parseProfile(deep.profile_top);
const RB = PROFILE.rows.find((r) => r.fn.includes('(route_build)'));
const SHARE = (RB.cumtime / PROFILE.total) * 100;
const TB = deep.timing.baseline, TI = deep.timing.indexed;
const RATIO = L.ratioStats(TB.times_s, TI.times_s);
const QUIET = deepMd.match(/quieter run measured baseline\s+([\d.]+) s and indexed ([\d.]+) s/);
const RECORDED = deepMd.match(/## Results \(measured ([^,]+), ([^,]+), (Python [\d.]+)/);
const D = deep.deterministic;

const SECTIONS = [['top', 'Overview', '◎'], ['routing', 'Routing', '⇢'], ['manifest', 'Manifests', '✓'], ['cancel', 'Cancel', '⏹'], ['profile', 'Profile', '▤'], ['race', 'Race', '⚡'], ['sources', 'Go & Rust', '{}'], ['grades', 'Grades', '★'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Systems Languages Lab</a>
      <a className="m" href={blob('SPEC.md')}>Spec</a>
      <a className="m" href={blob('level-3-deep/README.md')}>Deep study</a>
      <a className="m" href={blob('docs/research-review.md')}>Research review</a>
      <span className="spacer" />
      <span className="status"><i /> Python reference executed</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

function useNarrow() {
  const q = '(max-width: 760px)';
  const [narrow, setNarrow] = useState(() => typeof window !== 'undefined' && window.matchMedia(q).matches);
  useEffect(() => { const m = window.matchMedia(q), f = () => setNarrow(m.matches); m.addEventListener('change', f); return () => m.removeEventListener('change', f); }, []);
  return narrow;
}

function Range({ label, value, min, max, step, onChange, show }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

export default function App() {
  useReveal();
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Routing />
      <Manifest />
      <Cancel />
      <Profile />
      <Race />
      <Sources />
      <Grades />
      <Reproduce />
      <Dock />
      <footer>
        Code: Apache-2.0. Every number on this page is read at build time from the level results JSON, READMEs and sources in the repo, or computed live in your browser by JS ports of the Python reference. Go and Rust sources are UNEXECUTED.
      </footer>
    </div>
  );
}

function Hero() {
  return (
    <header className="card hero window" id="top" data-title="p21.lab">
      <div className="head">
        <p className="eyebrow">Go and Rust ideas · executed as a Python reference</p>
        <span className="pill warn">● Go and Rust UNEXECUTED</span>
      </div>
      <h1>Profiling a routing service found <em>one function</em> eating {SHARE.toFixed(1)}% of the time.</h1>
      <p className="sub">
        In the recorded Python run, <span className="mono">route_build</span> filtered and sorted every endpoint on every request. A per-model index cut a {fmt(D.workload.requests)}-request batch
        from {TB.median_s} s to {TI.median_s} s (median of {TB.repetitions}) with identical routing. The Go and Rust ports of the same service and checker are written but have never been compiled.
        Below, JS ports of the Python code rerun every level in your browser and are checked against the recorded results at build time.
      </p>
      <div className="actions">
        <a className="btn primary" href="#race">Run the live race</a>
        <a className="btn ghost" href={blob('level-3-deep/results_deep.json')}>Read results_deep.json</a>
        <span className="hint">Reproduce with <code>python3 level-3-deep/run_deep.py</code></span>
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{SHARE.toFixed(1)}%</div><div className="cap">route_build share of profiled time ({RB.cumtime.toFixed(3)} of {PROFILE.total.toFixed(3)} s cumulative)</div></div>
        <div className="tile"><div className="num">{TB.median_s} → {TI.median_s} s</div><div className="cap">Median batch, baseline to indexed, {TB.repetitions} reps</div></div>
        <div className="tile"><div className="num">{fmt(D.indexed_routing.requests_routed)} / {fmt(D.workload.requests)}</div><div className="cap">Requests routed; records identical: {String(D.routing_records_identical)}</div></div>
        <div className="tile"><div className="num">{TEST_COUNT}</div><div className="cap">Python unit tests in tests/, plus a smoke test</div></div>
      </div>
      <p className="banner">
        <b>Plain scope.</b> Every executed level is Python stdlib on one shared VM. The Go and Rust sources are UNEXECUTED: no compiler, linter or test run has touched them.
        Endpoint probes and tool manifests are scripted fixtures, not live HTTP services or real MCP files.
      </p>
    </header>
  );
}

function freshRouting(res) {
  return { records: res.health_records.map((r) => ({ name: r.name, model: r.model, healthy: r.healthy, latency_ms: r.latency_ms })), models: res.routing_records.map((r) => r.model) };
}

function Routing() {
  const [level, setLevel] = useState('learn');
  const res = level === 'learn' ? learn : build;
  const [state, setState] = useState(() => ({ learn: freshRouting(learn), build: freshRouting(build) }));
  const [add, setAdd] = useState('chat');
  const { records, models } = state[level];
  const set = (fn) => setState((s) => ({ ...s, [level]: fn(s[level]) }));
  const recs = useMemo(() => L.runRouting(models, records), [models, records]);
  const sum = L.summariseRouting(recs);
  const matches = L.sameData(sum, res.routing);
  const modelNames = [...new Set(res.health_records.map((r) => r.model)), 'unknown'];
  const narrow = useNarrow();
  const W = narrow ? 340 : 460, rowH = 26, H = records.length * rowH + 24, l = 120, max = Math.max(4, ...Object.values(sum.per_endpoint));
  return (
    <section id="routing" className="card window reveal" data-title="healthsvc.go — python reference">
      <div className="head">
        <div>
          <p className="eyebrow">Live playground · health and routing</p>
          <h2>Healthy endpoints only, lowest latency wins, name breaks ties.</h2>
          <p className="sub">
            The endpoint table is the recorded health record set from <a href={blob(`level-${level === 'learn' ? '1-learn/results_learn' : '2-build/results_build'}.json`)}>{level === 'learn' ? 'results_learn' : 'results_build'}.json</a>.
            Flip an endpoint's health, change its scripted latency, or add requests, and a JS port of <span className="mono">route_build</span> reroutes every request.
            On load it reproduces the recorded run: {res.routing.requests_routed} of {res.routing.requests_total} routed.
          </p>
        </div>
        <div className="seg" role="group" aria-label="Level">
          {[['learn', 'Learn'], ['build', 'Build']].map(([k, t]) => <button key={k} aria-pressed={level === k} onClick={() => setLevel(k)}>{t}</button>)}
        </div>
      </div>
      <div className="grid2">
        <div className="scroll-x">
          <table>
            <thead><tr><th>Endpoint</th><th>Model</th><th>Healthy</th><th>Latency (ms)</th></tr></thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={r.name}>
                  <td className="mono">{r.name}</td><td>{r.model}</td>
                  <td><input type="checkbox" checked={r.healthy} aria-label={`${r.name} healthy`} onChange={(e) => set((s) => ({ ...s, records: s.records.map((x, j) => (j === i ? { ...x, healthy: e.target.checked } : x)) }))} /></td>
                  <td><input className="num-in" type="number" min="0" max="999" value={r.latency_ms} aria-label={`${r.name} latency in ms`} onChange={(e) => set((s) => ({ ...s, records: s.records.map((x, j) => (j === i ? { ...x, latency_ms: Math.max(0, +e.target.value || 0) } : x)) }))} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <div className="head" style={{ marginBottom: 8 }}>
            <h3>{sum.requests_routed} of {sum.requests_total} requests routed</h3>
            <span className={`pill ${matches ? 'good' : 'info'}`}>{matches ? '✓ matches recorded run' : 'edited'}</span>
          </div>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Requests routed per endpoint">
            {records.map((r, i) => {
              const n = sum.per_endpoint[r.name] || 0, y = i * rowH + 4;
              return (
                <g key={r.name}>
                  <text x={l - 8} y={y + 14} textAnchor="end">{r.name}</text>
                  <rect x={l} y={y + 3} width={W - l - 30} height={14} rx="4" fill="var(--primary-pale)" />
                  <rect x={l} y={y + 3} width={((W - l - 30) * n) / max} height={14} rx="4" fill={r.healthy ? 'var(--primary)' : 'var(--bad)'} />
                  <text x={l + ((W - l - 30) * n) / max + 6} y={y + 14} style={{ fill: 'var(--text)' }}>{n}</text>
                </g>
              );
            })}
            <text x={W - 30} y={H - 2} textAnchor="end">requests per endpoint, unhealthy in red</text>
          </svg>
          <div className="chips" aria-live="polite">
            {recs.map((r, i) => (
              <button key={i} className={`chip ${r.routed ? '' : 'miss'}`} aria-label={`Remove request ${r.request}`} title="Remove this request" onClick={() => set((s) => ({ ...s, models: s.models.filter((_, j) => j !== i) }))}>
                #{r.request} {r.model} → {r.routed_to ?? 'unrouted'}
              </button>
            ))}
          </div>
          <div className="actions" style={{ marginTop: 12 }}>
            <div className="field inline"><label htmlFor="addreq">Add request</label>
              <select id="addreq" value={add} onChange={(e) => setAdd(e.target.value)}>{modelNames.map((m) => <option key={m}>{m}</option>)}</select>
            </div>
            <button className="btn ghost" onClick={() => set((s) => ({ ...s, models: [...s.models, add] }))}>Add</button>
            <button className="btn ghost" onClick={() => setState((s) => ({ ...s, [level]: freshRouting(res) }))}>Reset to recorded</button>
          </div>
        </div>
      </div>
    </section>
  );
}

const MANIFEST_FIELDS = [
  ['description', 'Description', 'text'], ['permissions', 'Permissions', 'list'], ['shell_allowlist', 'Shell allowlist', 'list'],
  ['allowed_hosts', 'Allowed hosts', 'list'], ['allowed_paths', 'Allowed paths', 'list'], ['version', 'Version', 'text'], ['owner', 'Owner', 'text'],
];
const FLAGS = [['can_execute_shell', 'Can execute shell'], ['network_access', 'Network access'], ['fs_write', 'Writes files']];
const RULE_NAMES = { R1: 'wildcard permission', R2: 'shell unscoped', R3: 'network unscoped', R4: 'fs write unscoped', R5: 'missing description', R6: 'unpinned version', R7: 'excessive rate', R8: 'missing owner' };
const SEV_COLOR = { high: 'bad', medium: 'warn', low: 'info' };

function Manifest() {
  const [tools, setTools] = useState(() => structuredClone(fx.tools_build));
  const [sel, setSel] = useState(1);
  const t = tools[sel];
  const edit = (k, v) => setTools((ts) => ts.map((x, i) => (i === sel ? { ...x, [k]: v } : x)));
  const recs = L.checkAll(tools, fx.severity);
  const sum = L.summariseManifest(recs, fx.rule_ids_build, fx.severity);
  const matches = L.sameData(sum, build.manifest);
  const rec = recs[sel];
  const maxRule = 4;
  return (
    <section id="manifest" className="card window reveal" data-title="manifest_checker.rs — python reference">
      <div className="head">
        <div>
          <p className="eyebrow">Live checker · eight rules</p>
          <h2>Edit a tool manifest and watch the eight safety rules re-run.</h2>
          <p className="sub">
            The eight Build manifests come from <a href={blob('level-2-build/fixtures_build.json')}>fixtures_build.json</a>, exported from <span className="mono">TOOLS_BUILD</span> and guarded by a parity test.
            A JS port of <span className="mono">check_tool_build</span> applies R1 to R8 with their severities. Unedited, the set reproduces <a href={blob('level-2-build/results_build.json')}>results_build.json</a>: {build.manifest.tools_unsafe} of {build.manifest.tools_total} unsafe, {build.manifest.total_flags} flags.
          </p>
        </div>
        <span className={`pill ${matches ? 'good' : 'info'}`}>{matches ? '✓ matches results_build.json' : 'edited set'}</span>
      </div>
      <div className="toolpick" role="group" aria-label="Pick a tool manifest">
        {recs.map((r, i) => (
          <button key={r.name} aria-pressed={sel === i} onClick={() => setSel(i)} className={r.safe ? 'safe' : 'unsafe'}>
            <span className="mono">{r.name}</span><small>{r.safe ? 'safe' : `${r.flag_count} flag${r.flag_count > 1 ? 's' : ''}`}</small>
          </button>
        ))}
      </div>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div>
          <h3>Manifest: <span className="mono">{t.name}</span></h3>
          <div className="controls" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', marginTop: 12 }}>
            {MANIFEST_FIELDS.map(([k, label, kind]) => (
              <div className="field" key={k}><label htmlFor={`mf-${k}`}>{label}</label>
                <input id={`mf-${k}`} type="text" value={kind === 'list' ? t[k].join(', ') : t[k]} placeholder={kind === 'list' ? 'none' : 'empty'}
                  onChange={(e) => edit(k, kind === 'list' ? e.target.value.split(',').map((s) => s.trim()).filter(Boolean) : e.target.value)} />
              </div>
            ))}
            <div className="field"><label htmlFor="mf-rate">Rate limit per min</label>
              <input id="mf-rate" type="number" min="0" value={t.rate_limit_per_min ?? ''} placeholder="none set" onChange={(e) => edit('rate_limit_per_min', e.target.value === '' ? null : +e.target.value)} />
            </div>
          </div>
          <div className="checks">
            {FLAGS.map(([k, label]) => <label key={k}><input type="checkbox" checked={t[k]} onChange={(e) => edit(k, e.target.checked)} /> {label}</label>)}
          </div>
          <div className="actions" style={{ marginTop: 12 }}>
            <button className="btn ghost" onClick={() => setTools((ts) => ts.map((x, i) => (i === sel ? structuredClone(fx.tools_build[i]) : x)))}>Reset this tool</button>
            <button className="btn ghost" onClick={() => setTools(structuredClone(fx.tools_build))}>Reset all</button>
          </div>
        </div>
        <div>
          <h3>{rec.safe ? 'No rule broken: safe' : `${rec.flag_count} rule${rec.flag_count > 1 ? 's' : ''} broken: unsafe`}</h3>
          <ul className="flaglist" aria-live="polite">
            {rec.flags.length ? rec.flags.map((f) => <li key={f}><span className={`pill ${SEV_COLOR[fx.severity[f]]}`}>{fx.severity[f]}</span><b className="mono">{f}</b> {RULE_NAMES[f]}</li>)
              : <li><span className="pill good">clear</span> All eight rules pass.</li>}
          </ul>
          <h3 style={{ marginTop: 18 }}>Flags per rule, all eight tools</h3>
          <div className="bars" style={{ marginTop: 10 }}>
            {fx.rule_ids_build.map((r) => (
              <div className="bar-row" key={r}>
                <div className="lab"><span><b className="mono">{r}</b> {RULE_NAMES[r]} · {fx.severity[r]}</span><b>{sum.flags_per_rule[r]}</b></div>
                <div className="track"><div className="fill" style={{ width: `${Math.min(100, (sum.flags_per_rule[r] / maxRule) * 100)}%`, background: `var(--${SEV_COLOR[fx.severity[r]] === 'info' ? 'primary' : SEV_COLOR[fx.severity[r]]})` }} />
                  <div className="ref" style={{ left: `${(build.manifest.flags_per_rule[r] / maxRule) * 100}%` }} title={`Recorded: ${build.manifest.flags_per_rule[r]}`} /></div>
              </div>
            ))}
          </div>
          <div className="sevrow">
            {['high', 'medium', 'low'].map((s) => (
              <div className="tile" key={s}><div className="num">{sum.flags_per_severity[s]}</div><div className="cap">{s} severity (recorded {build.manifest.flags_per_severity[s]})</div></div>
            ))}
          </div>
          <p className="hint">Black ticks mark the recorded per-rule counts. Scale 0 to {maxRule}.</p>
        </div>
      </div>
    </section>
  );
}

function Cancel() {
  const n = fx.endpoints_build.length;
  const [k, setK] = useState(n);
  const sim = L.simulatePool(fx.endpoints_build, k >= n ? null : k);
  const recordedChains = build.health_records.filter((r) => r.error_chain.length);
  const isRec = k === 0 || k >= n;
  const ref = k === 0 ? build.cancellation : build.pool;
  return (
    <section id="cancel" className="card window reveal" data-title="pool.cancel">
      <p className="eyebrow">Simulation · cancellable worker pool</p>
      <h2>Cancel the pool mid-run and every remaining job is skipped, not lost.</h2>
      <p className="sub">
        The Build pool checks a shared cancel token before each job, the Python analogue of Go's <span className="mono">context.Context</span>. This sequential emulation fires the token after N jobs over the {n} Build endpoints in registry order.
        The two recorded runs in results_build.json are the ends of the slider: pre-cancelled ({build.cancellation.probed} probed, {build.cancellation.skipped} skipped) and never cancelled ({build.pool.probed} probed).
      </p>
      <div className="controls" style={{ marginTop: 16 }}>
        <Range label="Cancel after N jobs" value={k} min={0} max={n} step={1} onChange={setK} show={k >= n ? 'never' : k} />
      </div>
      <div className="tiles" style={{ marginTop: 0 }}>
        <div className="tile"><div className="num">{sim.info.probed}</div><div className="cap">probed</div></div>
        <div className="tile"><div className="num">{sim.info.skipped}</div><div className="cap">skipped by cancellation</div></div>
        <div className="tile"><div className="num">{sim.info.status}</div><div className="cap">pool status</div></div>
        <div className="tile"><div className="num">{sim.records.filter((r) => r.healthy).length}</div><div className="cap">healthy among probed</div></div>
      </div>
      <div className="jobs" aria-label="Job outcomes in registry order" role="list">
        {sim.order.map((j, i) => <div role="listitem" key={j.name} className={`job ${j.state}`}><small>{i + 1}</small><span className="mono">{j.name}</span><em>{j.state === 'ok' ? 'healthy' : j.state === 'error' ? 'error' : 'skipped'}</em></div>)}
      </div>
      <p className="hint">{isRec ? (L.sameData(sim.info, ref) ? `✓ Matches the recorded ${k === 0 ? 'cancellation' : 'pool'} run in results_build.json.` : 'Does not match the recorded run.') : 'Intermediate N values are a simulation of the token logic; Python ran only the two recorded ends.'}</p>
      <h3 style={{ marginTop: 18 }}>Error chains, recorded in results_build.json</h3>
      <div className="scroll-x">
        <table>
          <thead><tr><th>Endpoint</th><th>Kind</th><th>Chain, outermost first</th><th>This run</th></tr></thead>
          <tbody>
            {recordedChains.map((r) => {
              const live = sim.records.find((x) => x.name === r.name);
              return <tr key={r.name}><td className="mono">{r.name}</td><td>{r.error_kind}</td><td className="mono">{L.chainString(r.error_chain)}</td>
                <td>{live ? <span className={`pill ${L.chainString(live.error_chain) === L.chainString(r.error_chain) ? 'good' : 'bad'}`}>reproduced</span> : <span className="pill info">skipped</span>}</td></tr>;
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Profile() {
  const [metric, setMetric] = useState('cumtime');
  const narrow = useNarrow();
  const rows = PROFILE.rows.filter((r) => r.cumtime > 0);
  const W = narrow ? 360 : 960, rowH = narrow ? 44 : 34, l = narrow ? 0 : 330, H = rows.length * rowH + 28, by = narrow ? 18 : 8;
  const x = (v) => l + (v / PROFILE.total) * (W - l - 70);
  const label = (fn) => fn.replace(/^.*service_build\.py:(\d+)\((.+)\)$/, '$2 · line $1');
  // strip plot on a log axis, 0.02 s to 4 s
  const SW = narrow ? 360 : 960, SH = 150, sl = narrow ? 64 : 90, lo = Math.log10(0.02), hi = Math.log10(4);
  const sx = (v) => sl + ((Math.log10(v) - lo) / (hi - lo)) * (SW - sl - 20);
  const arms = [['Baseline route_build', TB, 'var(--bad)'], ['Indexed router', TI, 'var(--good)']];
  return (
    <section id="profile" className="card window reveal" data-title="profile_deep.py">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded replay · {RECORDED ? `${RECORDED[1]}, ${RECORDED[2]}, ${RECORDED[3]}` : 'results_deep.json'}</p>
          <h2>The profile points at the sort inside <em>route_build</em>.</h2>
          <p className="sub">
            cProfile rows parsed from <span className="mono">profile_top</span> in <a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>: {fmt(D.workload.requests)} requests over {D.workload.endpoints} endpoints, {PROFILE.total} s under the profiler.
            {' '}route_build is called {fmt(RB.ncalls)} times and holds {SHARE.toFixed(1)}% of cumulative time; list sort alone is {PROFILE.rows.find((r) => r.fn.includes('sort'))?.cumtime} s.
          </p>
        </div>
        <div className="seg" role="group" aria-label="Profile metric">
          {[['cumtime', 'Cumulative'], ['tottime', 'Own time']].map(([k, t]) => <button key={k} aria-pressed={metric === k} onClick={() => setMetric(k)}>{t}</button>)}
        </div>
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`cProfile ${metric} by function, recorded run`}>
        {rows.map((r, i) => (
          <g key={r.fn} transform={`translate(0 ${i * rowH})`}>
            <text x={narrow ? 0 : l - 10} y={narrow ? 12 : 20} textAnchor={narrow ? 'start' : 'end'} style={{ fill: 'var(--text)', fontSize: 12 }}>{label(r.fn)}</text>
            <rect x={l} y={by} width={W - l - 70} height={16} rx="4" fill="var(--primary-pale)" />
            <rect x={l} y={by} width={Math.max(1, x(r[metric]) - l)} height={16} rx="4" fill={r.fn.includes('(route_build)') ? 'var(--bad)' : 'var(--primary)'} />
            <text x={x(r[metric]) + 6} y={by + 12} style={{ fill: 'var(--text)' }}>{r[metric].toFixed(3)} s</text>
          </g>
        ))}
        <text x={l} y={H - 4}>{narrow ? `seconds of ${PROFILE.total} s under cProfile` : `seconds, of ${PROFILE.total} s total under cProfile · ncalls: ${rows.map((r) => fmt(r.ncalls)).join(' · ')}`}</text>
      </svg>
      <h3 style={{ marginTop: 22 }}>All {TB.repetitions} timed batches per arm (log scale), median marked</h3>
      <svg className="chart" viewBox={`0 0 ${SW} ${SH}`} role="img" aria-label="Recorded batch times per repetition for baseline and indexed routing">
        {(narrow ? [0.02, 0.1, 0.5, 2] : [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 4]).map((t) => <g key={t}><line className="axis" x1={sx(t)} x2={sx(t)} y1={10} y2={SH - 24} /><text x={sx(t)} y={SH - 8} textAnchor="middle">{t} s</text></g>)}
        {arms.map(([name, arm, c], i) => {
          const y = 36 + i * 52;
          return (
            <g key={name}>
              <text x={0} y={y + 4} style={{ fill: 'var(--text)', fontSize: 12 }}>{name.split(' ')[0]}</text>
              {arm.times_s.map((v, j) => <circle key={j} cx={sx(v)} cy={y} r="6" fill={c} opacity="0.75"><title>{`rep ${j + 1}: ${v} s`}</title></circle>)}
              <line x1={sx(arm.median_s)} x2={sx(arm.median_s)} y1={y - 14} y2={y + 14} stroke="var(--text)" strokeWidth="2.5" />
              <text x={sx(arm.median_s)} y={y - 18} textAnchor={sx(arm.median_s) > SW * 0.75 ? 'end' : 'middle'} style={{ fill: 'var(--text)' }}>median {arm.median_s} s</text>
            </g>
          );
        })}
      </svg>
      <div className="tiles sm">
        <div className="tile"><div className="num">{RATIO.medianRatio.toFixed(1)}×</div><div className="cap">Median ratio, computed from times_s</div></div>
        <div className="tile"><div className="num">{RATIO.pairedMin.toFixed(1)}–{RATIO.pairedMax.toFixed(1)}×</div><div className="cap">Range of the {TB.repetitions} paired per-rep ratios</div></div>
        <div className="tile"><div className="num">{Math.min(...TB.times_s).toFixed(2)}–{Math.max(...TB.times_s).toFixed(2)} s</div><div className="cap">Baseline spread, min to max</div></div>
        <div className="tile"><div className="num">{Math.min(...TI.times_s).toFixed(3)}–{Math.max(...TI.times_s).toFixed(3)} s</div><div className="cap">Indexed spread (includes one index build per batch)</div></div>
      </div>
      <p className="banner">
        <b>Shared-VM variance.</b> Five repetitions on a shared VM is a thin sample, so read the ratio as an order of magnitude, not a constant.
        {QUIET && <> A quieter study run recorded in the Deep README measured {QUIET[1]} s and {QUIET[2]} s, a {(QUIET[1] / QUIET[2]).toFixed(0)}× ratio.</>} No confidence interval is claimed.
      </p>
    </section>
  );
}

function Race() {
  const [endpoints, setEndpoints] = useState(D.workload.endpoints);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [sweep, setSweep] = useState(null);
  const run = useCallback(() => {
    setBusy(true);
    requestAnimationFrame(() => setTimeout(() => {
      const eps = L.makeWorkloadEndpoints(fx.endpoints_build, endpoints);
      const recs = L.simulatePool(eps, null).records;
      const reqs = L.makeWorkloadRequests(D.workload.models, D.workload.requests);
      const base = L.runRouting(reqs, recs);
      const idx = L.runRouting(reqs, recs, L.indexedRouter(recs));
      const tb = L.timeMedian(() => L.runRouting(reqs, recs), 5);
      const ti = L.timeMedian(() => L.runRouting(reqs, recs, L.indexedRouter(recs)), 5);
      const identical = JSON.stringify(base) === JSON.stringify(idx);
      setRes({ endpoints, tb, ti, identical, routed: L.summariseRouting(idx).requests_routed, total: reqs.length });
      setBusy(false);
    }, 0));
  }, [endpoints]);

  const runSweep = () => {
    const sizes = [50, 100, 200, 400, 800], reqs = L.makeWorkloadRequests(D.workload.models, 5000), out = [];
    setSweep({ points: [], running: true });
    const step = (i) => {
      if (i >= sizes.length) { setSweep({ points: out, running: false }); return; }
      const recs = L.simulatePool(L.makeWorkloadEndpoints(fx.endpoints_build, sizes[i]), null).records;
      out.push({ n: sizes[i], b: L.timeMedian(() => L.runRouting(reqs, recs), 3).median, x: L.timeMedian(() => L.runRouting(reqs, recs, L.indexedRouter(recs)), 3).median });
      setSweep({ points: [...out], running: true });
      setTimeout(() => step(i + 1), 30);
    };
    setTimeout(() => step(0), 30);
  };
  useEffect(() => { const t = setTimeout(() => { run(); setTimeout(runSweep, 600); }, 400); return () => clearTimeout(t); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const isRec = endpoints === D.workload.endpoints;
  const W = 460, H = 220, p = { l: 48, r: 12, t: 12, b: 26 };
  const pts = sweep?.points || [];
  const ymax = Math.max(1, ...pts.map((q) => q.b));
  const sx = (n) => p.l + ((Math.log2(n) - Math.log2(50)) / (Math.log2(800) - Math.log2(50))) * (W - p.l - p.r);
  const sy = (v) => p.t + (1 - v / ymax) * (H - p.t - p.b);
  return (
    <section id="race" className="card window reveal" data-title="bench.html — measured in your browser">
      <div className="head">
        <div>
          <p className="eyebrow">Live benchmark · your browser, this run</p>
          <h2>Rerun the bottleneck fix yourself: filter-and-sort against an index.</h2>
          <p className="sub">
            The same deterministic workload as <span className="mono">profile_deep.py</span>, generated in JS: endpoints cycling the {fx.endpoints_build.length} Build fixtures, {fmt(D.workload.requests)} requests cycling {D.workload.models.join(', ')}.
            Timing follows the study method (1 warmup, 5 repetitions, median, <span className="mono">performance.now</span>). These are JavaScript timings on your machine, not comparable to the recorded Python numbers and not Go or Rust performance.
          </p>
        </div>
        <span className="pill info">{busy ? 'running…' : res ? `${res.endpoints} endpoints` : 'starting…'}</span>
      </div>
      <div className="controls">
        <Range label="Endpoints in the registry" value={endpoints} min={50} max={800} step={50} onChange={setEndpoints} show={endpoints} />
      </div>
      <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
        <button className="btn primary" onClick={run} disabled={busy}>{busy ? 'Timing…' : 'Run race'}</button>
        <span className="hint">{isRec ? `At ${D.workload.endpoints} endpoints the routed count must match the recorded ${fmt(D.indexed_routing.requests_routed)}.` : 'Off the recorded size: no recorded reference exists.'}</span>
      </div>
      {res && (
        <div className="grid2">
          <div>
            <div className="tiles sm" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 0 }}>
              <div className="tile"><div className="num">{res.tb.median.toFixed(1)} ms</div><div className="cap">baseline median (filter and sort per request)</div></div>
              <div className="tile"><div className="num">{res.ti.median.toFixed(2)} ms</div><div className="cap">indexed median (includes index build)</div></div>
              <div className="tile"><div className="num">{(res.tb.median / Math.max(res.ti.median, 0.001)).toFixed(1)}×</div><div className="cap">browser ratio, this run</div></div>
              <div className="tile"><div className="num">{fmt(res.routed)} / {fmt(res.total)}</div><div className="cap">routed by both</div></div>
            </div>
            <p className="hint" style={{ marginTop: 12 }}>
              <span className={`pill ${res.identical ? 'good' : 'bad'}`}>{res.identical ? '✓ records identical' : '✗ records differ'}</span>{' '}
              {res.endpoints === D.workload.endpoints && <span className={`pill ${res.routed === D.indexed_routing.requests_routed ? 'good' : 'bad'}`}>{res.routed === D.indexed_routing.requests_routed ? '✓ routed count matches results_deep.json' : 'routed count differs'}</span>}
            </p>
            <p className="hint">Batch times (ms): baseline {res.tb.times.map((t) => t.toFixed(1)).join(', ')} · indexed {res.ti.times.map((t) => t.toFixed(2)).join(', ')}. Browser timers may be coarsened for privacy.</p>
          </div>
          <div>
            <div className="head" style={{ marginBottom: 6 }}>
              <h3>Scaling sweep, 50 to 800 endpoints (5,000 requests, 3 reps)</h3>
              <button className="btn ghost" onClick={runSweep} disabled={sweep?.running}>{sweep?.running ? 'Sweeping…' : 'Run sweep'}</button>
            </div>
            <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Browser-measured median batch time by registry size, baseline versus indexed">
              {[50, 100, 200, 400, 800].map((n) => <g key={n}><line className="axis" x1={sx(n)} x2={sx(n)} y1={p.t} y2={H - p.b} /><text x={sx(n)} y={H - 8} textAnchor="middle">{n}</text></g>)}
              <text x={p.l - 6} y={sy(ymax) + 4} textAnchor="end">{pts.length ? `${ymax.toFixed(0)} ms` : ''}</text>
              <text x={p.l - 6} y={sy(0) + 4} textAnchor="end">0</text>
              {pts.length > 0 && <>
                <polyline fill="none" stroke="var(--bad)" strokeWidth="2.5" points={pts.map((q) => `${sx(q.n)},${sy(q.b)}`).join(' ')} />
                <polyline fill="none" stroke="var(--good)" strokeWidth="2.5" points={pts.map((q) => `${sx(q.n)},${sy(q.x)}`).join(' ')} />
                {pts.map((q) => <g key={q.n}><circle cx={sx(q.n)} cy={sy(q.b)} r="4" fill="var(--bad)" /><circle cx={sx(q.n)} cy={sy(q.x)} r="4" fill="var(--good)" /></g>)}
              </>}
              {!pts.length && <text x={W / 2} y={H / 2} textAnchor="middle">Sweep pending: 5,000 requests per size, 3 reps</text>}
            </svg>
            <div className="legend"><span><i style={{ background: 'var(--bad)' }} />baseline, grows with registry size</span><span><i style={{ background: 'var(--good)' }} />indexed</span></div>
          </div>
        </div>
      )}
    </section>
  );
}

function Sources() {
  const files = Object.entries(sources).map(([p, src]) => {
    const rel = p.replace('../../', '');
    const [level, lang] = rel.split('/');
    return { rel, level, lang, lines: src.split('\n').length - (src.endsWith('\n') ? 1 : 0), labelled: /unexecuted|not compiled or run/i.test(src) };
  }).sort((a, b) => (a.rel < b.rel ? -1 : 1));
  const levels = [...new Set(files.map((f) => f.level))];
  const [lang, setLang] = useState('go');
  const steps = L.parseGoSteps(profileGo);
  const rust = L.section(deepMd, 'Rust traits and generics (UNEXECUTED) and the cost note').split('\n\n').map((s) => s.replace(/\s+/g, ' ').trim());
  return (
    <section id="sources" className="card window reveal" data-title="unexecuted/">
      <div className="head">
        <div>
          <p className="eyebrow">Design only · never compiled</p>
          <h2>The Go and Rust ports exist as source, <em>not</em> as evidence.</h2>
          <p className="sub">
            {files.length} files, {fmt(files.reduce((s, f) => s + f.lines, 0))} lines, read from the repo at build time. The build VM had no go, rustc or cargo, so none of these were compiled, linted or tested. Nothing on this page comes from them.
          </p>
        </div>
        <div className="seg" role="group" aria-label="Language">
          {[['go', 'Go'], ['rust', 'Rust']].map(([k, t]) => <button key={k} aria-pressed={lang === k} onClick={() => setLang(k)}>{t}</button>)}
        </div>
      </div>
      <div className="tree">
        {levels.map((lv) => (
          <div key={lv} className="tile">
            <h3 className="mono">{lv}/{lang}/</h3>
            <ul>
              {files.filter((f) => f.level === lv && f.lang === lang).map((f) => (
                <li key={f.rel}><a className="mono" href={blob(f.rel)}>{f.rel.split('/').slice(2).join('/')}</a><span>{f.lines} lines</span>{f.labelled ? <span className="pill warn">UNEXECUTED</span> : <span className="pill info">manifest</span>}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      {lang === 'go' ? (
        <>
          <h3 style={{ marginTop: 20 }}>Go pprof study plan (StudySteps in profile.go, UNEXECUTED, a plan and not a result)</h3>
          <ol className="steps" style={{ marginTop: 12 }}>{steps.map((s, i) => <li key={i}><span className="n">{i + 1}</span><div className="hint">{s}</div></li>)}</ol>
        </>
      ) : (
        <>
          <h3 style={{ marginTop: 20 }}>Rust Rule trait design: generic Checker against dyn CheckerSet (UNEXECUTED)</h3>
          {rust.map((para, i) => <p key={i} className="sub">{para}</p>)}
        </>
      )}
    </section>
  );
}

function Grades() {
  const levels = [['Learn', learnMd, 'level-1-learn/README.md'], ['Build', buildMd, 'level-2-build/README.md'], ['Deep', deepMd, 'level-3-deep/README.md']].map(([n, md, p]) => ({ n, p, ...L.parseGrade(md) }));
  const backlog = L.parseNumbered(roadmapMd);
  return (
    <section id="grades" className="card window reveal" data-title="GRADES.md">
      <p className="eyebrow">Self-assessment and gaps</p>
      <h2>Recorded grades, with every deduction itemized.</h2>
      <p className="sub">Parsed from each level README. The largest deductions are the same at every level: no Go or Rust ever ran.</p>
      <div className="grades">
        {levels.map((g) => (
          <div className="tile" key={g.n}>
            <div className="head" style={{ marginBottom: 4 }}><h3>{g.n}</h3><a className="hint" href={blob(g.p)}>README ↗</a></div>
            <div className="num">{fmt(g.grade)}<small> / {fmt(g.scale)}</small></div>
            <div className="track" style={{ margin: '8px 0 12px' }}><div className="fill" style={{ width: `${(g.grade / g.scale) * 100}%`, background: 'var(--primary)' }} /></div>
            <ul className="ded">{g.items.map((it, i) => <li key={i}><b>−{fmt(it.minus)}</b><span>{it.text}</span></li>)}</ul>
          </div>
        ))}
      </div>
      <h3 style={{ marginTop: 20 }}>v1.1 backlog (ROADMAP.md)</h3>
      <ol className="steps" style={{ marginTop: 12 }}>{backlog.map((b, i) => <li key={i}><span className="n">{i + 1}</span><div className="hint">{b}</div></li>)}</ol>
    </section>
  );
}

function Reproduce() {
  const docs = [
    ['level-1-learn/results_learn.json', 'results_learn.json', 'Learn: routing and checker counts'],
    ['level-2-build/results_build.json', 'results_build.json', 'Build: pool, errors, eight rules'],
    ['level-3-deep/results_deep.json', 'results_deep.json', 'Deep: profile and timing'],
    ['level-3-deep/DEEP-SPEC.md', 'Deep spec', 'Hypothesis written before the run'],
    ['docs/research-review.md', 'Research review', 'Rubric grade and open gaps'],
    ['ROADMAP.md', 'Roadmap', 'v1.1 toolchain port'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — zsh">
      <p className="eyebrow">Reproduce it</p>
      <h2>Python 3 stdlib only: clone, test, rerun.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Clone</b><div className="hint"><code>git clone {REPO}.git && cd systems-languages-lab</code></div></div></li>
        <li><span className="n">2</span><div><b>Run the {TEST_COUNT} unit tests and the smoke test</b><div className="hint"><code>python3 -m unittest discover -s tests && python3 tests/test_smoke.py</code></div></div></li>
        <li><span className="n">3</span><div><b>Rerun every level</b><div className="hint"><code>python3 level-1-learn/run_learn.py && python3 level-2-build/run_build.py && python3 level-3-deep/run_deep.py</code> (the Deep timing section changes per run; its deterministic section must not)</div></div></li>
        <li><span className="n">4</span><div><b>Rebuild this page</b><div className="hint"><code>cd site && npm ci && npm run build</code> runs the known-answer check against all three results files first.</div></div></li>
      </ol>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
      </div>
      <p className="hint" style={{ marginTop: 16 }}>Tagged releases: <a href={`${REPO}/releases`}>GitHub releases</a>.</p>
    </section>
  );
}
