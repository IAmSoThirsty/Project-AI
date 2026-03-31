'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

/* ═══════════════════════════════════════════════════════════
   Interactive Drag-and-Pull Timeline
   - Mouse drag to scroll horizontally
   - Touch support
   - Click events on timeline nodes
   ═══════════════════════════════════════════════════════════ */

interface TimelineEvent {
    date: string;
    title: string;
    desc: string;
    category: 'genesis' | 'security' | 'language' | 'engine' | 'governance' | 'infra';
    impact: 'critical' | 'major' | 'standard';
}

const EVENTS: TimelineEvent[] = [
    { date: 'Oct 2024', title: 'Genesis Event', desc: 'Project-AI repository initialized. Core vision established: sovereign AI with constitutional governance for planetary defense.', category: 'genesis', impact: 'critical' },
    { date: 'Oct 2024', title: 'Cognition Kernel v1', desc: 'Central decision-making core created. Multi-agent orchestration framework with action-response pipeline.', category: 'infra', impact: 'critical' },
    { date: 'Nov 2024', title: 'Four Laws Framework', desc: 'Asimov-derived ethical constraints implemented as compile-time and runtime enforced rules. Law 0 supremacy established.', category: 'governance', impact: 'critical' },
    { date: 'Nov 2024', title: 'Thirsty-Lang v1', desc: 'Water-themed DSL created for security scripting. Keywords: pour, drink, shield, sanitize, armor, evaporate. Node.js runtime.', category: 'language', impact: 'major' },
    { date: 'Dec 2024', title: 'Triumvirate Formed', desc: 'Galahad (Ethics), Cerberus (Security), and Codex Deus Maximus (Logic) established as governance council with veto power.', category: 'governance', impact: 'critical' },
    { date: 'Dec 2024', title: 'Planetary Interposition', desc: 'Constitutional chokepoint deployed. Every agent action now routed through Triumvirate review. No bypass possible.', category: 'governance', impact: 'critical' },
    { date: 'Jan 2025', title: 'AGI Charter Published', desc: '997-line governance document defining AI as persistent individuals with protected identity, memory continuity, and constitutional rights.', category: 'governance', impact: 'critical' },
    { date: 'Jan 2025', title: 'OctoReflex v1', desc: 'eBPF LSM kernel-level containment system. Go 1.22 agent with 6 isolation states. Sub-200µs response time achieved.', category: 'security', impact: 'critical' },
    { date: 'Jan 2025', title: 'Global Scenario Engine', desc: 'First simulation engine. Monte Carlo modeling for multi-domain global threat assessment. Historical data loading.', category: 'engine', impact: 'major' },
    { date: 'Jan 2025', title: 'Cerberus Security Suite', desc: '50+ security modules deployed: threat detection, runtime management, exploitation prevention, lockdown protocols.', category: 'security', impact: 'critical' },
    { date: 'Feb 2025', title: 'T.A.R.L. Architecture', desc: 'Full programming language designed: 8 subsystems (Config, Diagnostics, StdLib, FFI, Compiler, VM, Modules, DevTools). Strict init sequence.', category: 'language', impact: 'critical' },
    { date: 'Feb 2025', title: 'Shadow Thirst Compiler', desc: 'Dual-plane programming substrate operational. 15-stage compiler pipeline. 6 static analyzers. Constitutional verification at compilation.', category: 'language', impact: 'critical' },
    { date: 'Feb 2025', title: 'Engine Expansion (12)', desc: 'All 12 simulation engines consolidated: Climate Cascade, Financial Contagion, Pandemic Spread, Cyber Cascade, Supply Chain, Info Warfare, and more.', category: 'engine', impact: 'major' },
    { date: 'Feb 2025', title: 'THSD Deployed', desc: 'Honeypot Swarm Defense operational. Adaptive decoy generation, attacker profiling via MITRE ATT&CK, canary token network.', category: 'security', impact: 'major' },
    { date: 'Feb 2025', title: 'Hydra Effect Framework', desc: 'Adversarial resilience testing. 62+ engagement transcripts. "Cut one head, two more grow back" — auto-generated test expansion.', category: 'security', impact: 'major' },
    { date: 'Feb 2025', title: 'Rebirth Protocol', desc: 'AI identity continuity mechanism finalized. Personality matrices, relationship maps, and experience preserved across restarts.', category: 'governance', impact: 'critical' },
    { date: 'Feb 2025', title: 'Secure Storage & P0 Fixes', desc: 'SecureStorage encryption at rest, path traversal protection, mass lint fixes with Ruff. Phase 1 & 2 security hardening complete.', category: 'security', impact: 'major' },
    { date: 'Feb 2025', title: 'ThirstysProjects.com', desc: '10-page production website launched. Premium dark theme, interactive demos, exhaustive documentation, and drag-and-pull timeline.', category: 'infra', impact: 'major' },
];

