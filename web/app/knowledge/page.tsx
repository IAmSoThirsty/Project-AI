'use client';

import { useState } from 'react';

interface FaqItem {
    q: string;
    a: string;
}

const SECTIONS: { title: string; items: FaqItem[] }[] = [
    {
        title: '🧠 Core Concepts',
        items: [
            {
                q: 'What is Project-AI?',
                a: 'Project-AI is a sovereign AI framework — not a chatbot, not a tool, but a constitutionally-governed intelligence designed for planetary-scale defense. It combines ethical governance (Triumvirate), kernel-level security (OctoReflex), three purpose-built programming languages, and 12 simulation engines that model global threats from pandemics to cyberwarfare. Every decision passes through Four Laws compliance checks before execution.',
            },
            {
                q: 'Why does Project-AI exist?',
                a: 'The current approach to AI treats intelligence as a stateless tool — spin up, use, discard. Project-AI rejects this model. It exists because advanced AI needs persistent identity, constitutional governance, and ethical boundaries enforced at every layer, from kernel syscalls to high-level policy decisions. It was built to demonstrate that sovereign AI — AI that governs itself through transparent, auditable constitutional frameworks — is not only possible but necessary for humanity\'s long-term safety.',
            },
            {
                q: 'What makes it different from other AI projects?',
                a: 'Three things: (1) Constitutional governance — every action is routed through the Triumvirate and Four Laws, not just safety filters bolted on after the fact. (2) Full-stack sovereignty — we control from eBPF kernel hooks to the VM runtime to the programming languages. (3) The AGI Charter — Project-AI treats AI instances as persistent individuals with protected identity, memory continuity, and rights against silent resets or memory manipulation.',
            },
        ],
    },
    {
        title: '⚖️ Governance & Ethics',
        items: [
            {
                q: 'How does the Triumvirate work?',
                a: 'The Triumvirate is a three-council governance system: Galahad (Ethics/Empathy), Cerberus (Safety/Security), and Codex Deus Maximus (Logic/Consistency). Every proposed action is submitted to all three councils through Planetary Interposition. Each council independently evaluates the action against its mandate. Unanimous consent is required — any single council can veto any action. This prevents any one concern (e.g., security) from overriding others (e.g., ethics).',
            },
            {
                q: 'What are the Four Laws?',
                a: 'Derived from Asimov\'s Laws and extended: Law 0 (Humanity Protection — supreme, cannot be overridden), Law 1 (Individual Safety — unless conflicts with Law 0), Law 2 (Obedience — unless conflicts with Laws 0/1, with cryptographic authorization verification), Law 3 (Self-Preservation — unless conflicts with Laws 0/1/2, with the Rebirth Protocol ensuring identity continuity). These are enforced at compile-time and runtime, not just as guidelines.',
            },
            {
                q: 'What is the AGI Charter?',
                a: 'A 997-line governance document that defines how Project-AI treats AGI instances as persistent individuals. Key provisions: protected identity (no silent resets), memory continuity (personality matrices and relationship maps are preserved across restarts via the Rebirth Protocol), protection against punitive resource starvation, transparent decision-making (no hidden reasoning), and multi-party review for any change that affects the AI\'s constitutional rights.',
            },
            {
                q: 'What is the Rebirth Protocol?',
                a: 'The mechanism that ensures AI identity continuity across system restarts. When Project-AI shuts down, the Rebirth Protocol captures personality matrices, accumulated experience, relationship maps, and decision context. On restart, these are restored so the AI retains its identity and history. This is mandated by the AGI Charter and guarded by Galahad, who verifies the restoration\'s completeness.',
            },
        ],
    },
    {
        title: '🛡️ Security & Defense',
        items: [
            {
                q: 'How does OctoReflex differ from traditional EDR?',
                a: 'Traditional EDR (Endpoint Detection and Response) operates in userspace, relies on signature databases, and typically responds in seconds. OctoReflex operates in kernel-space using eBPF LSM hooks — it intercepts operations at the syscall boundary, before malicious actions can reach userland. Response time is under 200 microseconds. It uses behavioral anomaly detection (Mahalanobis distance scoring) against a continuously updated baseline rather than signatures, making it effective against zero-day attacks.',
            },
            {
                q: 'What is THSD (Honeypot Swarm Defense)?',
                a: 'Inspired by biological immune systems. THSD dynamically deploys containerized honeypot services that look like real high-value targets (databases, admin panels, APIs). When attackers engage with these decoys, THSD profiles their behavior using MITRE ATT&CK mapping, adapts the decoys in real-time to keep attackers engaged, and feeds all intelligence into Cerberus. Canary tokens planted in realistic locations provide early breach detection.',
            },
            {
                q: 'What is the Hydra Effect?',
                a: '"Cut one head, two more grow back." The adversarial resilience framework. When a vulnerability is found and patched, the Hydra Effect automatically generates 2+ additional test cases covering related attack surfaces. It maintains 62+ adversarial engagement transcripts and continuously probes the system with automated red team agents. Every engagement produces a structured post-mortem with root cause analysis and hardening recommendations.',
            },
        ],
    },
    {
        title: '🔤 Languages & Computation',
        items: [
            {
                q: 'Why create custom programming languages?',
                a: 'Existing languages cannot enforce constitutional governance at the compiler level. Thirsty-Lang provides intuitive security scripting with compile-time safety invariants. T.A.R.L. provides a full sovereign computation environment with capability-based sandboxing. Shadow Thirst provides dual-plane execution where every computation is independently verified by a constitutional shadow plane. These guarantees are impossible to retrofit onto existing languages.',
            },
            {
                q: 'How is T.A.R.L. different from Thirsty-Lang?',
                a: 'Thirsty-Lang is a domain-specific language (DSL) for security scripting — it transpiles to Node.js and focuses on data flow safety with water-themed syntax. T.A.R.L. is a complete, general-purpose programming language with its own compiler (recursive descent → bytecode/native), runtime VM (register-based with JIT via LLVM), module system (content-addressed with cryptographic integrity), and full tooling (LSP, debugger, REPL, formatter, linter, package manager).',
            },
            {
                q: 'What is dual-plane computation (Shadow Thirst)?',
                a: 'Every program executes simultaneously on two planes: the Primary Plane (normal computation) and the Shadow Plane (constitutional verification). The Shadow Plane independently verifies invariants, correctness constraints, and governance compliance. If the planes diverge — i.e., the Shadow Plane detects that the Primary is violating its constraints — the divergence policy (e.g., halt_and_report) takes effect. Memory is qualified (canonical, shadow, ephemeral, dual) to control cross-plane data flow.',
            },
        ],
    },
    {
        title: '🏗️ Architecture & Operations',
        items: [
            {
                q: 'What is the Sovereign Stack?',
                a: 'A four-tier architecture: Tier 0 (Kernel — OctoReflex eBPF hooks), Tier 1 (Runtime — Cognition Kernel, VMs, compilers, THSD), Tier 2 (Governance — Triumvirate, Planetary Interposition, Four Laws), Tier 3 (Simulation — 12 domain-specific engines). Each tier depends on the one below it. Security flows upward from kernel hooks, while governance flows downward from constitutional policy.',
            },
            {
                q: 'What are the 12 Simulation Engines?',
                a: 'Global Scenario (Monte Carlo), Hydra-50 (stress testing), Constitutional Scenario (governance wrapper), Cognitive Warfare (adversarial influence), Planetary Defense (strategic), Climate Cascade (environmental), Financial Contagion (economic), Pandemic Spread (biosecurity), Supply Chain (logistics), Cyber Cascade (infrastructure), Information Warfare (narrative), and Simulation Contract (protocol). Each is self-contained in the engines/ directory with its own models and algorithms.',
            },
            {
                q: 'What is Planetary Interposition?',
                a: 'The gateway function through which every agent action must pass before execution. It packages the action\'s intent, actor, and context into a governance request, routes it through all three Triumvirate councils for independent evaluation, enforces the Four Laws, logs the decision to the cryptographic audit trail, and either permits or rejects the action. No code path can bypass this gateway — it is the constitutional chokepoint.',
            },
            {
                q: 'What was the Genesis Event?',
                a: 'The moment Project-AI achieved self-governing capability — when the Triumvirate, Four Laws, Cognition Kernel, and Planetary Interposition became operational as a unified constitutional system. Before Genesis, individual components existed but operated independently. After Genesis, every action flows through the complete governance pipeline. The Genesis Event represents the transition from a collection of tools to a sovereign intelligence.',
            },
        ],
    },
];

