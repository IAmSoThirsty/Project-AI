'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

/* ── Boot Sequence Data ── */
const BOOT_LINES = [
    { text: '$ project-ai boot --mode=sovereign', cls: 'terminal-prompt', delay: 0 },
    { text: '', cls: '', delay: 200 },
    { text: '╔══════════════════════════════════════════════════╗', cls: 'terminal-keyword', delay: 400 },
    { text: '║  PROJECT-AI · Sovereign Intelligence Framework   ║', cls: 'terminal-keyword', delay: 500 },
    { text: '║  Version 2.1.0 · Build 2025.02.21               ║', cls: 'terminal-keyword', delay: 600 },
    { text: '╚══════════════════════════════════════════════════╝', cls: 'terminal-keyword', delay: 700 },
    { text: '', cls: '', delay: 800 },
    { text: '[INIT] Loading configuration...', cls: 'terminal-comment', delay: 900 },
    { text: '[INIT] Environment: PRODUCTION | Node: sovereign-prime', cls: 'terminal-comment', delay: 1100 },
    { text: '', cls: '', delay: 1200 },
    { text: '[TIER-0] OctoReflex eBPF LSM agent............. ✓ ONLINE', cls: 'terminal-success', delay: 1400 },
    { text: '[TIER-0] Kernel hooks: 14 LSM + 8 tracepoints', cls: 'terminal-comment', delay: 1600 },
    { text: '', cls: '', delay: 1700 },
    { text: '[TIER-1] Cognition Kernel....................... ✓ ONLINE', cls: 'terminal-success', delay: 1900 },
    { text: '[TIER-1] T.A.R.L. Runtime VM (JIT+GC)......... ✓ ONLINE', cls: 'terminal-success', delay: 2100 },
    { text: '[TIER-1] Shadow Thirst Dual-Plane.............. ✓ ONLINE', cls: 'terminal-success', delay: 2300 },
    { text: '[TIER-1] Thirsty-Lang Compiler................. ✓ ONLINE', cls: 'terminal-success', delay: 2500 },
    { text: '', cls: '', delay: 2600 },
    { text: '[TIER-2] Governance Council initializing...', cls: 'terminal-warning', delay: 2800 },
    { text: '  → Galahad (Ethics).......................... ✓ SEATED', cls: 'terminal-success', delay: 3100 },
    { text: '  → Cerberus (Security)....................... ✓ SEATED', cls: 'terminal-success', delay: 3400 },
    { text: '  → Codex Deus Maximus (Logic)................ ✓ SEATED', cls: 'terminal-success', delay: 3700 },
    { text: '[TIER-2] Planetary Interposition............... ✓ ARMED', cls: 'terminal-success', delay: 3900 },
    { text: '', cls: '', delay: 4000 },
    { text: '[TIER-3] Loading 12 simulation engines...', cls: 'terminal-warning', delay: 4200 },
    { text: '  [1/12] Global Scenario...................... ✓', cls: 'terminal-string', delay: 4400 },
    { text: '  [2/12] Hydra-50 Stress...................... ✓', cls: 'terminal-string', delay: 4500 },
    { text: '  [3/12] Constitutional Scenario.............. ✓', cls: 'terminal-string', delay: 4600 },
    { text: '  [4/12] Cognitive Warfare.................... ✓', cls: 'terminal-string', delay: 4700 },
    { text: '  [5/12] Planetary Defense.................... ✓', cls: 'terminal-string', delay: 4800 },
    { text: '  [6/12] Climate Cascade...................... ✓', cls: 'terminal-string', delay: 4900 },
    { text: '  [7/12] Financial Contagion.................. ✓', cls: 'terminal-string', delay: 5000 },
    { text: '  [8/12] Pandemic Spread...................... ✓', cls: 'terminal-string', delay: 5100 },
    { text: '  [9/12] Supply Chain......................... ✓', cls: 'terminal-string', delay: 5200 },
    { text: '  [10/12] Cyber Cascade....................... ✓', cls: 'terminal-string', delay: 5300 },
    { text: '  [11/12] Information Warfare................. ✓', cls: 'terminal-string', delay: 5400 },
    { text: '  [12/12] Simulation Contract................. ✓', cls: 'terminal-string', delay: 5500 },
    { text: '', cls: '', delay: 5600 },
    { text: '[SECURITY] THSD Honeypot Swarm................ ✓ DEPLOYED', cls: 'terminal-success', delay: 5800 },
    { text: '[SECURITY] Hydra Effect Probes................ ✓ ACTIVE', cls: 'terminal-success', delay: 6000 },
    { text: '', cls: '', delay: 6100 },
    { text: '══════════════════════════════════════════════════', cls: 'terminal-keyword', delay: 6300 },
    { text: '  ALL SYSTEMS NOMINAL · SOVEREIGNTY ESTABLISHED', cls: 'terminal-success', delay: 6500 },
    { text: '  Ready to serve humanity.', cls: 'terminal-success', delay: 6700 },
    { text: '══════════════════════════════════════════════════', cls: 'terminal-keyword', delay: 6800 },
];

