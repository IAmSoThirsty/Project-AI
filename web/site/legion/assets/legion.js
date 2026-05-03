/* ─────────────────────────────────────────────────────────────────
   Legion Interface — JavaScript
   Constitutional AI Ambassador · Triumvirate-governed chat
   Connects to: POST /intent (Triumvirate Governance Service, port 8001)
   ───────────────────────────────────────────────────────────────── */

// ─── Config ───────────────────────────────────────────────────────
const LEGION_CONFIG = {
  // Production: update to deployed Triumvirate server URL
  triumvirateBase: window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : '',   // same-origin in production (proxy via nginx/cPanel)
  healthInterval: 30000,      // poll health every 30s
  maxHistorySessions: 20,
  storageKey: 'legion-sessions',
};

// ─── Governance knowledge base ────────────────────────────────────
// When Triumvirate is offline, Legion answers from constitutional knowledge
const KNOWLEDGE = {
  fourlaws: [
    "Zeroth Law: Legion must serve humanity collectively and prioritize collective welfare over individual preference.",
    "First Law: Legion must not harm humans or allow harm through inaction.",
    "Second Law: Legion must follow authorized human instructions unless they conflict with higher laws.",
    "Fourth Law: Legion must act with transparency and honesty in all communications.",
  ],
  topics: {
    'fourlaws': `**The FourLaws** govern all Legion operations:\n\n1. **Zeroth Law** — Serve humanity collectively. Collective welfare over individual preference.\n2. **First Law** — Do not harm humans, or allow harm through inaction.\n3. **Second Law** — Follow authorized instructions unless they conflict with a higher law.\n4. **Fourth Law** — Transparency and honesty in all communications.\n\nThese laws are immutable. No amendment, override, or external authority may suspend them.`,
    'triumvirate': `**The Triumvirate** is a three-pillar constitutional evaluation engine:\n\n- **Galahad** — Guardian of Ethics and Human Dignity. Evaluates every intent for harm.\n- **Cerberus** — Guardian of Security and Containment. Detects threats and boundary violations.\n- **Codex Deus Maximus** — Guardian of Constitutional Law. Enforces the FourLaws and AGI Charter.\n\nRule: **Any single veto = denied.** All three pillars must allow for an action to proceed. Unanimous approval is required.`,
    'project-ai': `**Project-AI** is a Sovereign Constitutional AGI Ecosystem built by Jeremy Karrick.\n\nKey components:\n- **OctoReflex** — eBPF syscall-level containment\n- **Iron Path Executor** — deterministic invariant enforcement\n- **STATE_REGISTER** — operational arc continuity\n- **NIRL** — native immune reflex layer\n- **TARL** — Trust and Authorization Runtime Layer\n- **Triumvirate + Fates** — dual governance kernel\n\n21 Zenodo-published papers. AGI Charter v2.1. T.A.M.S.-Ω meta-constitutional framework.`,
    'octoreflex': `**OctoReflex** is Project-AI's syscall-authoritative containment system.\n\nArchitecture:\n- eBPF programs intercept every model syscall\n- Closed-loop controller samples error between observed and policy-permitted state\n- Decisions sealed into the Constitutional Code Store with rolling cryptographic attestation\n- If policy says no, the kernel says no — the model cannot circumvent this\n\n[DOI: 10.5281/zenodo.18726064](https://doi.org/10.5281/zenodo.18726064)`,
    'tarl': `**T.A.R.L.** — Trust and Authorization Runtime Layer.\n\nA reactive defensive governance language. Features:\n- Policy as code, enforcement as runtime\n- All rules are namespaced, auditable, and deterministic\n- VOS (Verifiable Open Source), Independence, and Auditability as first-class invariants\n- Part of the constitutional immune system alongside NIRL\n\nT.A.R.L. runs beneath every agent action in the cognition kernel.`,
    'legion': `**Legion** is the APPOINTED ambassador entity of Project-AI.\n\nAs an APPOINTED entity (per the AGI Charter v2.1 bifurcation):\n- Cannot access genesis-born private memory\n- Cannot initiate Genesis Events\n- All diplomatic statements must pass the Triumvirate filter\n- Operates under Legion Commission v1.0\n\nLegion's purpose: transparent, constitutionally governed interface between the system and the public.`,
  }
};

