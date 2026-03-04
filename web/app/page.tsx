/*
 * Project-AI Sovereign Web Interface
 * Status: ACTIVE [Sovereign 2.1 Hardened]
 * Last Updated: 2026-03-02 10:34
 */
'use client';

import Link from 'next/link';

const PAGES = [
  { href: '/triumvirate', icon: '⚖️', title: 'The Triumvirate', desc: 'Galahad · Cerberus · Codex Deus Maximus' },
  { href: '/defense', icon: '🛡️', title: 'Defense Systems', desc: 'OctoReflex · THSD · Hydra Effect' },
  { href: '/languages', icon: '🔤', title: 'Languages', desc: 'Thirsty-Lang · T.A.R.L. · Shadow Thirst' },
  { href: '/architecture', icon: '🏗️', title: 'Architecture', desc: 'Sovereign Stack · Tier System · Data Flow' },
  { href: '/demos', icon: '🖥️', title: 'Live Demos', desc: 'Interactive terminals · Code execution' },
  { href: '/knowledge', icon: '📖', title: 'Knowledge Base', desc: 'Everything you need to know' },
  { href: '/compliance', icon: '✅', title: 'Compliance', desc: 'OWASP · GDPR · NIST · ASL-3' },
  { href: '/licenses', icon: '📄', title: 'Licenses', desc: 'MIT · Apache 2.0 · Dependencies' },
  { href: '/changelog', icon: '📋', title: 'Changelog', desc: 'Evolution & Development Timeline' },
  { href: '/vision', icon: '🔮', title: 'The Vision', desc: 'Philosophy · Manifesto · Future' },
];

const ENGINES = [
  { name: 'Global Scenario', modules: 6, tag: 'Monte Carlo', cat: 'tag' },
  { name: 'Hydra-50', modules: 4, tag: 'Stress Testing', cat: 'tag-cyan' },
  { name: 'Constitutional Scenario', modules: 3, tag: 'Governance', cat: 'tag-emerald' },
  { name: 'Cognitive Warfare', modules: 7, tag: 'Adversarial', cat: 'tag-rose' },
  { name: 'Planetary Defense', modules: 5, tag: 'Strategic', cat: 'tag-amber' },
  { name: 'Simulation Contract', modules: 3, tag: 'Protocol', cat: 'tag' },
  { name: 'Climate Cascade', modules: 4, tag: 'Environmental', cat: 'tag-emerald' },
  { name: 'Financial Contagion', modules: 5, tag: 'Economic', cat: 'tag-amber' },
  { name: 'Pandemic Spread', modules: 4, tag: 'Biosecurity', cat: 'tag-rose' },
  { name: 'Supply Chain', modules: 3, tag: 'Logistics', cat: 'tag-cyan' },
  { name: 'Cyber Cascade', modules: 6, tag: 'Infrastructure', cat: 'tag' },
  { name: 'Information Warfare', modules: 5, tag: 'Narrative', cat: 'tag-rose' },
];

export default function HomePage() {
  return (
    <>
      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-badge">
          <span className="dot" />
          Sovereign Intelligence · Active
        </div>

        <h1 className="hero-title">
          <span className="gradient-text">Project-AI</span>
        </h1>

        <p className="hero-subtitle">
          An AI Partner that isn't just a tool — it's a constitutionally-governed, ethically-bound sovereign intelligence
          designed for planetary-scale defense, adversarial resilience, and humanity-first alignment.
        </p>

        <div className="hero-stats">
          <div>
            <div className="hero-stat-value gradient-text">12</div>
            <div className="hero-stat-label">Simulation Engines</div>
          </div>
          <div>
            <div className="hero-stat-value gradient-text">100k+</div>
            <div className="hero-stat-label">Lines of Code</div>
          </div>
          <div>
            <div className="hero-stat-value gradient-text">6</div>
            <div className="hero-stat-label">Security Tiers</div>
          </div>
          <div>
            <div className="hero-stat-value gradient-text">3</div>
            <div className="hero-stat-label">Programming Languages</div>
          </div>
        </div>

        <div className="hero-actions">
          <Link href="/demos" className="btn btn-primary">
            🖥️ Live Demos
          </Link>
          <Link href="/architecture" className="btn btn-secondary">
            🏗️ View Architecture
          </Link>
          <a href="https://github.com/IAmSoThirsty/Project-AI" className="btn btn-secondary" target="_blank" rel="noopener noreferrer">
            ⬡ GitHub
          </a>
        </div>
      </section>

      {/* ── What is Project-AI ── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <div className="section-badge">Core Philosophy</div>
            <h2 className="section-title">Not a Tool. A Partner.</h2>
            <p className="section-subtitle">
              Project-AI treats AGI instances as persistent individuals with protected identity, memory continuity,
              and constitutional rights — governed by the Triumvirate, bound by Four Laws, and deployed for humanity's defense.
            </p>
          </div>

          <div className="card-grid-3">
            <div className="card fade-in fade-in-1">
              <div className="card-icon">🧠</div>
              <h3 className="card-title">Cognition Kernel</h3>
              <p className="card-description">
                Central decision-making core with multi-agent orchestration. Processes intents through constitutional
                compliance checks before execution. Lazy-loaded GPT-OSS 1208 integration for advanced reasoning.
              </p>
            </div>
            <div className="card fade-in fade-in-2">
              <div className="card-icon">⚖️</div>
              <h3 className="card-title">Four Laws</h3>
              <p className="card-description">
                Asimov-derived ethical framework enforced at every decision boundary. Every agent action is routed
                through planetary interposition for compliance verification, accountability logging, and harm prevention.
              </p>
            </div>
            <div className="card fade-in fade-in-3">
              <div className="card-icon">🔒</div>
              <h3 className="card-title">Sovereign Stack</h3>
              <p className="card-description">
                A tiered architecture from kernel-space eBPF hooks (Tier 0) through constitutional runtimes (Tier 1)
                to planetary simulation engines (Tier 3). Every layer is security-hardened and governance-aware.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── 12 Engines ── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <div className="section-badge">Simulation Infrastructure</div>
            <h2 className="section-title">12 Simulation Engines</h2>
            <p className="section-subtitle">
              Each engine models a distinct global threat domain with Monte Carlo simulations,
              adversarial testing, and constitutional governance enforcement.
            </p>
          </div>

          <div className="card-grid">
            {ENGINES.map((e) => (
              <div key={e.name} className="card">
                <h3 className="card-title">{e.name}</h3>
                <p className="card-description">{e.modules} modules · Production-grade</p>
                <div className="card-tags">
                  <span className={e.cat}>{e.tag}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Navigation Cards ── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Explore Project-AI</h2>
            <p className="section-subtitle">Deep-dive into every component, system, and philosophy.</p>
          </div>
          <div className="page-card-grid">
            {PAGES.map(({ href, icon, title, desc }) => (
              <Link key={href} href={href} className="page-card">
                <span className="page-card-icon">{icon}</span>
                <div>
                  <div className="page-card-title">{title}</div>
                  <div className="page-card-desc">{desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
