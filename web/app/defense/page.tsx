'use client';

export default function DefensePage() {
    return (
        <>
            <section className="section">
                <div className="container">
                    <div className="section-header">
                        <div className="section-badge">Security Infrastructure</div>
                        <h1 className="section-title">Defense Systems</h1>
                        <p className="section-subtitle">
                            Three interconnected defense systems provide security coverage from kernel-space
                            to the network perimeter — with sub-200µs containment latency for critical threats.
                        </p>
                    </div>

                    {/* ── OctoReflex ── */}
                    <div className="feature-card fade-in" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon cyan">🐙</div>
                            <div>
                                <h2 className="feature-card-title">OctoReflex</h2>
                                <div className="feature-card-sub">eBPF LSM Kernel-Level Reflexive Containment · Go 1.22</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                OctoReflex is not a traditional EDR or antivirus — it operates at the Linux kernel level using eBPF
                                LSM (Linux Security Module) hooks to enforce process isolation policies in kernel-space, before malicious
                                actions can reach userland. Written in Go 1.22, it achieves containment decisions in under 200 microseconds.
                            </p>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Six Isolation States</h4>
                            <p>Every monitored process exists in one of six states, with transitions driven by behavioral anomaly scoring:</p>
                            <ul>
                                <li><strong style={{ color: 'var(--emerald-400)' }}>NORMAL</strong> — Full capabilities. Baseline behavioral profile is being established and monitored</li>
                                <li><strong style={{ color: 'var(--cyan-400)' }}>PRESSURE</strong> — Elevated monitoring. Anomaly score exceeds threshold 1. Syscall rate limiting applied</li>
                                <li><strong style={{ color: 'var(--amber-400)' }}>ISOLATED</strong> — Network access revoked. Process restricted to read-only filesystem access. IPC blocked</li>
                                <li><strong style={{ color: 'var(--amber-400)' }}>FROZEN</strong> — Process suspended via SIGSTOP. Memory snapshot captured for forensic analysis</li>
                                <li><strong style={{ color: 'var(--rose-400)' }}>QUARANTINED</strong> — Process moved to isolated cgroup with zero network, zero filesystem, minimal CPU allocation</li>
                                <li><strong style={{ color: 'var(--rose-400)' }}>TERMINATED</strong> — Process killed with SIGKILL. All child processes terminated. Post-mortem artifacts preserved</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Anomaly Detection Algorithm</h4>
                            <p>
                                OctoReflex uses Mahalanobis distance scoring against a continuously updated behavioral baseline.
                                The algorithm computes the statistical distance of current process behavior from observed normal patterns
                                across multiple dimensions: syscall frequency vector, memory allocation patterns, file access patterns,
                                network connection rates, and CPU utilization curves.
                            </p>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Threat Mapping</h4>
                        </div>

                        <div style={{ overflowX: 'auto', marginTop: 16 }}>
                            <table className="compliance-table">
                                <thead>
                                    <tr>
                                        <th>Attack Type</th>
                                        <th>Target State</th>
                                        <th>Enforcement Mechanism</th>
                                        <th>Latency</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td>Buffer Overflow</td><td className="status-fail">QUARANTINED</td><td>eBPF mprotect hook, memory sealing</td><td>&lt;150µs</td></tr>
                                    <tr><td>Privilege Escalation</td><td className="status-fail">TERMINATED</td><td>LSM cred_prepare hook, capability drop</td><td>&lt;100µs</td></tr>
                                    <tr><td>Lateral Movement</td><td className="status-warn">ISOLATED</td><td>Network namespace isolation, eBPF connect hook</td><td>&lt;200µs</td></tr>
                                    <tr><td>Data Exfiltration</td><td className="status-warn">FROZEN</td><td>eBPF sendmsg hook, egress rate limiting</td><td>&lt;180µs</td></tr>
                                    <tr><td>Rootkit Installation</td><td className="status-fail">TERMINATED</td><td>LSM kernel_module hook, kmod deny</td><td>&lt;80µs</td></tr>
                                    <tr><td>Cryptomining</td><td className="status-warn">PRESSURE</td><td>CPU scheduler throttling, cgroup limits</td><td>&lt;500µs</td></tr>
                                    <tr><td>Fork Bomb</td><td className="status-fail">TERMINATED</td><td>eBPF fork hook, PID limit enforcement</td><td>&lt;50µs</td></tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="feature-card-body" style={{ marginTop: 16 }}>
                            <h4 style={{ marginBottom: 12, color: 'var(--text-primary)' }}>Deployment</h4>
                            <ul>
                                <li><strong>Kernel Requirements</strong> — Linux 5.15+ with BTF (BPF Type Format) and LSM BPF hook support</li>
                                <li><strong>Runtime</strong> — Single Go binary, ~12MB, no external dependencies. Runs as systemd service or Kubernetes DaemonSet</li>
                                <li><strong>Resource Overhead</strong> — &lt;2% CPU, &lt;50MB RSS at 10k monitored processes. Zero-copy eBPF ring buffer for event streaming</li>
                                <li><strong>Configuration</strong> — YAML policy files defining per-process or per-cgroup isolation rules, anomaly thresholds, and escalation paths</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── THSD ── */}
                    <div className="feature-card fade-in fade-in-1" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon amber">🍯</div>
                            <div>
                                <h2 className="feature-card-title">THSD</h2>
                                <div className="feature-card-sub">Thirsty's Honeypot Swarm Defense · Biological Security Model</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                THSD draws inspiration from biological immune systems — specifically, the adaptive immune response
                                and swarm intelligence patterns observed in social insects. Rather than building walls, THSD creates
                                an ecosystem of intelligent decoys that learn, adapt, and coordinate to detect, profile, and exhaust attackers.
                            </p>
                            <ul>
                                <li><strong>Honeypot Swarm Deployment</strong> — Dynamically spawns realistic decoy services (databases, APIs, file servers, admin panels) that appear as high-value targets. Each honeypot is containerized with unique fingerprints to prevent attacker pattern recognition</li>
                                <li><strong>Adaptive Decoy Generation</strong> — Machine learning pipeline analyzes attacker behavior in real-time and generates new decoys tailored to the attacker's observed techniques, tools, and objectives</li>
                                <li><strong>Attacker Profiling Engine</strong> — Builds behavioral profiles using MITRE ATT&CK framework mapping. Classifies attackers by sophistication level (script kiddie → APT) and adjusts response intensity</li>
                                <li><strong>Swarm Coordination Protocol</strong> — Honeypots communicate through an encrypted mesh network, sharing threat intelligence and coordinating lures to guide attackers through increasingly instrumented environments</li>
                                <li><strong>Resource Exhaustion Tactics</strong> — Employs tarpit techniques (intentionally slow responses), computational puzzles, and fake data streams to waste attacker time and resources</li>
                                <li><strong>Integration with Cerberus</strong> — All intelligence gathered by THSD feeds into Cerberus's threat detection pipeline, enriching the security model with real attacker TTPs</li>
                                <li><strong>Canary Token Network</strong> — Plants cryptographic canary tokens in realistic locations (config files, databases, git repos) that trigger alerts when accessed, providing early warning of breaches</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Hydra Effect ── */}
                    <div className="feature-card fade-in fade-in-2" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon rose">🐉</div>
                            <div>
                                <h2 className="feature-card-title">The Hydra Effect</h2>
                                <div className="feature-card-sub">Adversarial Resilience Framework · 62+ Transcripts</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                "Cut one head, two more grow back." The Hydra Effect is Project-AI's adversarial testing and resilience
                                framework. It systematically subjects every component to adversarial attack scenarios, stress tests, and
                                fault injection — with the explicit goal of making the system stronger through controlled failure.
                            </p>
                            <ul>
                                <li><strong>Adversarial Transcript Library</strong> — 62+ documented adversarial engagement transcripts covering prompt injection, jailbreak attempts, social engineering, logic manipulation, and context poisoning</li>
                                <li><strong>Red Team Automation</strong> — Automated adversarial agents that continuously probe the system using evolving attack scripts derived from the transcript library and latest CVE databases</li>
                                <li><strong>Stress Testing Suite</strong> — Pushes every engine to operational limits: concurrent scenario simulations, memory pressure tests, network partition tolerance, clock skew resilience, and data corruption recovery</li>
                                <li><strong>Fault Injection Engine</strong> — Controlled chaos engineering: kills random processes, injects network delays, corrupts partial data, simulates disk failures, and validates graceful degradation</li>
                                <li><strong>Resilience Scoring</strong> — Quantitative resilience metrics (MTTR, MTBF, degradation curves, recovery completeness) for every subsystem, tracked over time with regression detection</li>
                                <li><strong>Post-Mortem Pipeline</strong> — Every adversarial engagement produces a structured post-mortem: root cause, attack vector, defense effectiveness, recommended hardening, and updated threat model</li>
                                <li><strong>Hydra Regrowth Protocol</strong> — When a vulnerability is found and patched, the framework automatically generates 2+ additional test cases covering related attack surfaces — making the system provably stronger</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Defense Integration Diagram ── */}
                    <div className="section-header" style={{ marginTop: 48 }}>
                        <div className="section-badge">Integration</div>
                        <h2 className="section-title">Defense Layer Integration</h2>
                    </div>

                    <div className="arch-diagram">
                        <div className="arch-layer tier-0">
                            🐙 OctoReflex — Kernel Space (eBPF LSM hooks, &lt;200µs containment)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-1">
                            🐕 Cerberus — Runtime Boundary (Process isolation, network control, audit)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-2">
                            🍯 THSD — Network Perimeter (Honeypot swarms, decoy generation, attacker profiling)
                        </div>
                        <div className="arch-connector" />
                        <div className="arch-layer tier-3">
                            🐉 Hydra Effect — Continuous Testing (Adversarial probing, fault injection, resilience scoring)
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}