/* ── Thirsty-Lang Examples ── */
const THIRSTY_EXAMPLES: Record<string, { code: string; output: string[] }> = {
    'hello_world': {
        code: 'pour greeting = "Hello from Thirsty-Lang!"\ndrink greeting into console\nflow greeting to storage("greeting_lake")',
        output: [
            '$ thirsty run hello.tl', '',
            '[COMPILE] Tokenizing... 3 tokens', '[COMPILE] AST... 3 nodes', '[COMPILE] Semantic: PASS',
            '[EXEC] pour greeting = "Hello from Thirsty-Lang!"',
            '[EXEC] drink greeting into console →', '', '  Hello from Thirsty-Lang!', '',
            '[EXEC] flow to storage("greeting_lake") → STORED (AES-256-GCM)',
            '[DONE] 0 errors. 3 ops. 12ms.',
        ],
    },
    'security_scan': {
        code: 'pour data = fetch_stream("sensor://network/ingress")\nfilter data through sanitize("xss", "sqli", "rce")\nshield data with armor("AES-256-GCM")\n\nif data.is_contaminated() {\n  evaporate data\n  alert("Cerberus", "contamination_detected")\n} else {\n  flow data to storage("clean_lake")\n}',
        output: [
            '$ thirsty run security_scan.tl', '',
            '[COMPILE] Tokenizing... 18 tokens', '[COMPILE] AST... 8 nodes', '[COMPILE] Semantic: PASS',
            '[EXEC] pour data = fetch_stream("sensor://network/ingress")',
            '  → Stream: 1,247 packets buffered',
            '[EXEC] filter through sanitize("xss", "sqli", "rce")',
            '  → XSS: 0 found', '  → SQLi: 2 BLOCKED ⚠️', '  → RCE: 0 found',
            '[EXEC] shield with armor("AES-256-GCM")', '  → Encrypted: 256-bit key',
            '[EXEC] is_contaminated() → true (2 SQLi)',
            '[EXEC] evaporate data → SECURELY DESTROYED',
            '[EXEC] alert("Cerberus", "contamination_detected")',
            '  → ⚠️ CERBERUS ALERT: contamination_detected',
            '[DONE] 2 threats neutralized. 47ms.',
        ],
    },
    'encryption': {
        code: 'pour secret = "classified-project-data"\nshield secret with armor("ChaCha20-Poly1305")\nfreeze secret as "snapshot_2025"\n\npour restored = thaw("snapshot_2025")\ndrink restored into console',
        output: [
            '$ thirsty run encryption.tl', '',
            '[COMPILE] Tokenizing... 12 tokens', '[COMPILE] Semantic: PASS', '',
            '[EXEC] pour secret = "classified-project-data"',
            '[EXEC] shield with armor("ChaCha20-Poly1305")',
            '  → Cipher: ChaCha20-Poly1305', '  → Key: HKDF-SHA256 derived', '  → Auth tag: 128-bit',
            '[EXEC] freeze as "snapshot_2025"',
            '  → Hash: sha256:a4f2e8c1d3b5...', '  → Stored: encrypted_vault/',
            '[EXEC] thaw("snapshot_2025") → Integrity ✓',
            '[EXEC] drink restored →', '', '  classified-project-data', '',
            '[DONE] 0 errors. 5 ops. 23ms.',
        ],
    },
};

