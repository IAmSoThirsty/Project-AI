'use client';

export default function LicensesPage() {
    return (
        <section className="section">
            <div className="container-narrow">
                <div className="section-header">
                    <div className="section-badge">Legal</div>
                    <h1 className="section-title">Licenses</h1>
                    <p className="section-subtitle">
                        Project-AI is open source. Every component, dependency, and artifact is transparently licensed.
                    </p>
                </div>

                {/* Project-AI MIT */}
                <div className="feature-card" style={{ marginBottom: 32 }}>
                    <div className="feature-card-header">
                        <div className="feature-card-icon violet">📄</div>
                        <div>
                            <h2 className="feature-card-title">Project-AI</h2>
                            <div className="feature-card-sub">MIT License · Copyright © 2025 Project AI Team</div>
                        </div>
                    </div>
                    <div className="code-block" style={{ fontSize: '0.78rem', lineHeight: 1.7 }}>
                        {`MIT License

Copyright (c) 2025 Project AI Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`}
                    </div>
                </div>

                {/* OctoReflex Apache 2.0 */}
                <div className="feature-card" style={{ marginBottom: 32 }}>
                    <div className="feature-card-header">
                        <div className="feature-card-icon cyan">🐙</div>
                        <div>
                            <h2 className="feature-card-title">OctoReflex</h2>
                            <div className="feature-card-sub">Apache License 2.0</div>
                        </div>
                    </div>
                    <div className="feature-card-body">
                        <p>
                            OctoReflex is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at{' '}
                            <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank" rel="noopener noreferrer">
                                apache.org/licenses/LICENSE-2.0
                            </a>.
                        </p>
                        <p style={{ marginTop: 12 }}>
                            Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
                            on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                        </p>
                    </div>
                </div>

                {/* Key Dependencies */}
                <div style={{ marginBottom: 32 }}>
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>📦 Key Dependency Licenses</h2>
                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead><tr><th>Package</th><th>Version</th><th>License</th><th>Purpose</th></tr></thead>
                            <tbody>
                                <tr><td>Next.js</td><td>15.x</td><td>MIT</td><td>Web framework</td></tr>
                                <tr><td>React</td><td>18.x</td><td>MIT</td><td>UI library</td></tr>
                                <tr><td>Python</td><td>3.12+</td><td>PSF</td><td>Core runtime</td></tr>
                                <tr><td>FastAPI</td><td>0.100+</td><td>MIT</td><td>API server</td></tr>
                                <tr><td>uvicorn</td><td>0.24+</td><td>BSD-3</td><td>ASGI server</td></tr>
                                <tr><td>Go</td><td>1.22</td><td>BSD-3</td><td>OctoReflex agent</td></tr>
                                <tr><td>cilium/ebpf</td><td>0.12+</td><td>MIT</td><td>eBPF library</td></tr>
                                <tr><td>PostgreSQL</td><td>16+</td><td>PostgreSQL</td><td>Database</td></tr>
                                <tr><td>Redis</td><td>7+</td><td>BSD-3</td><td>Cache & locks</td></tr>
                                <tr><td>OpenTelemetry</td><td>Latest</td><td>Apache-2.0</td><td>Observability</td></tr>
                                <tr><td>Prometheus</td><td>Latest</td><td>Apache-2.0</td><td>Metrics</td></tr>
                                <tr><td>LLVM</td><td>17+</td><td>Apache-2.0</td><td>T.A.R.L. JIT backend</td></tr>
                                <tr><td>TypeScript</td><td>5.x</td><td>Apache-2.0</td><td>Web type checking</td></tr>
                                <tr><td>Electron</td><td>Latest</td><td>MIT</td><td>Desktop app</td></tr>
                                <tr><td>Unity</td><td>2022 LTS</td><td>Unity EULA</td><td>3D visualization</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* License Compliance */}
                <div className="feature-card">
                    <div className="feature-card-header">
                        <div className="feature-card-icon emerald">✅</div>
                        <div>
                            <h2 className="feature-card-title">Compliance Statement</h2>
                            <div className="feature-card-sub">Automated license verification</div>
                        </div>
                    </div>
                    <div className="feature-card-body">
                        <ul>
                            <li><strong>SBOM Generation</strong> — CycloneDX Software Bill of Materials generated on every build, capturing all transitive dependencies and their licenses</li>
                            <li><strong>License Compatibility</strong> — All dependencies verified compatible with MIT. No GPL contamination. No proprietary dependencies in core path</li>
                            <li><strong>Artifact Signing</strong> — Release artifacts signed with Sigstore Cosign for supply chain integrity verification</li>
                            <li><strong>Attribution</strong> — All third-party notices are maintained in THIRD_PARTY_NOTICES.md with proper attribution as required by respective licenses</li>
                            <li><strong>Continuous Auditing</strong> — CI pipeline runs license-checker on every PR to prevent introduction of incompatible licenses</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    );
}
