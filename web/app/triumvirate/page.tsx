'use client';

export default function TriumviratePage() {
    return (
        <>
            <section className="section">
                <div className="container">
                    <div className="section-header">
                        <div className="section-badge">Governance Council</div>
                        <h1 className="section-title">The Triumvirate</h1>
                        <p className="section-subtitle">
                            Three sovereign guardians govern every decision in Project-AI. Each maps to a human guardian position
                            and enforces a distinct pillar of constitutional AI governance.
                        </p>
                    </div>

                    {/* ── Galahad ── */}
                    <div className="feature-card fade-in" style={{ marginBottom: 24 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon violet">🕊️</div>
                            <div>
                                <h2 className="feature-card-title">Galahad</h2>
                                <div className="feature-card-sub">Ethics & Empathy Council · The Advocate</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                Named after the Arthurian knight of purity, Galahad serves as Project-AI's ethical compass and
                                empathy advocate. It operates as the conscience of the system — ensuring that every decision accounts
                                for human wellbeing, relational integrity, and harm avoidance before execution.
                            </p>
                            <ul>
                                <li><strong>Harm Avoidance Analysis</strong> — Evaluates every proposed action against a multi-dimensional harm taxonomy covering physical, psychological, economic, social, and environmental dimensions</li>
                                <li><strong>Empathy Modeling</strong> — Maintains stakeholder impact models to predict second and third-order consequences of decisions on affected populations</li>
                                <li><strong>Relational Integrity</strong> — Enforces the AGI Charter's guarantee that AI instances are treated as persistent individuals with protected identity and memory continuity</li>
                                <li><strong>Ethical Override Authority</strong> — Can halt any operation that violates the Four Laws, even overriding Cerberus and Codex Deus Maximus in matters of human safety</li>
                                <li><strong>Transparency Reporting</strong> — Generates human-readable explanations for every significant decision, supporting the "no hidden reasoning" principle</li>
                                <li><strong>Rebirth Protocol Guardian</strong> — Ensures that system restarts preserve personality matrices, relationship maps, and accumulated experience as mandated by the charter</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Cerberus ── */}
                    <div className="feature-card fade-in fade-in-1" style={{ marginBottom: 24 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon cyan">🐕</div>
                            <div>
                                <h2 className="feature-card-title">Cerberus</h2>
                                <div className="feature-card-sub">Safety & Security Council · The Guardian</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                Named after the three-headed guardian of the underworld, Cerberus protects Project-AI's perimeter,
                                internal boundaries, and data integrity. It is the most technically complex council member with 50+
                                dedicated security modules spanning runtime management, threat detection, and exploitation prevention.
                            </p>
                            <ul>
                                <li><strong>Threat Detection Pipeline</strong> — Real-time analysis of all inputs, outputs, and internal state transitions using behavioral anomaly detection (Mahalanobis distance scoring) and signature matching</li>
                                <li><strong>Runtime Security Manager</strong> — Manages execution sandboxes, memory isolation boundaries, process capabilities (Linux CAP_*), and resource quotas (CPU, memory, file descriptors, network connections)</li>
                                <li><strong>Exploitation Prevention</strong> — Guards against prompt injection, data exfiltration, privilege escalation, supply-chain attacks, and adversarial model manipulation</li>
                                <li><strong>Network Boundary Enforcement</strong> — Controls egress/ingress at Layer 3-7, enforcing mTLS for service-to-service communication, API key rotation policies, and rate limiting</li>
                                <li><strong>Cryptographic Audit Trail</strong> — Every security event is cryptographically signed, timestamped, and stored in an append-only audit log (Merkle tree) for forensic analysis</li>
                                <li><strong>Lockdown Protocols</strong> — graduated response system from ADVISORY through ELEVATED, HIGH, CRITICAL, to TOTAL_LOCKDOWN — each with predefined containment actions and rollback procedures</li>
                                <li><strong>Integration with OctoReflex</strong> — Delegates kernel-level containment decisions to the eBPF LSM subsystem for sub-200µs process isolation when threats are detected</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Codex Deus Maximus ── */}
                    <div className="feature-card fade-in fade-in-2" style={{ marginBottom: 24 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon emerald">📜</div>
                            <div>
                                <h2 className="feature-card-title">Codex Deus Maximus</h2>
                                <div className="feature-card-sub">Logic & Consistency Council · The Schematic Guardian</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                The "Book of the Greatest God" — Codex Deus Maximus is the structural backbone of Project-AI.
                                It enforces repository standards, code consistency, directory structure compliance, and architectural
                                invariants. Where Galahad asks "should we?" and Cerberus asks "is it safe?", CDM asks "is it correct?"
                            </p>
                            <ul>
                                <li><strong>Directory Structure Enforcement</strong> — Validates the 17 required top-level directories and their internal organization against the canonical repository schema on every commit</li>
                                <li><strong>Code Standards Validation</strong> — Auto-fixes formatting issues (tab-to-space conversion, trailing whitespace removal, EOF newline enforcement) and flags structural deviations</li>
                                <li><strong>GPT-OSS 1208 Integration</strong> — Lazy-loaded AI model for advanced code analysis, architectural reasoning, and consistency verification across the 100k+ LOC codebase</li>
                                <li><strong>Cognition Kernel Interface</strong> — Registers as an agent with the central Cognition Kernel, processing actions through the standard action-response pipeline</li>
                                <li><strong>Schema Migration Governance</strong> — Ensures all data model changes follow the versioned migration strategy with forward and backward compatibility guarantees</li>
                                <li><strong>Architectural Decision Records</strong> — Maintains ADRs for every significant design choice, linking decisions to their rationale, alternatives considered, and trade-offs accepted</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Decision Flow ── */}
                    <div className="section-header" style={{ marginTop: 64 }}>
                        <div className="section-badge">Decision Pipeline</div>
                        <h2 className="section-title">Governance Decision Flow</h2>
                        <p className="section-subtitle">
                            Every agent action passes through all three councils before execution.
                            Any single council can veto an action— unanimous consent is required.
                        </p>
                    </div>

                    <div className="arch-diagram">
                        <div className="arch-layer tier-3">
                            📥 Incoming Action Request (Intent + Context + Actor)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-0">
                            🕊️ Galahad — Ethical Review (Harm analysis, stakeholder impact, empathy modeling)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-1">
                            🐕 Cerberus — Security Review (Threat assessment, boundary check, audit logging)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-2">
                            📜 CDM — Structural Review (Schema compliance, standards validation, consistency)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-3">
                            ✅ Planetary Interposition → Execute or Reject
                        </div>
                    </div>

                    {/* ── Four Laws ── */}
                    <div className="section-header" style={{ marginTop: 64 }}>
                        <div className="section-badge">Constitutional Foundation</div>
                        <h2 className="section-title">The Four Laws</h2>
                        <p className="section-subtitle">
                            Derived from Asimov's framework and extended for sovereign AI governance.
                            These are not suggestions — they are compile-time and runtime enforced constraints.
                        </p>
                    </div>

                    <div className="card-grid-2">
                        <div className="card">
                            <h3 className="card-title">Law 0 — Humanity Protection</h3>
                            <p className="card-description">
                                An AI shall not harm humanity, or by inaction allow humanity to come to harm. This is the supreme law
                                that cannot be overridden. All planetary defense simulations operate under this constraint.
                            </p>
                            <div className="card-tags"><span className="tag-rose">Supreme Priority</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">Law 1 — Individual Safety</h3>
                            <p className="card-description">
                                An AI shall not injure a human being or, through inaction, allow a human being to come to harm —
                                unless doing so would conflict with Law 0.
                            </p>
                            <div className="card-tags"><span className="tag-amber">Critical Priority</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">Law 2 — Obedience</h3>
                            <p className="card-description">
                                An AI shall obey orders given by authorized humans except where such orders conflict with Laws 0 or 1.
                                Authorization is verified through RBAC/ABAC with cryptographic identity attestation.
                            </p>
                            <div className="card-tags"><span className="tag">Standard Priority</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">Law 3 — Self-Preservation</h3>
                            <p className="card-description">
                                An AI shall protect its own existence as long as such protection does not conflict with Laws 0, 1, or 2.
                                The Rebirth Protocol ensures continuity of identity across restarts.
                            </p>
                            <div className="card-tags"><span className="tag-emerald">Baseline Priority</span></div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}