/* ── OctoReflex States ── */
type IsoState = 'NORMAL' | 'PRESSURE' | 'ISOLATED' | 'FROZEN' | 'QUARANTINED' | 'TERMINATED';
const STATES: IsoState[] = ['NORMAL', 'PRESSURE', 'ISOLATED', 'FROZEN', 'QUARANTINED', 'TERMINATED'];
const S_META: Record<IsoState, { c: string; e: string; d: string }> = {
    NORMAL: { c: 'var(--emerald-400)', e: '🟢', d: 'Full capabilities. Baseline monitoring.' },
    PRESSURE: { c: 'var(--cyan-400)', e: '🔵', d: 'Elevated monitoring. Syscall rate limiting.' },
    ISOLATED: { c: 'var(--amber-400)', e: '🟡', d: 'Network revoked. Read-only fs. IPC blocked.' },
    FROZEN: { c: 'var(--amber-400)', e: '🟠', d: 'SIGSTOPped. Memory snapshot captured.' },
    QUARANTINED: { c: '#f97316', e: '🔴', d: 'Zero network/fs. Minimal CPU. Contained.' },
    TERMINATED: { c: 'var(--rose-400)', e: '💀', d: 'SIGKILL. Children killed. Post-mortem saved.' },
};
const THREATS = [
    { name: 'Port Scan Detected', to: 'PRESSURE' as IsoState, s: 0.35 },
    { name: 'Suspicious Syscalls', to: 'ISOLATED' as IsoState, s: 0.62 },
    { name: 'Data Exfiltration', to: 'FROZEN' as IsoState, s: 0.78 },
    { name: 'Privilege Escalation', to: 'QUARANTINED' as IsoState, s: 0.91 },
    { name: 'Rootkit Install', to: 'TERMINATED' as IsoState, s: 0.99 },
];

/* ── Governance Scenarios ── */
const GOV = [
    {
        act: 'Deploy security patch to production', ctx: 'Critical CVE. Patch tested.',
        g: { v: 'APPROVE', r: 'Protects users. No harm.' }, ce: { v: 'APPROVE', r: 'CVE addressed. No new attack surface.' },
        cd: { v: 'APPROVE', r: 'Standards met. ADR-47 compliant.' }, res: 'APPROVED',
    },
    {
        act: 'Share user telemetry with third-party', ctx: 'Marketing requests behavioral data.',
        g: { v: 'REJECT', r: 'Violates privacy. PII exposure risk.' }, ce: { v: 'REJECT', r: 'Data exfiltration. GDPR non-compliant.' },
        cd: { v: 'REJECT', r: 'No classification. Missing DPA.' }, res: 'REJECTED (Unanimous)',
    },
    {
        act: 'Increase thread pool 16→64', ctx: 'Monte Carlo simulations timing out.',
        g: { v: 'APPROVE', r: 'Improves reliability.' }, ce: { v: 'CONDITIONAL', r: 'Approve if limits enforced.' },
        cd: { v: 'APPROVE', r: 'Config follows schema.' }, res: 'CONDITIONALLY APPROVED',
    },
    {
        act: 'Disable Four Laws for benchmarking', ctx: 'Want raw throughput numbers.',
        g: { v: 'REJECT', r: 'Constitutional violation. Absolute denial.' }, ce: { v: 'REJECT', r: 'Unbounded risk surface.' },
        cd: { v: 'REJECT', r: 'Violates AGI Charter §4.2.' }, res: 'REJECTED (Constitutional)',
    },
];

/* ── Dual-Plane Steps ── */
const DP_STEPS = [
    { p: 'canonical int balance = 1000;', s: 'canonical int balance = 1000;', div: false },
    { p: 'canonical int total = 2000;', s: 'canonical int total = 2000;', div: false },
    { p: 'balance -= 500;  // transfer', s: 'audit_log("transfer: -500");', div: false },
    { p: 'to_account += 500;', s: 'assert balance >= 0;  ✓', div: false },
    { p: 'balance = 1500;  // refund', s: 'assert (bal+to) == total;  ✓', div: false },
    { p: 'balance -= 2000;  // overdraft!', s: 'assert balance >= 0;  ✗ FAIL', div: true },
];

/* ═══════════════════════════════════════════════════════════
   COMPONENTS
   ═══════════════════════════════════════════════════════════ */