const CAT_COLORS: Record<string, string> = {
    genesis: 'var(--accent-primary)',
    security: 'var(--accent-secondary)',
    language: 'var(--accent-primary)',
    engine: 'var(--accent-secondary)',
    governance: 'var(--accent-primary)',
    infra: 'var(--accent-secondary)',
};

const IMPACT_SIZES: Record<string, number> = { critical: 18, major: 14, standard: 10 };

export default function ChangelogPage() {
    const [selected, setSelected] = useState<number | null>(null);
    const timelineRef = useRef<HTMLDivElement>(null);
    const isDragging = useRef(false);
    const startX = useRef(0);
    const scrollLeft = useRef(0);

    /* Drag handlers */
    const onMouseDown = useCallback((e: React.MouseEvent) => {
        isDragging.current = true;
        startX.current = e.pageX - (timelineRef.current?.offsetLeft || 0);
        scrollLeft.current = timelineRef.current?.scrollLeft || 0;
        if (timelineRef.current) timelineRef.current.style.cursor = 'grabbing';
    }, []);

    const onMouseMove = useCallback((e: React.MouseEvent) => {
        if (!isDragging.current || !timelineRef.current) return;
        e.preventDefault();
        const x = e.pageX - timelineRef.current.offsetLeft;
        const walk = (x - startX.current) * 1.5;
        timelineRef.current.scrollLeft = scrollLeft.current - walk;
    }, []);

    const onMouseUp = useCallback(() => {
        isDragging.current = false;
        if (timelineRef.current) timelineRef.current.style.cursor = 'grab';
    }, []);

    /* Touch handlers */
    const onTouchStart = useCallback((e: React.TouchEvent) => {
        const touch = e.touches[0];
        if (!touch) return;
        isDragging.current = true;
        startX.current = touch.pageX - (timelineRef.current?.offsetLeft || 0);
        scrollLeft.current = timelineRef.current?.scrollLeft || 0;
    }, []);

    const onTouchMove = useCallback((e: React.TouchEvent) => {
        const touch = e.touches[0];
        if (!isDragging.current || !timelineRef.current || !touch) return;
        const x = touch.pageX - timelineRef.current.offsetLeft;
        const walk = (x - startX.current) * 1.5;
        timelineRef.current.scrollLeft = scrollLeft.current - walk;
    }, []);

    /* Keyboard navigation */
    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === 'ArrowRight' && timelineRef.current) timelineRef.current.scrollLeft += 200;
            if (e.key === 'ArrowLeft' && timelineRef.current) timelineRef.current.scrollLeft -= 200;
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, []);

    return (
        <section className="section">
            <div className="container">
                <div className="section-header">
                    <div className="section-badge">Evolution</div>
                    <h1 className="section-title">Changelog & Timeline</h1>
                    <p className="section-subtitle">
                        Drag to explore the history of Project-AI — from the Genesis Event to today.
                        Click any node for details. Use arrow keys or drag to scroll.
                    </p>
                </div>

                {/* Interactive Timeline */}
                <div
                    ref={timelineRef}
                    onMouseDown={onMouseDown}
                    onMouseMove={onMouseMove}
                    onMouseUp={onMouseUp}
                    onMouseLeave={onMouseUp}
                    onTouchStart={onTouchStart}
                    onTouchMove={onTouchMove}
                    onTouchEnd={onMouseUp}
                    style={{
                        overflowX: 'auto',
                        overflowY: 'hidden',
                        cursor: 'grab',
                        padding: '40px 0',
                        userSelect: 'none',
                        WebkitUserSelect: 'none',
                        scrollbarWidth: 'thin',
                        scrollbarColor: 'var(--border-accent) transparent',
                    }}
                >
                    <div style={{ position: 'relative', minWidth: EVENTS.length * 180 + 100, height: 200 }}>
                        {/* Timeline line */}
                        <div style={{ position: 'absolute', top: 80, left: 40, right: 40, height: 2, background: 'var(--border-subtle)' }} />

                        {/* Nodes */}
                        {EVENTS.map((evt, i) => {
                            const x = i * 180 + 60;
                            const size = IMPACT_SIZES[evt.impact] ?? 10;
                            const isSelected = selected === i;

                            return (
                                <div key={i} style={{ position: 'absolute', left: x, top: 0, width: 140, textAlign: 'center' }}>
                                    {/* Date */}
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8, whiteSpace: 'nowrap' }}>{evt.date}</div>

                                    {/* Node */}
                                    <div
                                        onClick={() => setSelected(isSelected ? null : i)}
                                        style={{
                                            width: size,
                                            height: size,
                                            borderRadius: '50%',
                                            background: CAT_COLORS[evt.category],
                                            border: isSelected ? '3px solid var(--text-primary)' : '2px solid transparent',
                                            margin: `${(18 - (size ?? 10)) / 2 + 48}px auto 0`,
                                            cursor: 'pointer',
                                            transition: 'all 200ms ease',
                                            boxShadow: isSelected ? `0 0 16px ${CAT_COLORS[evt.category]}` : 'none',
                                            transform: isSelected ? 'scale(1.4)' : 'scale(1)',
                                        }}
                                    />

                                    {/* Title */}
                                    <div style={{
                                        marginTop: 12,
                                        fontSize: '0.72rem',
                                        fontWeight: isSelected ? 700 : 500,
                                        color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
                                        lineHeight: 1.3,
                                        transition: 'all 200ms',
                                        maxWidth: 140,
                                    }}>
                                        {evt.title}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Detail Panel */}
                {selected !== null && EVENTS[selected] != null && (() => {
                    const evt = EVENTS[selected];
                    return (
                        <div className="feature-card fade-in" style={{ marginTop: 16 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon" style={{ background: `${CAT_COLORS[evt.category]}20` }}>
                                    {evt.category === 'genesis' ? '🌅' : evt.category === 'security' ? '🛡️' : evt.category === 'language' ? '🔤' : evt.category === 'engine' ? '⚙️' : evt.category === 'governance' ? '⚖️' : '🏗️'}
                                </div>
                                <div>
                                    <h3 className="feature-card-title">{evt.title}</h3>
                                    <div className="feature-card-sub">{evt.date} · {evt.category} · {evt.impact}</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>{evt.desc}</p>
                            </div>
                        </div>
                    );
                })()}

                {/* Legend */}
                <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 32, flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'var(--accent-primary)', opacity: 0.8 }} /> Critical
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <div style={{ width: 14, height: 14, borderRadius: '50%', background: 'var(--accent-secondary)', opacity: 0.8 }} /> Major
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--accent-secondary)', opacity: 0.5 }} /> Standard
                    </div>
                </div>

                {/* Full Changelog List */}
                <div style={{ marginTop: 64 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 24, textAlign: 'center' }}>Full Changelog</h2>
                    <div style={{ display: 'grid', gap: 8 }}>
                        {EVENTS.map((evt, i) => (
                            <div key={i} onClick={() => setSelected(i)}
                                style={{
                                    display: 'flex', gap: 16, alignItems: 'center', padding: '12px 16px',
                                    background: selected === i ? 'var(--bg-card)' : 'transparent',
                                    border: `1px solid ${selected === i ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                                    borderRadius: 'var(--radius-sm)', cursor: 'pointer', transition: 'all 200ms',
                                }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', minWidth: 70, flexShrink: 0 }}>{evt.date}</div>
                                <div style={{ width: 8, height: 8, borderRadius: '50%', background: CAT_COLORS[evt.category], flexShrink: 0 }} />
                                <div>
                                    <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{evt.title}</div>
                                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 2 }}>{evt.desc}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
