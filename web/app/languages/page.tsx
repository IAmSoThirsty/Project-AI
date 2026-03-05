'use client';

export default function LanguagesPage() {
    return (
        <>
            <section className="section">
                <div className="container">
                    <div className="section-header">
                        <div className="section-badge">Programming Systems</div>
                        <h1 className="section-title">Languages & Runtimes</h1>
                        <p className="section-subtitle">
                            Three purpose-built programming systems — each addressing a different computational need, from
                            rapid prototyping to constitutionally-bound dual-plane execution.
                        </p>
                    </div>

                    {/* ── Thirsty-Lang ── */}
                    <div className="feature-card fade-in" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon violet">💧</div>
                            <div>
                                <h2 className="feature-card-title">Thirsty-Lang</h2>
                                <div className="feature-card-sub">Water-Themed Programming Language · Node.js Runtime · 13,600 LOC</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                Thirsty-Lang is a domain-specific programming language built for Project-AI's operational scripting
                                and security automation. Its water-themed syntax makes security operations intuitive and readable,
                                while the compiler enforces safety invariants at parse time.
                            </p>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Core Keywords</h4>

                            <div className="code-block" style={{ marginBottom: 16 }}>
                                <span className="cm">{'// Thirsty-Lang sample — security-first data processing'}</span>{'\n'}
                                <span className="kw">pour</span> data <span className="op">=</span> <span className="fn">fetch_stream</span>(<span className="str">"sensor://octoreflex/events"</span>){'\n'}
                                <span className="kw">filter</span> data <span className="kw">through</span> <span className="fn">sanitize</span>(<span className="str">"xss"</span>, <span className="str">"sqli"</span>, <span className="str">"rce"</span>){'\n'}
                                <span className="kw">shield</span> data <span className="kw">with</span> <span className="fn">armor</span>(<span className="str">"AES-256-GCM"</span>){'\n'}
                                <span className="kw">drink</span> data <span className="kw">into</span> <span className="fn">cerberus_pipeline</span>(){'\n'}
                                {'\n'}
                                <span className="cm">{'// Conditional flow — water metaphors'}</span>{'\n'}
                                <span className="kw">if</span> data.<span className="fn">is_contaminated</span>() {'{'}{'\n'}
                                {'  '}<span className="kw">evaporate</span> data  <span className="cm">{'// safe destruction'}</span>{'\n'}
                                {'  '}<span className="fn">alert</span>(<span className="str">"Cerberus"</span>, <span className="str">"contamination_detected"</span>){'\n'}
                                {'}'} <span className="kw">else</span> {'{'}{'\n'}
                                {'  '}<span className="kw">flow</span> data <span className="kw">to</span> <span className="fn">storage</span>(<span className="str">"encrypted_lake"</span>){'\n'}
                                {'}'}
                            </div>

                            <ul>
                                <li><strong>pour</strong> — Variable declaration and data stream initialization</li>
                                <li><strong>drink</strong> — Data consumption and pipeline ingestion</li>
                                <li><strong>shield / armor</strong> — Encryption and security wrapping primitives</li>
                                <li><strong>sanitize</strong> — Input validation and sanitization (XSS, SQLi, RCE, SSRF)</li>
                                <li><strong>filter through</strong> — Data transformation pipeline with chained processors</li>
                                <li><strong>evaporate</strong> — Secure data destruction with cryptographic erasure</li>
                                <li><strong>flow to</strong> — Data routing to storage backends or processing endpoints</li>
                                <li><strong>freeze / thaw</strong> — Immutable snapshot creation and restoration</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Architecture</h4>
                            <ul>
                                <li><strong>CLI</strong> — Custom command-line interface for REPL, file compilation, and project management</li>
                                <li><strong>Compiler</strong> — Tokenizer → AST → Semantic Analysis → Code Generation targeting Node.js runtime</li>
                                <li><strong>Runtime</strong> — Node.js-based execution environment with security sandboxing</li>
                                <li><strong>TARL OS Integration</strong> — 13,600 LOC codebase used across the T.A.R.L. operating system layer</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── T.A.R.L. ── */}
                    <div className="feature-card fade-in fade-in-1" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon cyan">⚡</div>
                            <div>
                                <h2 className="feature-card-title">T.A.R.L.</h2>
                                <div className="feature-card-sub">Thirsty's Active Resistance Language · Full Programming Language · 8 Subsystems</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                T.A.R.L. is a complete, monolithic, production-grade programming language designed for sovereign
                                computation. Unlike Thirsty-Lang (which is a DSL for scripting), T.A.R.L. is a full-featured
                                language with its own compiler, runtime VM, module system, LSP, debugger, and REPL.
                            </p>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Eight Subsystems</h4>
                            <ul>
                                <li><strong>Configuration Management</strong> — Hierarchical config system with environment-aware overrides, feature flags, and schema validation. Uses <code>TarlConfig</code> definite types with compile-time defaults</li>
                                <li><strong>Diagnostics Engine</strong> — Rich error reporting with source spans, multi-span notes, fix suggestions, and severity levels. Emits LSP-compatible diagnostics for IDE integration</li>
                                <li><strong>Standard Library</strong> — Collections, I/O, cryptography, networking, serialization (JSON/CBOR/MessagePack), math, date/time, and concurrency primitives</li>
                                <li><strong>FFI Bridge</strong> — Foreign Function Interface for C, Rust, and Python interop. Includes automatic memory management across boundaries, type marshaling, and security sandboxing for untrusted FFI targets</li>
                                <li><strong>Compiler Frontend</strong> — Lexer → Parser (recursive descent) → AST → Type Checker → HIR → MIR → LIR → Bytecode/native. Supports incremental compilation and cached dependency resolution</li>
                                <li><strong>Runtime VM</strong> — Register-based virtual machine with JIT compilation (LLVM backend), garbage collection (generational, concurrent mark-sweep), and hot-reload for development</li>
                                <li><strong>Module System</strong> — Content-addressed module resolution with cryptographic integrity verification. Supports semantic versioning, diamond dependency resolution, and namespace isolation</li>
                                <li><strong>Development Tooling</strong> — Language Server Protocol (LSP) implementation, step-through debugger, profiler, REPL, formatter (tarlFmt), linter (tarlLint), and package manager (tarlPkg)</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Security Model</h4>
                            <ul>
                                <li><strong>Sandboxing</strong> — Every module runs in a capability-based sandbox. File system, network, and system call access must be explicitly granted through manifests</li>
                                <li><strong>FFI Security</strong> — All foreign calls pass through a security shim that validates parameters, enforces return type contracts, and prevents memory corruption leaks</li>
                                <li><strong>Runtime Security</strong> — Memory-safe by default. Stack overflow protection, integer overflow detection, bounds checking, and use-after-free prevention</li>
                                <li><strong>Cerberus Integration</strong> — Runtime events feed into Cerberus's threat detection pipeline for behavioral anomaly detection</li>
                                <li><strong>Codex Deus Maximus Integration</strong> — Source code is validated against structural standards before compilation proceeds</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Initialization Sequence</h4>
                            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                The strict initialization order prevents circular dependencies and ensures each subsystem has its
                                prerequisites satisfied before activation:
                            </p>
                            <div className="code-block" style={{ marginTop: 12 }}>
                                <span className="cm">{'// T.A.R.L. Cold Start Sequence (strict order)'}</span>{'\n'}
                                <span className="num">1.</span> <span className="ty">ConfigManager</span>.<span className="fn">init</span>()      <span className="cm">{'// Load config from env + files'}</span>{'\n'}
                                <span className="num">2.</span> <span className="ty">DiagnosticsEngine</span>.<span className="fn">init</span>() <span className="cm">{'// Error reporting infrastructure'}</span>{'\n'}
                                <span className="num">3.</span> <span className="ty">StdLib</span>.<span className="fn">register</span>()        <span className="cm">{'// Register built-in types + functions'}</span>{'\n'}
                                <span className="num">4.</span> <span className="ty">FFIBridge</span>.<span className="fn">init</span>()         <span className="cm">{'// Load native libraries + security shims'}</span>{'\n'}
                                <span className="num">5.</span> <span className="ty">Compiler</span>.<span className="fn">init</span>()          <span className="cm">{'// Lexer, parser, type checker ready'}</span>{'\n'}
                                <span className="num">6.</span> <span className="ty">RuntimeVM</span>.<span className="fn">init</span>()         <span className="cm">{'// VM + JIT + GC threads'}</span>{'\n'}
                                <span className="num">7.</span> <span className="ty">ModuleSystem</span>.<span className="fn">init</span>()      <span className="cm">{'// Resolve dependencies, verify signatures'}</span>{'\n'}
                                <span className="num">8.</span> <span className="ty">DevTools</span>.<span className="fn">init</span>()          <span className="cm">{'// LSP, debugger, REPL (dev mode only)'}</span>
                            </div>
                        </div>
                    </div>

                    {/* ── Shadow Thirst ── */}
                    <div className="feature-card fade-in fade-in-2" style={{ marginBottom: 32 }}>
                        <div className="feature-card-header">
                            <div className="feature-card-icon emerald">👁️</div>
                            <div>
                                <h2 className="feature-card-title">Shadow Thirst</h2>
                                <div className="feature-card-sub">Constitutionally-Bound Dual-Plane Programming Substrate · 4,800 LOC</div>
                            </div>
                        </div>
                        <div className="feature-card-body">
                            <p>
                                Shadow Thirst represents the cutting edge of constitutional computation — a programming substrate
                                where code executes simultaneously on two planes (Primary and Shadow), with compiler-enforced
                                separation guarantees. When the planes diverge, constitutional policies determine the outcome.
                            </p>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Dual-Plane Architecture</h4>
                            <ul>
                                <li><strong>Primary Plane</strong> — Standard execution context. Handles all normal computation, state mutations, and I/O operations</li>
                                <li><strong>Shadow Plane</strong> — Constitutional verification context. Mirrors primary execution and independently verifies invariants, correctness constraints, and governance compliance</li>
                                <li><strong>Invariant Plane</strong> — Read-only reference plane containing constitutional axioms. Neither Primary nor Shadow can mutate this plane — it serves as the ground truth</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Memory Qualifiers</h4>
                            <div className="code-block" style={{ marginBottom: 16 }}>
                                <span className="cm">{'// Shadow Thirst memory qualifier system'}</span>{'\n'}
                                <span className="kw">canonical</span> <span className="ty">int</span> balance <span className="op">=</span> <span className="num">1000</span>;  <span className="cm">{'// Exists on both planes, synced'}</span>{'\n'}
                                <span className="kw">shadow</span>    <span className="ty">int</span> audit   <span className="op">=</span> <span className="num">0</span>;     <span className="cm">{'// Shadow plane only — verification'}</span>{'\n'}
                                <span className="kw">ephemeral</span> <span className="ty">int</span> temp    <span className="op">=</span> <span className="num">0</span>;     <span className="cm">{'// Garbage collected per-frame'}</span>{'\n'}
                                <span className="kw">dual</span>      <span className="ty">int</span> shared  <span className="op">=</span> <span className="num">0</span>;     <span className="cm">{'// Both planes, independent values'}</span>{'\n'}
                                {'\n'}
                                <span className="cm">{'// Dual-plane function: executes on both planes'}</span>{'\n'}
                                <span className="kw">dual fn</span> <span className="fn">transfer</span>(<span className="ty">Account</span> from, <span className="ty">Account</span> to, <span className="ty">int</span> amount) {'{'}{'\n'}
                                {'  '}<span className="kw">primary</span> {'{'}{'\n'}
                                {'    '}from.balance <span className="op">-=</span> amount;{'\n'}
                                {'    '}to.balance <span className="op">+=</span> amount;{'\n'}
                                {'  }'}{'\n'}
                                {'  '}<span className="kw">shadow</span> {'{'}{'\n'}
                                {'    '}<span className="cm">{'// Independent verification'}</span>{'\n'}
                                {'    '}<span className="kw">assert</span> from.balance <span className="op">{'>='}</span> <span className="num">0</span> : <span className="str">"overdraft"</span>;{'\n'}
                                {'    '}<span className="kw">assert</span> (from.balance + to.balance) <span className="op">{'=='}</span> <span className="kw">invariant</span>.total_supply : <span className="str">"conservation"</span>;{'\n'}
                                {'  }'}{'\n'}
                                {'}'}{'\n'}
                                {'\n'}
                                <span className="cm">{'// Divergence policy — when planes disagree'}</span>{'\n'}
                                <span className="kw">@divergence_policy</span>(<span className="str">"halt_and_report"</span>){'\n'}
                                <span className="kw">mutation_boundary</span> <span className="fn">critical_state_change</span>() {'{'}{'\n'}
                                {'  '}<span className="cm">{'// ... both planes must agree for this mutation to commit'}</span>{'\n'}
                                {'}'}
                            </div>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>15-Stage Compiler Pipeline</h4>
                            <ul>
                                <li><strong>Stages 1-3:</strong> Lexer → Parser → AST construction with dual-plane annotations</li>
                                <li><strong>Stages 4-6:</strong> Type checking with plane-aware type rules → Plane separation analysis → Memory qualifier validation</li>
                                <li><strong>Stages 7-9:</strong> Dual-plane IR generation → Shadow integrity verification → Divergence point analysis</li>
                                <li><strong>Stages 10-12:</strong> Optimization (per-plane) → Dead shadow code elimination → Invariant plane extraction</li>
                                <li><strong>Stages 13-15:</strong> Code generation (dual binary) → Shadow-aware linking → Runtime verification stub injection</li>
                            </ul>

                            <h4 style={{ marginTop: 24, marginBottom: 12, color: 'var(--text-primary)' }}>Six Static Analyzers</h4>
                            <ul>
                                <li><strong>Plane Leak Detector</strong> — Ensures no data flows from Shadow to Primary plane without explicit declassification</li>
                                <li><strong>Invariant Violation Checker</strong> — Statically verifies that no code path can mutate the Invariant plane</li>
                                <li><strong>Divergence Point Analyzer</strong> — Identifies all points where Primary and Shadow execution could diverge and verifies policy coverage</li>
                                <li><strong>Memory Safety Analyzer</strong> — Verifies all ephemeral allocations are reclaimed, all canonical variables are in sync, and no dual variables are read without plane disambiguation</li>
                                <li><strong>Constitutional Compliance Checker</strong> — Validates that all governance constraints from the AGI Charter are enforceable in the compiled dual binary</li>
                                <li><strong>Temporal Safety Analyzer</strong> — Verifies that mutation boundaries cannot be entered from inconsistent states and that all sync points are reachable</li>
                            </ul>
                        </div>
                    </div>

                    {/* ── Comparison ── */}
                    <div className="section-header" style={{ marginTop: 48 }}>
                        <div className="section-badge">Comparison</div>
                        <h2 className="section-title">Language Comparison</h2>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table className="compliance-table">
                            <thead>
                                <tr>
                                    <th>Property</th>
                                    <th>Thirsty-Lang</th>
                                    <th>T.A.R.L.</th>
                                    <th>Shadow Thirst</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Type</td><td>DSL</td><td>General Purpose</td><td>Substrate</td></tr>
                                <tr><td>Runtime</td><td>Node.js</td><td>Custom VM + JIT</td><td>Shadow-Aware VM</td></tr>
                                <tr><td>Compilation</td><td>Transpiled</td><td>Bytecode + Native</td><td>Dual Binary</td></tr>
                                <tr><td>Memory Model</td><td>GC (V8)</td><td>Generational GC</td><td>Plane-Qualified</td></tr>
                                <tr><td>Safety</td><td>Sanitization</td><td>Capability Sandbox</td><td>Constitutional</td></tr>
                                <tr><td>Codebase</td><td>13,600 LOC</td><td>~40,000 LOC</td><td>4,800 LOC</td></tr>
                                <tr><td>Use Case</td><td>Security Scripting</td><td>Sovereign Computation</td><td>Adversarial Resilience</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </>
    );
}