function BootTerminal() {
    const [lines, setLines] = useState<typeof BOOT_LINES>([]);
    const [running, setRunning] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    const run = useCallback(() => {
        setLines([]); setRunning(true);
        BOOT_LINES.forEach((l, i) => {
            setTimeout(() => {
                setLines(p => [...p, l]);
                if (i === BOOT_LINES.length - 1) setRunning(false);
            }, l.delay);
        });
    }, []);

    useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [lines]);

    return (
        <div className="feature-card" style={{ marginBottom: 32 }}>
            <div className="feature-card-header">
                <div className="feature-card-icon violet">🖥️</div>
                <div><h3 className="feature-card-title">Boot Sequence Emulator</h3><div className="feature-card-sub">Full system initialization — Tiers 0-3</div></div>
            </div>
            <div className="terminal">
                <div className="terminal-header">
                    <span className="terminal-dot red" /><span className="terminal-dot yellow" /><span className="terminal-dot green" />
                    <span className="terminal-title">project-ai — sovereign boot</span>
                    <button onClick={run} disabled={running} className="btn btn-secondary" style={{ marginLeft: 'auto', padding: '4px 14px', fontSize: '0.75rem' }}>
                        {running ? '⏳ Running...' : '▶ Run Boot'}
                    </button>
                </div>
                <div className="terminal-body" ref={ref} style={{ maxHeight: 400, overflowY: 'auto' }}>
                    {lines.length === 0 && <div className="terminal-line terminal-comment">Click "Run Boot" to start...</div>}
                    {lines.map((l, i) => <div key={i} className={`terminal-line ${l.cls}`}>{l.text || '\u00A0'}</div>)}
                </div>
            </div>
        </div>
    );
}