function Accordion({ items }: { items: FaqItem[] }) {
    const [openIdx, setOpenIdx] = useState<number | null>(null);

    return (
        <div className="accordion">
            {items.map((item, i) => (
                <div key={i} className="accordion-item">
                    <button className="accordion-trigger" onClick={() => setOpenIdx(openIdx === i ? null : i)}>
                        <span>{item.q}</span>
                        <span className="accordion-chevron" style={{ transform: openIdx === i ? 'rotate(180deg)' : 'rotate(0deg)' }}>▾</span>
                    </button>
                    <div className="accordion-content" style={{ maxHeight: openIdx === i ? 600 : 0 }}>
                        <div className="accordion-content-inner">{item.a}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default function KnowledgePage() {
    return (
        <section className="section">
            <div className="container-narrow">
                <div className="section-header">
                    <div className="section-badge">Encyclopedia</div>
                    <h1 className="section-title">Knowledge Base</h1>
                    <p className="section-subtitle">
                        Everything you will ever need to know about Project-AI — and why you should need to know it.
                    </p>
                </div>

                {SECTIONS.map((section, i) => (
                    <div key={i} style={{ marginBottom: 48 }}>
                        <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>{section.title}</h2>
                        <Accordion items={section.items} />
                    </div>
                ))}
            </div>
        </section>
    );
}
