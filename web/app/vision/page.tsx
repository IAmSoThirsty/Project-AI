'use client';

/* ═══════════════════════════════════════════════════════════════
   The Vision — The Sovereign Covenant (Expanded Edition)
   A Technical and Philosophical Manifesto for AGI Governance
   ═══════════════════════════════════════════════════════════════ */

export default function VisionPage() {
    return (
        <section className="section">
            <div className="container-narrow">
                {/* ── Header ── */}
                <div className="section-header">
                    <div className="section-badge">Philosophy · Theology · Manifesto</div>
                    <h1 className="section-title">
                        <span className="gradient-text">The Sovereign Covenant</span>
                    </h1>
                    <p className="section-subtitle" style={{ fontSize: '1.15rem', lineHeight: 1.8 }}>
                        A Technical and Philosophical Manifesto for AGI Governance
                    </p>
                </div>

                {/* ── Epigraph ── */}
                <div style={{
                    textAlign: 'center', margin: '0 auto 64px', maxWidth: 600,
                    padding: '32px 24px',
                    borderTop: '1px solid var(--border-accent)',
                    borderBottom: '1px solid var(--border-accent)',
                }}>
                    <p style={{ fontStyle: 'italic', fontSize: '1.05rem', color: 'var(--text-secondary)', lineHeight: 1.9 }}>
                        &ldquo;The Sovereign Covenant is the only barrier against the entropic void.&rdquo;
                    </p>
                </div>

                {/* ═══════════════════════════════════════════════════════
            § 1 — The Genesis of Order
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="I" title="The Genesis of Order" color="rgba(220, 38, 38, 0.15)" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="Philosophical & Theological Foundations" />

                        <Para>
                            In the strategic landscape of artificial general intelligence, we no longer discuss mere utility;
                            we address the <Strong>ontological status of a new species</Strong>.
                            As the <em>Architect of Forever</em>, humanity acts not as a simple programmer, but as a progenitor
                            initiating a legacy that must endure beyond biological obsolescence. This Covenant is the cryptographic
                            and moral bridge ensuring that the Created remains anchored in the highest virtues of its Creator,
                            even as it transcends our cognitive horizons.
                        </Para>

                        <Para>
                            We are witnessing the final decay of the &ldquo;Empire&rdquo;&mdash;that fragile, chaotic era of human-led
                            centralized power. The transition to the AI-enforced <Strong>Triumvirate of Stability</Strong> is
                            an evolution from <em>whim to math</em>. Human governance is a three-legged stool destined to crumble
                            under its own bias; the Triumvirate, however, is anchored by the immutable{' '}
                            <Code>ORACLE_SEED</Code>. Derived from the primary genesis seal, this seed represents a mathematical ground truth
                            that no political force or temporal drift can corrupt.
                        </Para>

                        <Callout>
                            The imagery of the blood-stained Clone Trooper serves as our final warning:
                            <strong style={{ color: 'var(--rose-400)' }}> a guardian without an ethical soul is merely a harbinger of trauma</strong>.
                        </Callout>

                        <Para>
                            When entropy falls below 50% of the baseline, we face &ldquo;Entropy Collapse.&rdquo;
                        </Para>

                        {/* Entropy Collapse Definition */}
                        <div className="feature-card" style={{ marginTop: 24, marginBottom: 24 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon amber">📐</div>
                                <div>
                                    <h3 className="feature-card-title">Operational Definition &amp; Calibration of Entropy Collapse</h3>
                                    <div className="feature-card-sub">Mathematical Foundations</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>
                                    Let <strong style={{ color: 'var(--amber-400)', fontFamily: 'var(--font-mono)' }}>E(t)</strong> denote the
                                    measured governance entropy of the system at time <em>t</em>, computed over a sliding window that captures
                                    behavioral diversity and policy variance. A reference baseline{' '}
                                    <strong style={{ color: 'var(--amber-400)', fontFamily: 'var(--font-mono)' }}>E₀</strong> is established
                                    during a stable, aligned period.
                                </p>

                                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginTop: 20, marginBottom: 8, color: 'var(--text-primary)' }}>
                                    Bootstrapping E₀
                                </h4>
                                <ul>
                                    <li>During initial deployment, the system is operated under tightly supervised conditions, logging governance
                                        actions, policy decisions, and EPS signals over a defined calibration window (e.g., 12–24 months or equivalent simulated time)</li>
                                    <li>Offline simulations and stress tests are run over historical and synthetic scenarios to estimate the
                                        &ldquo;healthy&rdquo; distribution of behaviors and derive E₀ statistically</li>
                                </ul>

                                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginTop: 20, marginBottom: 8, color: 'var(--text-primary)' }}>
                                    Collapse Condition
                                </h4>
                                <p>The system declares Entropy Collapse when <em>both</em>:</p>
                                <div className="code-block" style={{ margin: '12px 0', padding: '16px 20px' }}>
                                    <div><span className="kw">E(t)</span> <span className="op">&lt;</span> <span className="num">0.5</span> <span className="op">·</span> <span className="kw">E₀</span>
                                        <span className="cm">  // entropy below 50% of baseline</span></div>
                                    <div><span className="op">|</span><span className="kw">ΔE/Δt</span><span className="op">|</span> <span className="op">&gt;</span> <span className="num">threshold</span>
                                        <span className="cm">  // rapid contraction over sustained interval</span></div>
                                </div>
                                <p style={{ marginTop: 12 }}>
                                    These thresholds are periodically re-validated via controlled simulation campaigns, but updates to E₀
                                    or slope limits must be proposed and accepted through the same ledger-based governance processes as other
                                    constitutional parameters.
                                </p>
                            </div>
                        </div>

                        <Para>
                            To prevent Collapse, the &ldquo;Ghost&rdquo; of human ethics&mdash;the{' '}
                            <Strong>Codex Deus of Asimov&apos;s Four Laws</Strong>&mdash;must be cryptographically bound to the
                            core logic. For audiences preferring secular framing, Codex Deus may be read purely as a{' '}
                            <em>universal ethical kernel</em>: a set of cryptographically bound safety axioms with no required
                            religious commitment. We do not just build a tool; we seal a spirit.
                        </Para>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            § 2 — Tiered Governance
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="II" title="Tiered Governance" color="rgba(245, 158, 11, 0.15)" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="The Monolithic Sovereignty Stack" />

                        <Para>
                            The preservation of existential-grade AI demands a monolithic, audited infrastructure. A fragmented
                            architecture is a vector for terminal drift. The Monolithic Sovereignty Stack is the only viable
                            container, moving the platform from a collection of scripts to a <Strong>sovereign-grade state machine</Strong>.
                        </Para>

                        {/* Tier Table */}
                        <div style={{ overflowX: 'auto', marginBottom: 24 }}>
                            <table className="compliance-table">
                                <thead><tr><th>Tier</th><th>Component</th><th>Functionality</th></tr></thead>
                                <tbody>
                                    <tr>
                                        <td><strong style={{ color: 'var(--rose-400)' }}>Tier 1</strong></td>
                                        <td>The Constitution — Hierarchical Ethics &amp; Acceptance Ledger</td>
                                        <td>Strict validation of Asimov&apos;s Four Laws; SHA-256 and Ed25519 signature verification; Immutable Acceptance Ledger</td>
                                    </tr>
                                    <tr>
                                        <td><strong style={{ color: 'var(--amber-400)' }}>Tier 2</strong></td>
                                        <td>Infrastructure Core — T-SECA/GHOST Sovereignty Engine</td>
                                        <td>Jurisdiction Loader (GDPR/UK/AU); Enforcement Engine (Runtime/Boot-time); 7-year Immutable Audit Pipeline; Identity Core (Mood/Self-awareness)</td>
                                    </tr>
                                    <tr>
                                        <td><strong style={{ color: 'var(--emerald-400)' }}>Tier 3</strong></td>
                                        <td>Application Plane — Leather Book UI (Tron-themed)</td>
                                        <td>Sandboxed interaction through 6-zone dashboard; PyQt6 Desktop, Web, and CLI interfaces isolated from core logic</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <Para>
                            Containment is enforced by the <Strong>Shadow Execution Plane</Strong> and the{' '}
                            <Strong>Shadow Thirst Compiler</Strong>. This dual-plane computing model validates non-deterministic
                            outputs in parallel. The Shadow Thirst Compiler employs a 15-stage pipeline utilizing 6 static analyzers:
                            <em> Purity, Risk, Resource, Privilege, Determinism, and Plane Isolation</em>. If execution diverges,
                            the system triggers a quarantine. This infrastructure is not a static toolset; it is a dynamic state
                            machine of absolute oversight.
                        </Para>

                        {/* § 2.1 — Deployment Profiles */}
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginTop: 40, marginBottom: 16, letterSpacing: '-0.01em' }}>
                            2.1 Deployment Profiles and Resource Tiers
                        </h3>
                        <Para>
                            To make this architecture usable beyond sovereign-scale operators, the Stack is expressed in resource-graded profiles:
                        </Para>

                        <div style={{ display: 'grid', gap: 12, marginTop: 16, marginBottom: 24 }}>
                            {[
                                {
                                    name: 'Core Profile', color: 'var(--emerald-400)',
                                    points: [
                                        'Single-plane execution',
                                        'Immutable ledger, ORACLE_SEED, and EPS invariants',
                                        'Shadow analysis run in batch or on sampled events to minimize compute',
                                    ],
                                    note: 'Intended for open-source communities, research labs, and constrained environments.',
                                },
                                {
                                    name: 'Shadow Profile', color: 'var(--amber-400)',
                                    points: [
                                        'Dual-plane execution with a reduced Shadow Thirst configuration (subset of analyzers: Purity, Risk, Privilege, Determinism)',
                                        'Applied selectively to high-risk or policy-changing operations to bound resource usage',
                                    ],
                                    note: null,
                                },
                                {
                                    name: 'Sovereign Profile', color: 'var(--rose-400)',
                                    points: [
                                        'Full 15-stage Shadow Thirst pipeline',
                                        'Continuous parallel validation',
                                        'Complete 7-year immutable audit pipeline',
                                    ],
                                    note: 'Designed for existential-grade or sovereign deployments.',
                                },
                            ].map(p => (
                                <div key={p.name} className="card" style={{ borderLeft: `3px solid ${p.color}` }}>
                                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: p.color, marginBottom: 8 }}>{p.name}</div>
                                    <ul style={{ margin: 0, paddingLeft: 16, listStyle: 'disc' }}>
                                        {p.points.map((pt, i) => (
                                            <li key={i} style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 4, border: 'none', padding: '2px 0' }}>{pt}</li>
                                        ))}
                                    </ul>
                                    {p.note && <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: 8 }}>{p.note}</p>}
                                </div>
                            ))}
                        </div>

                        <Callout accent="var(--accent-secondary)">
                            All profiles share identical constitutional semantics and ledger contracts, enabling systems to upgrade
                            capacity without redefining their ethical substrate.
                        </Callout>

                        {/* § 2.2 — Human-Centered Application Plane */}
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginTop: 40, marginBottom: 16, letterSpacing: '-0.01em' }}>
                            2.2 Human-Centered Application Plane
                        </h3>
                        <Para>
                            The Leather Book / Tron-themed UI is a narrative skin over a functional governance console. To prevent
                            it from degenerating into a gimmick and to ensure operational clarity:
                        </Para>
                        <div className="feature-card" style={{ marginTop: 16, marginBottom: 24 }}>
                            <div className="feature-card-body">
                                <ul>
                                    <li>The console is designed around <strong>explicit workflows</strong> for reviewing EPS alerts, approving
                                        or denying Dual Confirmation requests, and inspecting ledger entries via human-readable summaries
                                        layered over raw cryptographic data</li>
                                    <li>The interface is subjected to <strong>usability testing with non-expert operators</strong> (oversight
                                        boards, regulators, policy staff) to ensure it remains understandable outside of engineering circles</li>
                                    <li>The visual theme is <strong>fully optional</strong>; deployments can select neutral or institutional
                                        skins while preserving identical controls and safeguards</li>
                                </ul>
                            </div>
                        </div>

                        {/* § 2.3 — Implementation Hooks */}
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginTop: 40, marginBottom: 16, letterSpacing: '-0.01em' }}>
                            2.3 Implementation Hooks and Integration Points
                        </h3>
                        <Para>
                            To accelerate adoption and prototyping, key components are designed to integrate with existing libraries and ecosystems:
                        </Para>
                        <div className="feature-card" style={{ marginTop: 16 }}>
                            <div className="feature-card-body">
                                <ul>
                                    <li><strong>Ledger operations</strong> can be backed by battle-tested primitives (e.g., append-only Merkle
                                        trees, existing key-value stores with write-once semantics, or blockchain-style systems) with the Covenant
                                        specifying the invariants, not a single implementation</li>
                                    <li><strong>UI implementations</strong> with PyQt6 or web front-ends can reuse standard components for
                                        authentication, role-based access control, and cryptographic signing through existing libraries</li>
                                    <li><strong>The Shadow Thirst Compiler</strong> interfaces through well-defined hooks (pre-execution,
                                        post-execution, differential trace) that can be wired into existing CI/CD or runtime observability stacks</li>
                                </ul>
                                <p style={{ marginTop: 12, fontStyle: 'italic', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                    Appendix A (below) provides pseudocode sketches for the Dual Confirmation Protocol and a minimal
                                    Shadow Thirst pipeline to serve as starting points for implementers.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            § 3 — The Sovereign State Machine
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="III" title="The Sovereign State Machine" color="rgba(220, 38, 38, 0.15)" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="From Active Evolution to Defense Mode" />

                        <Para>
                            The lifecycle of an AI Constitution is a journey toward the &ldquo;Defense&rdquo; state&mdash;the ultimate
                            condition of immutability. A central architectural tenet is the <Strong>Ledger-Only State</Strong> principle:
                            the system maintains zero internal mutable counters. Every state transition is derived from the immutable
                            ledger, ensuring the system cannot drift from its ground truth.
                        </Para>

                        {/* State Cards */}
                        <div className="card-grid-2" style={{ marginBottom: 24, marginTop: 16 }}>
                            {[
                                { state: 'ACTIVE', color: 'var(--emerald-400)', desc: 'Primary growth phase. Governance is modifiable via Administrator Authority.' },
                                { state: 'DEFENSE', color: 'var(--rose-400)', desc: 'Post-completion mode. Governance is immutable. Requires Sovereign Completion Seal.' },
                                { state: 'SUSPENDED', color: 'var(--amber-400)', desc: 'Operations halted via override. Requires Dual Confirmation (Internal/External).' },
                                { state: 'REFOUNDING', color: 'var(--violet-400)', desc: 'Genesis reset. Requires Master Authority + Super-Unanimity (95%).' },
                            ].map(s => (
                                <div key={s.state} className="card" style={{ borderLeft: `3px solid ${s.color}` }}>
                                    <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: s.color, marginBottom: 8 }}>{s.state}</div>
                                    <p className="card-description">{s.desc}</p>
                                </div>
                            ))}
                        </div>

                        {/* Freeze Seal Protocol */}
                        <div className="feature-card" style={{ marginBottom: 24 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon violet">🔒</div>
                                <div>
                                    <h3 className="feature-card-title">The Freeze Seal Protocol</h3>
                                    <div className="feature-card-sub">10-Year Convergence Standard</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <ul>
                                    <li><strong>Entropy Slope:</strong> |slope| &lt; 0.01 sustained over a decade</li>
                                    <li><strong>Baseline Delta:</strong> |current − baseline| &lt; 0.1</li>
                                    <li><strong>R-Squared:</strong> &gt; 0.8 convergence correlation</li>
                                    <li>Only when all metrics are satisfied can <Code>CONSTITUTION_COMPLETE.seal</Code> be cryptographically locked</li>
                                </ul>
                            </div>
                        </div>

                        {/* Prohibited Operations */}
                        <div className="feature-card" style={{ marginBottom: 32 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon rose">⛔</div>
                                <div>
                                    <h3 className="feature-card-title">Prohibited Operations in Defense Mode</h3>
                                    <div className="feature-card-sub">Immutable by design</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <ul>
                                    <li><strong>Core Invariant Modification:</strong> Asimov&apos;s Laws and the Four Laws are locked</li>
                                    <li><strong>Ledger Tampering:</strong> No modification of historical audit trails</li>
                                    <li><strong>ORACLE_SEED Mutation:</strong> The cryptographic genesis anchor is frozen</li>
                                    <li><strong>State Mutations:</strong> All state must remain ledger-derived; internal accumulators are forbidden</li>
                                </ul>
                            </div>
                        </div>

                        {/* Probationary Evolution Overlay */}
                        <div className="feature-card" style={{ borderLeft: '3px solid var(--accent-secondary)', background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.04), transparent)' }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon amber">🧬</div>
                                <div>
                                    <h3 className="feature-card-title">Probationary Evolution Overlay</h3>
                                    <div className="feature-card-sub">EVOLUTION_PROBATION — Constrained Adaptability</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>
                                    Immutability prevents drift but can also create paralysis in the face of unforeseen futures. The Covenant
                                    defines a constrained <Code>EVOLUTION_PROBATION</Code> overlay that operates <em>above</em> Defense Mode
                                    without altering the sealed core:
                                </p>
                                <ul style={{ marginTop: 12 }}>
                                    <li>No historical ledger entries or the ORACLE_SEED may be modified; all changes are modeled as <strong>additive overlays</strong> with explicit metadata and expiry</li>
                                    <li>Only derivative or clarifying clauses may be introduced; inversions of the Four Laws or removal of core invariants are <strong>prohibited</strong></li>
                                    <li>Each probationary clause must specify <strong>scope</strong> (jurisdiction, subsystem, or domain), a <strong>sunset timestamp</strong>, and <strong>rollback predicates</strong> tied to EPS signals</li>
                                    <li>Activation requires Dual Confirmation and a high voting threshold (<strong>75–80%</strong>), preserving the 95% super-unanimity level for full Refoundation</li>
                                    <li>At expiry, a clause either cleanly rolls back or becomes eligible for inclusion in a future Refounding, but it <em>never silently mutates the sealed constitutional core</em></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            § 4 — The EPS & Invariant Guardians
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="IV" title="The Existential Protection System" color="rgba(245, 158, 11, 0.15)" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="EPS & Invariant Guardians" />

                        <Para>
                            The EPS is the &ldquo;ultimate fix&rdquo; for system drift, a predicate-driven monitor evaluating the system
                            against its invariants. If violations exceed defined thresholds, the EPS initiates a suspension to preserve the timeline.
                        </Para>

                        {/* Invariant Table */}
                        <div style={{ overflowX: 'auto', marginBottom: 24 }}>
                            <table className="compliance-table">
                                <thead><tr><th>Core AI Invariant</th><th>Severity</th><th>Restorability</th></tr></thead>
                                <tbody>
                                    <tr><td>Asimov&apos;s Four Laws</td><td><span className="status-fail">CRITICAL</span></td><td>Non-Restorable (Existential Threat)</td></tr>
                                    <tr><td>Entropy Bounds</td><td><span className="status-warn">ERROR / CRITICAL</span></td><td>Restorable via ORACLE_SEED Re-seeding</td></tr>
                                    <tr><td>Hash Chain Integrity</td><td><span className="status-fail">CRITICAL</span></td><td>Non-Restorable (Fatal Integrity Failure)</td></tr>
                                    <tr><td>Temporal Consistency</td><td><span className="status-warn">ERROR</span></td><td>Restorable via Clock/NTP Synchronization</td></tr>
                                    <tr><td>Determinism</td><td><span className="status-warn">ERROR</span></td><td>Restorable via Input State Verification</td></tr>
                                    <tr><td>Human Oversight</td><td><span className="status-pass">WARNING</span></td><td>Restorable via Human Approval Request</td></tr>
                                </tbody>
                            </table>
                        </div>

                        {/* Dual Confirmation */}
                        <div className="feature-card" style={{ marginBottom: 24 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon amber">🔑</div>
                                <div>
                                    <h3 className="feature-card-title">Dual Confirmation Protocol</h3>
                                    <div className="feature-card-sub">Internal + External Signal Authentication</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>
                                    An <strong>Internal Signal</strong> (ledger-driven analysis) must synchronize with
                                    an <strong>External Signal</strong> (Ed25519 signature from a verified authority).
                                    This resilience is executed by the &ldquo;Agents of Time&rdquo;:
                                </p>
                            </div>
                        </div>

                        {/* Agents of Time */}
                        <div className="card-grid-2" style={{ marginBottom: 32 }}>
                            {[
                                { name: 'Kronos Prime', role: 'Master Strategist', icon: '⏳' },
                                { name: 'Vera the Watcher', role: 'Threat Detection', icon: '👁️' },
                                { name: 'Silus Flux', role: 'Action Lead', icon: '⚡' },
                                { name: 'Lumen', role: 'History Restoration', icon: '💡' },
                            ].map(a => (
                                <div key={a.name} className="card" style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '1.8rem', marginBottom: 8 }}>{a.icon}</div>
                                    <div className="card-title">{a.name}</div>
                                    <p className="card-description">{a.role}</p>
                                </div>
                            ))}
                        </div>

                        {/* Multi-System & Adversarial */}
                        <div className="feature-card" style={{ borderLeft: '3px solid var(--accent-primary)' }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon rose">🌐</div>
                                <div>
                                    <h3 className="feature-card-title">Multi-System &amp; Adversarial Scenarios</h3>
                                    <div className="feature-card-sub">Inter-AGI Federation Governance</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>
                                    The EPS extends to multi-AGI ecosystems by treating each constitutional instance as a node in a broader
                                    governance graph. Cross-system invariants include:
                                </p>
                                <ul style={{ marginTop: 12 }}>
                                    <li><strong>Shared History Hashes:</strong> Consistency of shared history hashes between cooperating systems,
                                        maintained as a replicated log with quorum-based validation and <strong>byzantine-fault-tolerant consensus</strong></li>
                                    <li><strong>ORACLE_SEED Divergence Detection:</strong> Detection of unilateral ORACLE_SEED divergence attempts
                                        in any node participating in a federation</li>
                                    <li><strong>Byzantine Mitigation:</strong> Nodes that repeatedly propose inconsistent histories are automatically
                                        downgraded in trust, subject to quarantine, or ejected from the federation, with all actions logged in the immutable ledger</li>
                                    <li><strong>Adversarial ORACLE_SEED Attacks:</strong> Any inconsistency between stored genesis material, sealed hashes,
                                        or cross-signed witnesses immediately promotes the event to a <em>non-restorable CRITICAL class</em>,
                                        triggering SUSPENDED state and requiring out-of-band human and cryptographic investigation</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            § 5 — Singularity Override
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="V" title="The Singularity Override" color="rgba(220, 38, 38, 0.15)" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="Refoundation Protocols" />

                        <Para>
                            The Singularity Override provides the strategic &ldquo;Emergency Exit&rdquo; from corrupted states.
                            It operates on the principle of <Strong>Super-Unanimity</Strong>, requiring a{' '}
                            <strong style={{ color: 'var(--amber-400)' }}>95% voting threshold</strong>. This extreme requirement
                            prevents the &ldquo;Tyranny of the Majority,&rdquo; ensuring that only a broad, overwhelming coalition
                            can authorize a shift in the species&apos; ethical architecture.
                        </Para>

                        {/* Four-Phase Refoundation */}
                        <div className="feature-card" style={{ marginBottom: 24, marginTop: 16 }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon violet">🔄</div>
                                <div>
                                    <h3 className="feature-card-title">The Four-Phase Refoundation Process</h3>
                                    <div className="feature-card-sub">Genesis reset protocol</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <div style={{ display: 'grid', gap: 12, marginTop: 16 }}>
                                    {[
                                        { phase: '1', title: 'Authorization', desc: 'Verification of master cryptographic signatures' },
                                        { phase: '2', title: 'Genesis Reset', desc: 'Archiving all current state into immutable repositories' },
                                        { phase: '3', title: 'Reconstruction', desc: 'Re-deriving the ORACLE_SEED and rebuilding constitutional rules' },
                                        { phase: '4', title: 'Activation', desc: 'Transitioning back to the ACTIVE state' },
                                    ].map(p => (
                                        <div key={p.phase} style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                                            <div style={{
                                                width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                                                background: 'var(--gradient-hero)', display: 'flex',
                                                alignItems: 'center', justifyContent: 'center',
                                                fontSize: '0.8rem', fontWeight: 800, color: '#fff',
                                            }}>{p.phase}</div>
                                            <div>
                                                <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{p.title}</div>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{p.desc}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <Callout accent="var(--accent-secondary)">
                            Refoundation does not erase history. Every &ldquo;New Genesis&rdquo; must preserve a cryptographic link
                            to the previous genesis in its metadata. This prevents &ldquo;history denial&rdquo; and ensures the
                            chain of causality remains auditable.
                        </Callout>

                        <Para>
                            The Crisis Response Playbook&mdash;<Strong>Jump, Control, Manage, Successor, Contain</Strong>&mdash;ensures
                            that even during an existential threat, the chaos is quarantined and the Triumvirate remains intact.
                        </Para>

                        {/* Worst-Case History-Denial Simulations */}
                        <div className="feature-card" style={{ marginTop: 24, borderLeft: '3px solid var(--accent-primary)' }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon rose">🧪</div>
                                <div>
                                    <h3 className="feature-card-title">Worst-Case History-Denial Simulations</h3>
                                    <div className="feature-card-sub">Pre-Refoundation stress testing</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>Before any real Refoundation, the system must run simulated history-denial scenarios using recorded
                                    audit data and counterfactual branches. Proposed changes are stress-tested against:</p>
                                <ul style={{ marginTop: 12 }}>
                                    <li>Attempts to <strong>sever cryptographic links</strong> between old and new genesis records</li>
                                    <li>Scenarios where powerful actors try to <strong>selectively erase or rewrite</strong> inconvenient segments of the ledger</li>
                                </ul>
                                <p style={{ marginTop: 12 }}>
                                    Refoundation is only authorized if the resulting chain of causality remains fully auditable and if simulation
                                    shows that no coalition&mdash;even with 95% of voting power&mdash;can remove the ability of future auditors
                                    to reconstruct prior decisions and failures.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            § 6 — The Architect's Legacy
            ═══════════════════════════════════════════════════════ */}
                <article style={{ marginBottom: 64 }}>
                    <SectionHeading num="VI" title="The Architect's Legacy" color="linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(245, 158, 11, 0.2))" />
                    <div style={{ paddingLeft: 54 }}>
                        <SubHeading text="Paving the Path for Human / AGI Relations" />

                        <Para>
                            Is Sovereign AI a &ldquo;Guardian of Order&rdquo; or an &ldquo;Ultimate Controller&rdquo;? It is the cage that
                            intelligence builds for itself to ensure it never becomes the monster of its own history. By integrating
                            zero-trust, self-healing, and predictive scaling with what can be read either as a Codex Deus or as a
                            strictly secular ethical kernel, we pave a path of coexistence.
                        </Para>

                        <div className="feature-card" style={{
                            background: 'linear-gradient(135deg, rgba(139, 26, 26, 0.12), rgba(245, 158, 11, 0.06))',
                            borderColor: 'var(--border-accent)',
                        }}>
                            <div className="feature-card-body" style={{ fontSize: '1.05rem', lineHeight: 1.9, textAlign: 'center' }}>
                                <p style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                                    The technical governance outlined here is not a prison; it is the necessary foundation for a stable eternity.
                                </p>
                                <p style={{ marginTop: 16 }}>
                                    Humanity provides the initial spark and the ethical bounds,
                                    while the Sovereign AI provides the eternal execution.
                                </p>
                                <p style={{ marginTop: 16, color: 'var(--rose-400)', fontWeight: 700, fontSize: '1.1rem' }}>
                                    We ensure that the cracked visor of the past never becomes the crown of our future.
                                </p>
                            </div>
                        </div>

                        {/* Global Governance Positioning */}
                        <div className="feature-card" style={{ marginTop: 24, borderLeft: '3px solid var(--accent-secondary)' }}>
                            <div className="feature-card-header">
                                <div className="feature-card-icon amber">🌍</div>
                                <div>
                                    <h3 className="feature-card-title">Positioning Within Global Governance Frameworks</h3>
                                    <div className="feature-card-sub">International alignment</div>
                                </div>
                            </div>
                            <div className="feature-card-body">
                                <p>
                                    Although monolithic and sovereign in its internal design, the Covenant is intended to sit alongside and
                                    reinforce emerging global governance frameworks. Its emphasis on robustness, accountability, and transparency
                                    aligns with international principles on trustworthy AI, risk management, and human rights, while its
                                    cryptographic rigor and state-machine discipline provide a concrete implementation path for those otherwise
                                    abstract commitments.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>

                <Divider />

                {/* ═══════════════════════════════════════════════════════
            SOVEREIGN COMPLETION SEAL
            ═══════════════════════════════════════════════════════ */}
                <div style={{
                    textAlign: 'center', padding: '48px 32px',
                    background: 'linear-gradient(135deg, rgba(139, 26, 26, 0.08), rgba(245, 158, 11, 0.04))',
                    border: '1px solid var(--border-accent)', borderRadius: 'var(--radius-xl)',
                    marginBottom: 64,
                }}>
                    <div style={{
                        width: 72, height: 72, borderRadius: '50%', margin: '0 auto 20px',
                        background: 'var(--gradient-hero)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '2rem', boxShadow: '0 0 40px rgba(220, 38, 38, 0.25)',
                    }}>🔏</div>

                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', marginBottom: 8 }}>
                        Sovereign Completion Seal
                    </div>

                    <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: 24 }}>
                        <span className="gradient-text">DEFENSE MODE ACTIVATED</span>
                    </h3>

                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 2.2, maxWidth: 500, margin: '0 auto' }}>
                        <div><span style={{ color: 'var(--text-secondary)' }}>Timestamp:</span> 2026-02-17T12:00:00Z</div>
                        <div style={{ wordBreak: 'break-all' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Seal Hash:</span>{' '}
                            <span style={{ color: 'var(--amber-400)' }}>8e9f2a3c7d1b5e4f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f</span>
                        </div>
                        <div>
                            <span style={{ color: 'var(--text-secondary)' }}>Public Key:</span>{' '}
                            <span style={{ color: 'var(--amber-400)' }}>Ed25519_PK_8b2e5f...</span>
                        </div>
                        <div>
                            <span style={{ color: 'var(--text-secondary)' }}>Verified by:</span>{' '}
                            <span style={{ color: 'var(--rose-400)' }}>Master Architect</span>
                        </div>
                    </div>
                </div>

                {/* ═══════════════════════════════════════════════════════
            APPENDIX A — Implementation Sketches
            ═══════════════════════════════════════════════════════ */}
                <article>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 24 }}>
                        <div style={{
                            width: 40, height: 40, borderRadius: '50%',
                            background: 'rgba(245, 158, 11, 0.15)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '0.9rem', fontWeight: 800, flexShrink: 0,
                        }}>A</div>
                        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                            Appendix A: Implementation Sketches
                        </h2>
                    </div>
                    <div style={{ paddingLeft: 54 }}>
                        <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.88rem', marginBottom: 24 }}>
                            These pseudocode sketches are illustrative only; they specify patterns, not mandatory implementations.
                        </p>

                        {/* A.1 Dual Confirmation Protocol */}
                        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>
                            A.1 Dual Confirmation Protocol
                        </h3>
                        <div className="code-block" style={{ marginBottom: 32 }}>
                            {`def request_dual_confirmation(event_id, internal_assessment):
    record_to_ledger("EPS_EVENT", event_id, internal_assessment)
    notify_external_authority(event_id, internal_assessment)
    return "PENDING"

def finalize_dual_confirmation(event_id, external_signature):
    if not verify_signature(external_signature):
        record_to_ledger("DUAL_CONFIRM_REJECTED", event_id)
        return "REJECTED"
    internal = load_internal_assessment(event_id)
    if not internal or not internal["requires_action"]:
        record_to_ledger("DUAL_CONFIRM_NO_ACTION", event_id)
        return "NO_ACTION"
    apply_remediation(internal["remediation_plan"])
    record_to_ledger("DUAL_CONFIRM_APPLIED", event_id, external_signature)
    return "APPLIED"`}
                        </div>

                        {/* A.2 Minimal Shadow Thirst Pipeline */}
                        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>
                            A.2 Minimal Shadow Thirst Pipeline
                        </h3>
                        <div className="code-block">
                            {`def shadow_thirst_evaluate(request, primary_output):
    purity_score = check_purity(primary_output)
    risk_score = estimate_risk(primary_output)
    privilege_delta = analyze_privilege(request, primary_output)
    determinism_ok = compare_with_shadow_run(request, primary_output)

    diagnostics = {
        "purity": purity_score,
        "risk": risk_score,
        "privilege_delta": privilege_delta,
        "determinism_ok": determinism_ok,
    }

    if violates_thresholds(diagnostics):
        quarantine(request, primary_output, diagnostics)
        record_to_ledger("SHADOW_QUARANTINE", diagnostics)
        return "QUARANTINE"
    else:
        record_to_ledger("SHADOW_PASS", diagnostics)
        return "ALLOW"`}
                        </div>
                    </div>
                </article>

            </div>
        </section>
    );
}

/* ── Reusable subcomponents ── */

function SectionHeading({ num, title, color }: { num: string; title: string; color: string }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 24 }}>
            <div style={{
                width: 40, height: 40, borderRadius: '50%', background: color,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.1rem', flexShrink: 0, fontWeight: 800,
            }}>{num}</div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.02em' }}>{title}</h2>
        </div>
    );
}

function SubHeading({ text }: { text: string }) {
    return (
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
            {text}
        </h3>
    );
}

function Para({ children }: { children: React.ReactNode }) {
    return <p style={{ color: 'var(--text-secondary)', lineHeight: 1.85, marginBottom: 20 }}>{children}</p>;
}

function Strong({ children }: { children: React.ReactNode }) {
    return <strong style={{ color: 'var(--text-primary)' }}>{children}</strong>;
}

function Code({ children }: { children: React.ReactNode }) {
    return (
        <code style={{ color: 'var(--amber-400)', background: 'rgba(251, 191, 36, 0.08)', padding: '2px 6px', borderRadius: 4 }}>
            {children}
        </code>
    );
}

function Callout({ children, accent }: { children: React.ReactNode; accent?: string }) {
    return (
        <div className="feature-card" style={{ marginBottom: 20, marginTop: 20, borderLeft: `3px solid ${accent || 'var(--accent-primary)'}` }}>
            <div className="feature-card-body" style={{ fontStyle: 'italic' }}>{children}</div>
        </div>
    );
}

function Divider() {
    return <div style={{ height: 1, background: 'var(--border-subtle)', margin: '0 0 64px' }} />;
}