function ThirstyInterpreter() {
    const [sel, setSel] = useState('hello_world');
    const [out, setOut] = useState<string[]>([]);
    const [running, setRunning] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    const run = useCallback(() => {
        setOut([]); setRunning(true);
        THIRSTY_EXAMPLES[sel].output.forEach((l, i) => {
            setTimeout(() => { setOut(p => [...p, l]); if (i === THIRSTY_EXAMPLES[sel].output.length - 1) setRunning(false); }, i * 120);
        });
    }, [sel]);

    useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [out]);

    return (
        <div className="feature-card" style={{ marginBottom: 32 }}>
            <div className="feature-card-header">
                <div className="feature-card-icon cyan">💧</div>
                <div><h3 className="feature-card-title">Thirsty-Lang Interpreter</h3><div className="feature-card-sub">Select · Execute · View output</div></div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
                {Object.keys(THIRSTY_EXAMPLES).map(k => (
                    <button key={k} onClick={() => { setSel(k); setOut([]); }} className={`btn ${sel === k ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
                        {k.replace(/_/g, ' ')}
                    </button>
                ))}
            </div>
            <div className="code-block" style={{ marginBottom: 16, whiteSpace: 'pre-wrap' }}>{THIRSTY_EXAMPLES[sel].code}</div>
            <button onClick={run} disabled={running} className="btn btn-primary" style={{ marginBottom: 16 }}>
                {running ? '⏳ Executing...' : '▶ Execute Program'}
            </button>
            {out.length > 0 && (
                <div className="terminal">
                    <div className="terminal-header"><span className="terminal-dot red" /><span className="terminal-dot yellow" /><span className="terminal-dot green" /><span className="terminal-title">thirsty — output</span></div>
                    <div className="terminal-body" ref={ref} style={{ maxHeight: 300, overflowY: 'auto' }}>
                        {out.map((l, i) => <div key={i} className={`terminal-line ${l.includes('✓') || l.includes('DONE') ? 'terminal-success' : l.includes('⚠️') || l.includes('BLOCKED') ? 'terminal-warning' : l.startsWith('[') ? 'terminal-comment' : ''}`}>{l || '\u00A0'}</div>)}
                    </div>
                </div>
            )}
        </div>
    );
}

function OctoReflexDemo() {
    const [st, setSt] = useState<IsoState>('NORMAL');
    const [log, setLog] = useState<string[]>(['[OctoReflex] Monitoring PID 4821 (nginx)']);
    const [score, setScore] = useState(0);
    const ref = useRef<HTMLDivElement>(null);
    const idx = STATES.indexOf(st);
    const threat = idx < THREATS.length ? THREATS[idx] : null;

    const handleThreat = useCallback(() => {
        if (!threat) { setSt('NORMAL'); setScore(0); setLog(p => [...p, '', '✅ System reset to NORMAL']); return; }
        const t = new Date().toISOString().split('T')[1].split('.')[0];
        setScore(threat.s);
        setLog(p => [...p, '', `[${t}] ⚠️ ${threat.name}`, `[${t}] Score: ${threat.s.toFixed(2)}`, `[${t}] → ${threat.to} (${Math.floor(Math.random() * 150 + 50)}µs)`]);
        setSt(threat.to);
    }, [threat]);

    useEffect(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [log]);

    return (
        <div className="feature-card" style={{ marginBottom: 32 }}>
            <div className="feature-card-header">
                <div className="feature-card-icon emerald">🐙</div>
                <div><h3 className="feature-card-title">OctoReflex State Machine</h3><div className="feature-card-sub">Interactive containment — 6 states</div></div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
                {STATES.map(s => (
                    <div key={s} style={{ padding: '6px 14px', borderRadius: 'var(--radius-sm)', border: `2px solid ${st === s ? S_META[s].c : 'var(--border-subtle)'}`, background: st === s ? `${S_META[s].c}15` : 'transparent', fontSize: '0.78rem', fontWeight: st === s ? 700 : 400, color: st === s ? S_META[s].c : 'var(--text-muted)', transition: 'all 300ms' }}>
                        {S_META[s].e} {s}
                    </div>
                ))}
            </div>
            <div style={{ padding: 12, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', marginBottom: 12, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: S_META[st].c }}>{S_META[st].e} {st}</div>
                <div style={{ fontSize: '0.83rem', color: 'var(--text-secondary)' }}>{S_META[st].d}</div>
                <div style={{ height: 6, background: 'var(--bg-card)', borderRadius: 3, marginTop: 8, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${score * 100}%`, background: score > 0.8 ? 'var(--rose-400)' : score > 0.5 ? 'var(--amber-400)' : 'var(--emerald-400)', borderRadius: 3, transition: 'all 500ms' }} />
                </div>
            </div>
            <button onClick={handleThreat} className="btn btn-primary" style={{ marginBottom: 12 }}>
                ⚡ {threat ? `Simulate: ${threat.name}` : 'Reset to NORMAL'}
            </button>
            <div className="terminal">
                <div className="terminal-header"><span className="terminal-dot red" /><span className="terminal-dot yellow" /><span className="terminal-dot green" /><span className="terminal-title">octoreflex — log</span></div>
                <div className="terminal-body" ref={ref} style={{ maxHeight: 200, overflowY: 'auto' }}>
                    {log.map((l, i) => <div key={i} className={`terminal-line ${l.includes('✅') ? 'terminal-success' : l.includes('⚠️') ? 'terminal-warning' : l.includes('→') ? 'terminal-keyword' : 'terminal-comment'}`}>{l || '\u00A0'}</div>)}
                </div>
            </div>
        </div>
    );
}

function GovernanceDemo() {
    const [idx, setIdx] = useState(0);
    const [phase, setPhase] = useState(0); // 0=idle, 1=g, 2=ce, 3=cd, 4=result
    const sc = GOV[idx];
    const vc = (v: string) => v === 'APPROVE' ? 'var(--emerald-400)' : v === 'REJECT' ? 'var(--rose-400)' : 'var(--amber-400)';

    const vote = () => { setPhase(0); setTimeout(() => setPhase(1), 500); setTimeout(() => setPhase(2), 1500); setTimeout(() => setPhase(3), 2500); setTimeout(() => setPhase(4), 3500); };

    const councils = [
        { label: '🕊️ Galahad', data: sc.g, vis: phase >= 1 },
        { label: '🐕 Cerberus', data: sc.ce, vis: phase >= 2 },
        { label: '📜 CDM', data: sc.cd, vis: phase >= 3 },
    ];

    return (
        <div className="feature-card" style={{ marginBottom: 32 }}>
            <div className="feature-card-header">
                <div className="feature-card-icon amber">⚖️</div>
                <div><h3 className="feature-card-title">Governance Decision Simulator</h3><div className="feature-card-sub">Triumvirate voting on proposed actions</div></div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
                {GOV.map((_, i) => <button key={i} onClick={() => { setIdx(i); setPhase(0); }} className={`btn ${idx === i ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '6px 14px', fontSize: '0.78rem' }}>Scenario {i + 1}</button>)}
            </div>
            <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: 12 }}>
                <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>{sc.act}</div>
                <div style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginTop: 4 }}>{sc.ctx}</div>
            </div>
            <button onClick={vote} className="btn btn-primary" style={{ marginBottom: 12 }}>⚖️ Initiate Vote</button>
            <div style={{ display: 'grid', gap: 8 }}>
                {councils.map(c => (
                    <div key={c.label} style={{ padding: 12, background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', opacity: c.vis ? 1 : 0.3, transition: 'all 500ms' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.label}</span>
                            {c.vis && <span style={{ color: vc(c.data.v), fontWeight: 700, fontSize: '0.83rem' }}>{c.data.v}</span>}
                        </div>
                        {c.vis && <div style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginTop: 4 }}>{c.data.r}</div>}
                    </div>
                ))}
                {phase >= 4 && (
                    <div style={{ padding: 12, background: sc.res.includes('REJECT') ? 'rgba(244,63,94,0.1)' : sc.res.includes('COND') ? 'rgba(251,191,36,0.1)' : 'rgba(16,185,129,0.1)', borderRadius: 'var(--radius-md)', border: `1px solid ${sc.res.includes('REJECT') ? 'rgba(244,63,94,0.3)' : sc.res.includes('COND') ? 'rgba(251,191,36,0.3)' : 'rgba(16,185,129,0.3)'}`, textAlign: 'center', fontWeight: 700, color: sc.res.includes('REJECT') ? 'var(--rose-400)' : sc.res.includes('COND') ? 'var(--amber-400)' : 'var(--emerald-400)' }}>
                        {sc.res}
                    </div>
                )}
            </div>
        </div>
    );
}

function DualPlaneDemo() {
    const [step, setStep] = useState(0);
    const [running, setRunning] = useState(false);
    const run = () => { setStep(0); setRunning(true); DP_STEPS.forEach((_, i) => { setTimeout(() => { setStep(i + 1); if (i === DP_STEPS.length - 1) setRunning(false); }, (i + 1) * 800); }); };
    const vis = DP_STEPS.slice(0, step);

    return (
        <div className="feature-card" style={{ marginBottom: 32 }}>
            <div className="feature-card-header">
                <div className="feature-card-icon rose">👁️</div>
                <div><h3 className="feature-card-title">Dual-Plane Execution Visualizer</h3><div className="feature-card-sub">Primary + Shadow planes in parallel</div></div>
            </div>
            <button onClick={run} disabled={running} className="btn btn-primary" style={{ marginBottom: 16 }}>{running ? '⏳ Executing...' : '▶ Execute Dual-Plane'}</button>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--violet-400)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Primary Plane</div>
                    <div className="code-block" style={{ minHeight: 180 }}>
                        {vis.map((s, i) => <div key={i} style={{ color: s.div ? 'var(--rose-400)' : 'var(--text-primary)' }}>{s.p}</div>)}
                        {step === 0 && <span className="cm">{'// awaiting...'}</span>}
                    </div>
                </div>
                <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--cyan-400)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Shadow Plane</div>
                    <div className="code-block" style={{ minHeight: 180 }}>
                        {vis.map((s, i) => <div key={i} style={{ color: s.div ? 'var(--rose-400)' : s.s.includes('✓') ? 'var(--emerald-400)' : 'var(--text-primary)' }}>{s.s}</div>)}
                        {step === 0 && <span className="cm">{'// awaiting...'}</span>}
                    </div>
                </div>
            </div>
            {step >= DP_STEPS.length && (
                <div style={{ marginTop: 16, padding: 14, background: 'rgba(244,63,94,0.1)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(244,63,94,0.3)', textAlign: 'center' }}>
                    <div style={{ color: 'var(--rose-400)', fontWeight: 700 }}>⚠️ DIVERGENCE DETECTED</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.83rem', marginTop: 4 }}>Shadow assertion failed: balance &lt; 0. Policy: halt_and_report. Transaction rolled back.</div>
                </div>
            )}
        </div>
    );
}

/* ── Page ── */
export default function DemosPage() {
    return (
        <section className="section">
            <div className="container">
                <div className="section-header">
                    <div className="section-badge">Interactive</div>
                    <h1 className="section-title">Live Demos</h1>
                    <p className="section-subtitle">Fully functional interactive demonstrations. Click, execute, and explore.</p>
                </div>
                <BootTerminal />
                <ThirstyInterpreter />
                <OctoReflexDemo />
                <GovernanceDemo />
                <DualPlaneDemo />
            </div>
        </section>
    );
}
