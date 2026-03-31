'use client';

export default function CompliancePage() {
    return (
        <section className="section">
            <div className="container">
                <div className="section-header">
                    <div className="section-badge">Security & Regulatory</div>
                    <h1 className="section-title">Compliance</h1>
                    <p className="section-subtitle">
                        Project-AI's compliance posture across industry security frameworks, data protection regulations,
                        and AI governance standards.
                    </p>
                </div>

                {/* OWASP Top 10 */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>🛡️ OWASP Top 10 (2021)</h2>
                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead><tr><th>ID</th><th>Vulnerability</th><th>Status</th><th>Implementation</th></tr></thead>
                            <tbody>
                                <tr><td>A01</td><td>Broken Access Control</td><td className="status-pass">✓ PASS</td><td>RBAC/ABAC via Cerberus. Planetary Interposition gate. Cryptographic identity attestation.</td></tr>
                                <tr><td>A02</td><td>Cryptographic Failures</td><td className="status-pass">✓ PASS</td><td>AES-256-GCM/ChaCha20-Poly1305 at rest. TLS 1.3 in transit. KMS key rotation. No weak ciphers.</td></tr>
                                <tr><td>A03</td><td>Injection</td><td className="status-pass">✓ PASS</td><td>Thirsty-Lang sanitize() for XSS/SQLi/RCE. Parameterized queries. Input validation at every boundary.</td></tr>
                                <tr><td>A04</td><td>Insecure Design</td><td className="status-pass">✓ PASS</td><td>Constitutional governance by design. Threat modeling per STRIDE. Adversarial testing via Hydra Effect.</td></tr>
                                <tr><td>A05</td><td>Security Misconfiguration</td><td className="status-pass">✓ PASS</td><td>CDM enforces config schema validation. No default credentials. Hardened deployment templates.</td></tr>
                                <tr><td>A06</td><td>Vulnerable Components</td><td className="status-pass">✓ PASS</td><td>CycloneDX SBOM generation. pip-audit + npm audit in CI. Sigstore Cosign artifact signing.</td></tr>
                                <tr><td>A07</td><td>Auth Failures</td><td className="status-pass">✓ PASS</td><td>OIDC/OAuth2.0. API key rotation. Session management with Redis. MFA for admin operations.</td></tr>
                                <tr><td>A08</td><td>Data Integrity Failures</td><td className="status-pass">✓ PASS</td><td>Merkle tree audit log. Cryptographic signing of all artifacts. Supply chain verification.</td></tr>
                                <tr><td>A09</td><td>Logging Failures</td><td className="status-pass">✓ PASS</td><td>OpenTelemetry tracing. Structured JSON logging. Append-only audit trail. Prometheus metrics.</td></tr>
                                <tr><td>A10</td><td>SSRF</td><td className="status-pass">✓ PASS</td><td>Egress filtering via OctoReflex eBPF hooks. Network namespace isolation. URL allowlisting.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* GDPR */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>🇪🇺 GDPR Compliance</h2>
                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead><tr><th>Article</th><th>Requirement</th><th>Status</th><th>Implementation</th></tr></thead>
                            <tbody>
                                <tr><td>Art. 5</td><td>Data Processing Principles</td><td className="status-pass">✓</td><td>Purpose limitation enforced. Data minimization in all pipelines. Storage limitation policies.</td></tr>
                                <tr><td>Art. 6</td><td>Lawful Basis</td><td className="status-pass">✓</td><td>Consent management. Legitimate interest assessments. Contract basis documentation.</td></tr>
                                <tr><td>Art. 13-14</td><td>Right to Information</td><td className="status-pass">✓</td><td>Transparency through Galahad's reporting. Privacy policy auto-generation.</td></tr>
                                <tr><td>Art. 17</td><td>Right to Erasure</td><td className="status-pass">✓</td><td>Thirsty-Lang evaporate() for cryptographic erasure. Cascade deletion with referential tracking.</td></tr>
                                <tr><td>Art. 25</td><td>Privacy by Design</td><td className="status-pass">✓</td><td>Constitutional enforcement at compile-time. Shadow Thirst privacy plane verification.</td></tr>
                                <tr><td>Art. 32</td><td>Security of Processing</td><td className="status-pass">✓</td><td>Encryption at rest/transit. OctoReflex kernel hardening. Cerberus runtime security.</td></tr>
                                <tr><td>Art. 33-34</td><td>Breach Notification</td><td className="status-pass">✓</td><td>Automated incident detection with &lt;72h notification pipeline. Cerberus alert escalation.</td></tr>
                                <tr><td>Art. 35</td><td>DPIA</td><td className="status-pass">✓</td><td>Automated Data Protection Impact Assessments for new data processing operations.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* CCPA */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>🇺🇸 CCPA Compliance</h2>
                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead><tr><th>Section</th><th>Requirement</th><th>Status</th><th>Implementation</th></tr></thead>
                            <tbody>
                                <tr><td>§1798.100</td><td>Right to Know</td><td className="status-pass">✓</td><td>Data inventory API. Automated disclosure generation. Category-level and specific-piece reporting.</td></tr>
                                <tr><td>§1798.105</td><td>Right to Delete</td><td className="status-pass">✓</td><td>Verified deletion pipeline. Cryptographic erasure. Third-party cascade notifications.</td></tr>
                                <tr><td>§1798.110</td><td>Right to Data Portability</td><td className="status-pass">✓</td><td>Machine-readable export (JSON/CSV). Automated transfer protocol.</td></tr>
                                <tr><td>§1798.120</td><td>Right to Opt-Out</td><td className="status-pass">✓</td><td>Do Not Sell signal processing. Global Privacy Control (GPC) header support.</td></tr>
                                <tr><td>§1798.125</td><td>Non-Discrimination</td><td className="status-pass">✓</td><td>Galahad ethical review prevents service degradation based on rights exercise.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* NIST AI RMF */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>🤖 NIST AI Risk Management Framework 1.0</h2>
                    <div className="card-grid-2">
                        <div className="card">
                            <h3 className="card-title">GOVERN</h3>
                            <p className="card-description">Triumvirate governance structure with clear roles and accountability. AGI Charter defines policies. Four Laws provide enforceable constraints. Multi-party review for all changes.</p>
                            <div className="card-tags"><span className="tag-emerald">Implemented</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">MAP</h3>
                            <p className="card-description">Risk domains mapped across 12 simulation engines. Stakeholder impact modeling via Galahad. STRIDE threat modeling per component. Attack surface enumeration via Hydra Effect.</p>
                            <div className="card-tags"><span className="tag-emerald">Implemented</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">MEASURE</h3>
                            <p className="card-description">Continuous metrics via Prometheus/Grafana. Resilience scoring (MTTR, MTBF). Anomaly detection baselines (OctoReflex). Constitutional compliance rate tracking.</p>
                            <div className="card-tags"><span className="tag-emerald">Implemented</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">MANAGE</h3>
                            <p className="card-description">Graduated lockdown protocols (ADVISORY→TOTAL_LOCKDOWN). Incident response pipeline. Rollback/roll-forward strategies. Disaster recovery. Blue-green deployment.</p>
                            <div className="card-tags"><span className="tag-emerald">Implemented</span></div>
                        </div>
                    </div>
                </div>

                {/* Security Testing */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>🧪 Security Testing Methodology</h2>
                    <div className="card-grid-3">
                        <div className="card">
                            <div className="card-icon">🔍</div>
                            <h3 className="card-title">Static Analysis</h3>
                            <p className="card-description">Bandit (Python security), Semgrep (multi-language patterns), Ruff (fast linting), pip-audit (dependency vulnerabilities), npm audit (JS dependencies)</p>
                        </div>
                        <div className="card">
                            <div className="card-icon">⚡</div>
                            <h3 className="card-title">Dynamic Analysis</h3>
                            <p className="card-description">Hydra Effect adversarial probing. Fault injection engine. Chaos engineering (process kills, network partitions, disk failures). Load testing.</p>
                        </div>
                        <div className="card">
                            <div className="card-icon">🔴</div>
                            <h3 className="card-title">Red Team</h3>
                            <p className="card-description">62+ adversarial transcripts. Automated attack scripts from CVE databases. CobaltSplunk integration. Prompt injection testing. Social engineering simulations.</p>
                        </div>
                    </div>
                </div>

                {/* Supply Chain */}
                <div style={{ marginBottom: 48 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>📦 Supply Chain Security</h2>
                    <div className="card-grid-2">
                        <div className="card">
                            <h3 className="card-title">SBOM Generation</h3>
                            <p className="card-description">CycloneDX format. Automated generation in CI/CD. Full dependency tree with transitive dependencies. License compliance verification.</p>
                            <div className="card-tags"><span className="tag-cyan">CycloneDX</span></div>
                        </div>
                        <div className="card">
                            <h3 className="card-title">Artifact Signing</h3>
                            <p className="card-description">Sigstore Cosign for container and artifact signing. Keyless signing with OIDC identity. Transparency log for public verification.</p>
                            <div className="card-tags"><span className="tag">Sigstore</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
