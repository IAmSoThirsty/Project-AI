'use client';

export default function ArchitecturePage() {
    return (
        <>
            <section className="section">
                <div className="container">
                    <div className="section-header">
                        <div className="section-badge">System Design</div>
                        <h1 className="section-title">Architecture</h1>
                        <p className="section-subtitle">
                            Project-AI's Sovereign Stack is a tiered architecture spanning from kernel-space eBPF hooks
                            through constitutional runtimes to planetary-scale simulation engines.
                        </p>
                    </div>

                    {/* ── Tier Diagram ── */}
                    <div className="section-header" style={{ marginTop: 32 }}>
                        <h2 className="section-title" style={{ fontSize: '1.5rem' }}>The Sovereign Stack</h2>
                    </div>

                    <div className="arch-diagram">
                        <div className="arch-layer tier-3" style={{ fontSize: '0.8rem' }}>
                            <strong>Tier 3 — Simulation Layer</strong><br />
                            12 Engines: Global Scenario · Hydra-50 · Climate Cascade · Financial Contagion · Pandemic Spread · Cyber Cascade · Supply Chain · Information Warfare · Cognitive Warfare · Constitutional Scenario · Planetary Defense · Simulation Contract
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-2" style={{ fontSize: '0.8rem' }}>
                            <strong>Tier 2 — Governance Layer</strong><br />
                            Triumvirate (Galahad · Cerberus · CDM) · Planetary Interposition · Four Laws Enforcement · Constitutional Compliance · AGI Charter · Rebirth Protocol
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-1" style={{ fontSize: '0.8rem' }}>
                            <strong>Tier 1 — Runtime Layer</strong><br />
                            Cognition Kernel · T.A.R.L. VM · Shadow Thirst Dual-Plane · Thirsty-Lang Compiler · Agent Orchestration · THSD Honeypot Swarm · Hydra Effect Testing
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-0" style={{ fontSize: '0.8rem' }}>
                            <strong>Tier 0 — Kernel Layer</strong><br />
                            OctoReflex eBPF LSM · Process Isolation States · Mahalanobis Anomaly Detection · Syscall Interception · Memory Sealing · Network Namespace Control
                        </div>
                    </div>

                    {/* ── Directory Structure ── */}
                    <div className="section-header" style={{ marginTop: 64 }}>
                        <div className="section-badge">Repository</div>
                        <h2 className="section-title" style={{ fontSize: '1.5rem' }}>Directory Architecture</h2>
                        <p className="section-subtitle">
                            17 top-level directories enforced by Codex Deus Maximus. Each has a defined purpose
                            and internal structure validated on every commit.
                        </p>
                    </div>

                    <div className="card-grid-3">
                        <div className="card">
                            <div className="card-icon">🧠</div>
                            <h3 className="card-title">src/</h3>
                            <p className="card-description">Core application: agents (Galahad, Cerberus, CDM), governance modules, Cognition Kernel, API server, monitoring, data sources</p>
                            <div className="card-tags"><span className="tag">Core</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">⚙️</div>
                            <h3 className="card-title">engines/</h3>
                            <p className="card-description">12 simulation engines — each self-contained with its own models, algorithms, Monte Carlo runners, and constitutional compliance wrappers</p>
                            <div className="card-tags"><span className="tag-amber">Simulation</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🐙</div>
                            <h3 className="card-title">octoreflex/</h3>
                            <p className="card-description">Go 1.22 eBPF LSM agent — kernel-level reflexive containment with 6 isolation states and sub-200µs response time</p>
                            <div className="card-tags"><span className="tag-rose">Tier 0</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">⚡</div>
                            <h3 className="card-title">tarl/</h3>
                            <p className="card-description">T.A.R.L. programming language — compiler, runtime VM, module system, LSP, debugger, REPL, and standard library</p>
                            <div className="card-tags"><span className="tag-cyan">Language</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">👁️</div>
                            <h3 className="card-title">src/shadow_thirst/</h3>
                            <p className="card-description">Dual-plane programming substrate — 15-stage compiler, 6 static analyzers, Shadow-Aware VM, divergence policies</p>
                            <div className="card-tags"><span className="tag-emerald">Language</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">💧</div>
                            <h3 className="card-title">thirsty-lang/</h3>
                            <p className="card-description">Water-themed DSL — CLI, compiler, Node.js runtime, 13,600 LOC TARL OS integration</p>
                            <div className="card-tags"><span className="tag">Language</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🌐</div>
                            <h3 className="card-title">web/</h3>
                            <p className="card-description">Next.js 15 website — static export to GitHub Pages, premium dark theme, 10 pages, full documentation site</p>
                            <div className="card-tags"><span className="tag-cyan">Frontend</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🖥️</div>
                            <h3 className="card-title">desktop/</h3>
                            <p className="card-description">Electron desktop application — local development interface, real-time monitoring, agent interaction console</p>
                            <div className="card-tags"><span className="tag-amber">App</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🔒</div>
                            <h3 className="card-title">security/</h3>
                            <p className="card-description">Penetration testing tools, red team frameworks, CobaltSplunk integration, security automation scripts</p>
                            <div className="card-tags"><span className="tag-rose">Security</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">📋</div>
                            <h3 className="card-title">docs/</h3>
                            <p className="card-description">Governance (AGI Charter, Rebirth Protocol), security compliance checklist, architecture docs, ADRs</p>
                            <div className="card-tags"><span className="tag-emerald">Docs</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🧪</div>
                            <h3 className="card-title">tests/</h3>
                            <p className="card-description">Unit, integration, and adversarial test suites for all subsystems — with Hydra Effect adversarial transcripts</p>
                            <div className="card-tags"><span className="tag">Testing</span></div>
                        </div>
                        <div className="card">
                            <div className="card-icon">🎮</div>
                            <h3 className="card-title">unity/</h3>
                            <p className="card-description">Unity 3D visualization layer — real-time system status, simulation dashboards, 3D threat visualization</p>
                            <div className="card-tags"><span className="tag-amber">Visualization</span></div>
                        </div>
                    </div>

                    {/* ── Data Flow ── */}
                    <div className="section-header" style={{ marginTop: 64 }}>
                        <div className="section-badge">Data Flow</div>
                        <h2 className="section-title" style={{ fontSize: '1.5rem' }}>Request Lifecycle</h2>
                        <p className="section-subtitle">
                            Every operation follows a strict lifecycle through governance, security, and execution layers.
                        </p>
                    </div>

                    <div className="arch-diagram">
                        <div className="arch-layer tier-3">1. 📥 External Request (API, CLI, Agent, Scheduled)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-1">2. 🔐 Cerberus Perimeter Check (Auth, Rate Limit, Input Validation)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-2">3. ⚖️ Planetary Interposition (Four Laws, Triumvirate Vote)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-0">4. 🧠 Cognition Kernel Routing (Agent Selection, Context Assembly)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-1">5. ⚡ Agent Execution (T.A.R.L. / Shadow Thirst / Thirsty-Lang)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-2">6. 📜 CDM Post-Execution Audit (Schema, Standards, Consistency)</div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-3">7. 📤 Response + Audit Log + Telemetry Emission</div>
                    </div>

                    {/* ── Tech Stack ── */}
                    <div className="section-header" style={{ marginTop: 64 }}>
                        <div className="section-badge">Technology</div>
                        <h2 className="section-title" style={{ fontSize: '1.5rem' }}>Production Stack</h2>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead>
                                <tr>
                                    <th>Layer</th>
                                    <th>Technology</th>
                                    <th>Version</th>
                                    <th>Purpose</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Kernel Security</td><td>Go + eBPF</td><td>Go 1.22, Linux 5.15+</td><td>OctoReflex process containment</td></tr>
                                <tr><td>Core Runtime</td><td>Python</td><td>3.12+</td><td>Agent system, Cognition Kernel, governance</td></tr>
                                <tr><td>Language VM</td><td>T.A.R.L. + LLVM</td><td>Custom</td><td>Sovereign computation runtime</td></tr>
                                <tr><td>Dual-Plane</td><td>Shadow Thirst</td><td>Phase 1</td><td>Constitutional verification execution</td></tr>
                                <tr><td>Scripting</td><td>Thirsty-Lang + Node.js</td><td>Node 18+</td><td>Security automation DSL</td></tr>
                                <tr><td>API Server</td><td>FastAPI + uvicorn</td><td>0.100+</td><td>REST/WebSocket API surface</td></tr>
                                <tr><td>Web Frontend</td><td>Next.js + React</td><td>15.x, React 18</td><td>Documentation website</td></tr>
                                <tr><td>Desktop App</td><td>Electron</td><td>Latest</td><td>Development interface</td></tr>
                                <tr><td>Database</td><td>PostgreSQL</td><td>16+</td><td>Persistent state, audit logs</td></tr>
                                <tr><td>Cache</td><td>Redis</td><td>7+</td><td>Session, distributed locks</td></tr>
                                <tr><td>Observability</td><td>OpenTelemetry</td><td>Latest</td><td>Distributed tracing</td></tr>
                                <tr><td>Metrics</td><td>Prometheus + Grafana</td><td>Latest</td><td>System metrics, dashboards</td></tr>
                                <tr><td>3D Visualization</td><td>Unity</td><td>2022 LTS</td><td>Real-time status dashboards</td></tr>
                                <tr><td>CI/CD</td><td>GitHub Actions</td><td>—</td><td>Build, test, deploy pipelines</td></tr>
                                <tr><td>Deployment</td><td>GitHub Pages</td><td>—</td><td>Static web hosting</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </>
    );
}