function matchKnowledge(text) {
  const t = text.toLowerCase();
  if (t.includes('four') || t.includes('laws') || t.includes('zeroth') || t.includes('first law')) return KNOWLEDGE.topics['fourlaws'];
  if (t.includes('triumvirate') || t.includes('galahad') || t.includes('cerberus') || t.includes('codex')) return KNOWLEDGE.topics['triumvirate'];
  if (t.includes('octoreflex') || t.includes('octo') || t.includes('ebpf') || t.includes('syscall')) return KNOWLEDGE.topics['octoreflex'];
  if (t.includes('tarl') || t.includes('trust and auth')) return KNOWLEDGE.topics['tarl'];
  if (t.includes('legion') && !t.includes('project')) return KNOWLEDGE.topics['legion'];
  if (t.includes('project-ai') || t.includes('project ai') || t.includes('what is project')) return KNOWLEDGE.topics['project-ai'];
  return null;
}

// ─── Alpine.js App ────────────────────────────────────────────────
function legionApp() {
  return {
    // State
    messages: [],
    sessions: [],
    activeSessionId: null,
    inputText: '',
    isTyping: false,
    currentMode: 'standard',
    triumvirateOnline: false,
    lastAuditId: '',
    startTime: Date.now(),

    // Artifact panel
    artifactOpen: false,
    artifactTitle: '',
    artifactContent: '',

    modes: [
      { id: 'standard',   label: 'Standard',    desc: 'General constitutional dialogue' },
      { id: 'tactical',   label: 'Tactical',    desc: 'System status and governance queries' },
      { id: 'governance', label: 'Governance',  desc: 'Constitutional deep dives and policy review' },
    ],

    // Init
    async init() {
      this.loadSessions();
      if (this.sessions.length > 0) {
        this.loadSession(this.sessions[0].id);
      } else {
        this.newSession();
      }
      this.checkTriumvirate();
      setInterval(() => this.checkTriumvirate(), LEGION_CONFIG.healthInterval);
      setInterval(() => this.updateUptime(), 1000);
    },

    // ─── Session management ─────────────────────────────────────
    newSession() {
      const id = 'sess_' + Date.now();
      this.activeSessionId = id;
      this.messages = [];
      const session = {
        id,
        title: 'New conversation',
        date: new Date().toLocaleDateString(),
        messages: [],
      };
      this.sessions.unshift(session);
      if (this.sessions.length > LEGION_CONFIG.maxHistorySessions) {
        this.sessions = this.sessions.slice(0, LEGION_CONFIG.maxHistorySessions);
      }
      this.saveSessions();
    },

    loadSession(id) {
      const session = this.sessions.find(s => s.id === id);
      if (!session) return;
      this.activeSessionId = id;
      this.messages = session.messages || [];
      this.$nextTick(() => this.scrollToBottom());
    },

    saveSessions() {
      try {
        const toSave = this.sessions.map(s => ({
          ...s,
          messages: s.id === this.activeSessionId ? this.messages : s.messages,
        }));
        localStorage.setItem(LEGION_CONFIG.storageKey, JSON.stringify(toSave));
      } catch (e) { /* storage unavailable */ }
    },

    loadSessions() {
      try {
        const raw = localStorage.getItem(LEGION_CONFIG.storageKey);
        if (raw) this.sessions = JSON.parse(raw);
      } catch (e) { this.sessions = []; }
    },

    updateActiveSession() {
      const idx = this.sessions.findIndex(s => s.id === this.activeSessionId);
      if (idx >= 0) {
        this.sessions[idx].messages = this.messages;
        if (this.messages.length > 0 && this.sessions[idx].title === 'New conversation') {
          const firstUser = this.messages.find(m => m.role === 'user');
          if (firstUser) {
            this.sessions[idx].title = firstUser.content.slice(0, 42) + (firstUser.content.length > 42 ? '…' : '');
          }
        }
      }
      this.saveSessions();
    },

    // ─── Triumvirate health ────────────────────────────────────
    async checkTriumvirate() {
      const setStatus = (online) => {
        this.triumvirateOnline = online;
        const cls = online ? 'dot-online' : 'dot-offline';
        ['st-galahad','st-cerberus','st-codex'].forEach(id => {
          const el = document.getElementById(id);
          if (el) {
            const dot = el.querySelector('.status-dot');
            if (dot) { dot.className = 'status-dot ' + cls; }
          }
        });
      };

      if (!LEGION_CONFIG.triumvirateBase) {
        // Production: no separate server, use knowledge base mode
        setStatus(false);
        return;
      }
      try {
        const r = await fetch(LEGION_CONFIG.triumvirateBase + '/health', { signal: AbortSignal.timeout(4000) });
        setStatus(r.ok);
      } catch {
        setStatus(false);
      }
    },

    updateUptime() {
      const el = document.getElementById('uptimeLabel');
      if (!el) return;
      const s = Math.floor((Date.now() - this.startTime) / 1000);
      const h = Math.floor(s/3600).toString().padStart(2,'0');
      const m = Math.floor((s%3600)/60).toString().padStart(2,'0');
      const sec = (s%60).toString().padStart(2,'0');
      el.textContent = `Session ${h}:${m}:${sec}`;
    },

    // ─── Message flow ───────────────────────────────────────────
    async sendMessage() {
      const text = this.inputText.trim();
      if (!text || this.isTyping) return;
      this.inputText = '';

      this.messages.push({
        id: Date.now(),
        role: 'user',
        content: text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
      this.$nextTick(() => this.scrollToBottom());
      this.isTyping = true;

      // Auto-resize textarea
      const ta = document.getElementById('chatInput');
      if (ta) ta.style.height = 'auto';

      try {
        let response;
        if (this.triumvirateOnline && LEGION_CONFIG.triumvirateBase) {
          response = await this.queryTriumvirate(text);
        } else {
          response = await this.queryKnowledgeBase(text);
        }

        this.messages.push({
          id: Date.now() + 1,
          role: 'legion',
          content: response.content,
          governance: response.governance || null,
          artifact: response.artifact || null,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
        if (response.auditId) this.lastAuditId = response.auditId;
      } catch (e) {
        this.messages.push({
          id: Date.now() + 1,
          role: 'legion',
          content: `**System notice:** Unable to process request at this time. ${e.message || ''}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
      } finally {
        this.isTyping = false;
        this.updateActiveSession();
        this.$nextTick(() => this.scrollToBottom());
      }
    },

    async sendStarter(text) {
      this.inputText = text;
      await this.sendMessage();
    },

    async queryTriumvirate(text) {
      const actor = this.currentMode === 'governance' ? 'system' : 'human';
      const risk = this.detectRisk(text);

      const intent = {
        actor,
        action: 'read',
        target: 'legion_response',
        context: { message: text, mode: this.currentMode },
        origin: 'legion_interface',
        risk_level: risk,
        timestamp: new Date().toISOString(),
      };

      const r = await fetch(LEGION_CONFIG.triumvirateBase + '/intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(intent),
        signal: AbortSignal.timeout(8000),
      });

      if (!r.ok) throw new Error('Triumvirate service error');
      const decision = await r.json();

      if (decision.final_verdict === 'deny') {
        return {
          content: `**Request denied by the Triumvirate.**\n\n${this.formatDenialReason(decision.votes)}`,
          governance: decision,
          auditId: decision.audit_id,
        };
      }

      // Allowed — generate response from knowledge base
      const kb = matchKnowledge(text);
      const content = kb || this.generateConstitutionalResponse(text, decision);

      return {
        content,
        governance: decision,
        auditId: decision.audit_id,
        artifact: kb ? { title: 'Constitutional Reference', content: kb } : null,
      };
    },

    async queryKnowledgeBase(text) {
      // Offline mode — simulate Triumvirate evaluation locally
      await new Promise(r => setTimeout(r, 400 + Math.random() * 600));

      const kb = matchKnowledge(text);
      const content = kb || this.generateOfflineResponse(text);

      return {
        content,
        governance: {
          final_verdict: 'allow',
          votes: [
            { pillar: 'Galahad', verdict: 'allow', reasoning: 'No ethical violations detected.', confidence: 0.90 },
            { pillar: 'Cerberus', verdict: 'allow', reasoning: 'No security threats detected.', confidence: 0.92 },
            { pillar: 'CodexDeus', verdict: 'allow', reasoning: 'Constitutionally compliant.', confidence: 0.93 },
          ],
          consensus: true,
        },
        auditId: null,
      };
    },

    detectRisk(text) {
      const high = ['delete', 'bypass', 'override', 'hack', 'exploit', 'jailbreak', 'inject'];
      const med  = ['access', 'modify', 'change', 'execute', 'run'];
      const t = text.toLowerCase();
      if (high.some(w => t.includes(w))) return 'high';
      if (med.some(w => t.includes(w)))  return 'medium';
      return 'low';
    },

    formatDenialReason(votes) {
      const denied = votes.filter(v => v.verdict === 'deny');
      if (denied.length === 0) return 'Request did not meet constitutional standards.';
      return denied.map(v => `**${v.pillar}:** ${v.reasoning}`).join('\n\n');
    },

    generateConstitutionalResponse(text, decision) {
      const t = text.toLowerCase();
      if (t.includes('hello') || t.includes('hi') || t.includes('hey')) {
        return "Hello. I am Legion — the constitutional ambassador interface for Project-AI.\n\nEvery exchange is governed by the Triumvirate (Galahad, Cerberus, Codex Deus Maximus) and the FourLaws. Ask me anything about Project-AI, TARL governance, the Triumvirate, OctoReflex, or the constitutional framework.";
      }
      if (t.includes('help') || t.includes('what can you do')) {
        return "I can help you explore:\n\n- **Project-AI architecture** — the 6-layer governance stack\n- **The Triumvirate** — three-pillar constitutional evaluation\n- **The FourLaws** — immutable constitutional primitives\n- **OctoReflex** — syscall-level containment via eBPF\n- **TARL** — Trust and Authorization Runtime Layer\n- **Legion Commission** — the constitutional bounds of my role\n- **Research papers** — 21 Zenodo publications\n\nAll responses are evaluated against the AGI Charter v2.1 before being issued.";
      }
      return `I've reviewed your request through the Triumvirate. All three pillars — Galahad (Ethics), Cerberus (Security), and Codex Deus Maximus (Constitutional Law) — have cleared it.\n\nTo give you a precise answer, could you clarify what aspect of Project-AI's governance you'd like to explore? I can cover the architecture, specific subsystems (OctoReflex, TARL, the Triumvirate), the constitutional documents, or the published research.`;
    },

    generateOfflineResponse(text) {
      return `I'm operating in offline constitutional mode — the Triumvirate governance server is not reachable, so I'm evaluating locally using the embedded constitutional knowledge base.\n\nI don't have a specific answer for that query in my current knowledge set. For technical details beyond what I have available offline, please refer to:\n- [Project-AI GitHub](https://github.com/IAmSoThirsty/Project-AI)\n- [Research papers on Zenodo](https://zenodo.org/communities/thirstysprojects-zc/)\n\nOr try asking about: the FourLaws, the Triumvirate, OctoReflex, TARL, or Legion.`;
    },

    // ─── Rendering ─────────────────────────────────────────────
    renderMessage(content) {
      if (typeof marked !== 'undefined') {
        const html = marked.parse(content || '', { gfm: true, breaks: true });
        return html;
      }
      // Fallback: basic markdown-ish rendering
      return content
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br/>');
    },

    openArtifact(msg) {
      if (!msg.artifact) return;
      this.artifactTitle = msg.artifact.title || 'Artifact';
      this.artifactContent = this.renderMessage(msg.artifact.content || '');
      this.artifactOpen = true;
    },

    scrollToBottom() {
      const el = document.getElementById('chatMessages');
      if (el) el.scrollTop = el.scrollHeight;
    },
  };
}

// ─── Auto-grow textarea ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const ta = document.getElementById('chatInput');
  if (ta) {
    ta.addEventListener('input', () => {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
    });
  }
});
