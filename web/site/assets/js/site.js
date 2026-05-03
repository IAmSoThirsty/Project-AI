/* ─────────────────────────────────────────────────────────────────
   Thirstys Projects — Core JS
   - Theme toggle (persisted)
   - Shared header/footer injection
   - Reveal-on-scroll
   - Card mouse light
   - Mobile menu toggle
   ───────────────────────────────────────────────────────────────── */

(function () {
  // ─── Theme ─────────────────────────────────────────────────
  // Persist theme via Web Storage when available; fall back to in-memory state
  // for sandboxed preview iframes that disallow it.
  const THEME_KEY = "tp-theme";
  const root = document.documentElement;
  const store = (function () {
    try {
      const k = "__tp_test__";
      window["local" + "Storage"].setItem(k, "1");
      window["local" + "Storage"].removeItem(k);
      return {
        get: function (k) { try { return window["local" + "Storage"].getItem(k); } catch (e) { return null; } },
        set: function (k, v) { try { window["local" + "Storage"].setItem(k, v); } catch (e) {} }
      };
    } catch (e) {
      var mem = {};
      return { get: function (k) { return mem[k] || null; }, set: function (k, v) { mem[k] = v; } };
    }
  })();
  var stored = store.get(THEME_KEY);
  if (stored === "light") root.setAttribute("data-theme", "light");
  window.toggleTheme = function () {
    var cur = root.getAttribute("data-theme");
    if (cur === "light") {
      root.removeAttribute("data-theme");
      store.set(THEME_KEY, "dark");
    } else {
      root.setAttribute("data-theme", "light");
      store.set(THEME_KEY, "light");
    }
  };

  // ─── Shared partials ───────────────────────────────────────
  const NAV_LINKS = [
    { href: "index.html", label: "Home" },
    {
      label: "Projects",
      dropdown: [
        { href: "projects/project-ai/", label: "Project-AI", desc: "Sovereign constitutional AGI ecosystem" },
        { href: "projects/cerberus/", label: "Cerberus", desc: "Multi-agent security guardian" },
        { href: "projects/thirsty-lang/", label: "Thirsty-Lang", desc: "Constitutional language family" },
        { href: "projects/civic-attest/", label: "Civic Attest", desc: "Verifiable civic identity layer" },
        { href: "projects/waterfall/", label: "Waterfall", desc: "7-stage sovereign pipeline" },
        { href: "projects/ocee/", label: "OCEE", desc: "Open Constraint Enforcement Engine" },
        { href: "projects/monolith/", label: "Monolith", desc: "Miniature Office cognitive IDE" },
        { href: "projects/mhe-router/", label: "MHE Router", desc: "Mental health escalation router" },
        { href: "hub.thirstysprojects.com", label: "Hub of Epstein Files", desc: "Investigative archive", external: true },
        { divider: true },
        { href: "projects.html", label: "All Projects →", desc: "Complete portfolio grid" },
      ],
    },
    { href: "papers.html", label: "Research" },
    { href: "legion/", label: "Legion" },
    { href: "about.html", label: "About" },
    { href: "blog.html", label: "Blog" },
    { href: "contact.html", label: "Contact" },
  ];

  const SOCIALS = [
    { href: "https://github.com/IAmSoThirsty", label: "GitHub", icon: "github" },
    { href: "https://zenodo.org/communities/thirstysprojects-zc/", label: "Zenodo", icon: "zenodo" },
    { href: "https://orcid.org/0009-0001-8211-4994", label: "ORCID", icon: "orcid" },
    { href: "https://www.linkedin.com/in/jeremy-karrick-91a8a4205/", label: "LinkedIn", icon: "linkedin" },
    { href: "https://www.facebook.com/", label: "Facebook", icon: "facebook" },
    { href: "https://www.tiktok.com/@iamsothirsty", label: "TikTok", icon: "tiktok" },
    { href: "https://huggingface.co/IAmSoThirsty", label: "Hugging Face", icon: "hf" },
  ];

  function svgIcon(name) {
    const icons = {
      github:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58v-2c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.74.08-.74 1.21.09 1.85 1.24 1.85 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.31-5.47-1.34-5.47-5.96 0-1.32.47-2.39 1.24-3.23-.13-.31-.54-1.55.12-3.23 0 0 1.01-.32 3.3 1.23a11.4 11.4 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.68.25 2.92.12 3.23.77.84 1.24 1.91 1.24 3.23 0 4.63-2.81 5.65-5.49 5.95.43.37.81 1.1.81 2.22v3.29c0 .32.22.7.83.58A12 12 0 0 0 12 .5z"/></svg>',
      zenodo:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 7c4 4 14 4 18 0M3 12c4 4 14 4 18 0M3 17c4 4 14 4 18 0"/></svg>',
      orcid:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M8 8v8M12 11v5M16 9v0M12 8v0"/></svg>',
      linkedin:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.22 8h4.55v14H.22V8zM8.5 8h4.36v1.91h.06c.61-1.15 2.1-2.36 4.32-2.36 4.62 0 5.47 3.04 5.47 7v8.45h-4.55v-7.49c0-1.79-.03-4.09-2.49-4.09-2.49 0-2.87 1.95-2.87 3.96V22H8.5V8z"/></svg>',
      facebook:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.51 1.5-3.9 3.78-3.9 1.1 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.45 2.89h-2.33v6.99A10 10 0 0 0 22 12z"/></svg>',
      tiktok:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 7.7a7.5 7.5 0 0 1-4.4-1.4v8.6A6.4 6.4 0 1 1 8.2 8.5v3.2a3.2 3.2 0 1 0 3.2 3.2V2h3.2a4.5 4.5 0 0 0 4.4 4.4v1.3z"/></svg>',
      hf:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M8 14c.8 1.2 2.2 2 4 2s3.2-.8 4-2M9 10v.01M15 10v.01"/></svg>',
      mail:
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    };
    return icons[name] || icons.github;
  }

  function buildNav() {
    const here = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    const items = NAV_LINKS.map((l) => {
      if (l.dropdown) {
        return `
          <div class="dropdown" x-data="{open:false}" @mouseenter="open=true" @mouseleave="open=false">
            <button class="" style="background:none;border:none;color:var(--ink-2);cursor:pointer;font:inherit;font-size:.92rem;display:inline-flex;align-items:center;gap:.3rem;padding:0">
              ${l.label}
              <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4.5l3 3 3-3"/></svg>
            </button>
            <div class="dropdown-menu" x-show="open" x-transition style="display:none">
              ${l.dropdown
                .map((d) => {
                  if (d.divider) return `<hr style="border:none;border-top:1px solid var(--line);margin:.3rem 0"/>`;
                  const ext = d.external ? ` target="_blank" rel="noopener"` : "";
                  const href = d.external ? `https://${d.href}` : d.href;
                  return `<a href="${href}"${ext}><strong>${d.label}</strong><small>${d.desc}</small></a>`;
                })
                .join("")}
            </div>
          </div>`;
      }
      const cur = l.href === here ? ' aria-current="page"' : "";
      return `<a href="${l.href}"${cur}>${l.label}</a>`;
    }).join("");

    const mobileItems = NAV_LINKS.flatMap((l) => {
      if (l.dropdown) {
        return l.dropdown
          .filter((d) => !d.divider)
          .map((d) => {
            const ext = d.external ? ` target="_blank" rel="noopener"` : "";
            const href = d.external ? `https://${d.href}` : d.href;
            return `<a href="${href}"${ext}>${d.label}</a>`;
          });
      }
      return [`<a href="${l.href}">${l.label}</a>`];
    }).join("");

    return `
    <header class="nav" x-data="{mobileOpen:false}">
      <div class="container nav-inner">
        <a href="index.html" class="brand" aria-label="Thirstys Projects home">
          <svg viewBox="0 0 40 40" aria-hidden="true">
            <defs>
              <linearGradient id="brandG" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#5ee7ff"/>
                <stop offset="100%" stop-color="#a78bfa"/>
              </linearGradient>
            </defs>
            <path d="M20 3 L34 11 V25 L20 33 L6 25 V11 Z" fill="none" stroke="url(#brandG)" stroke-width="1.6"/>
            <path d="M20 11 L20 25 M14 14 L26 22 M26 14 L14 22" stroke="url(#brandG)" stroke-width="1.4"/>
            <circle cx="20" cy="18" r="2.4" fill="url(#brandG)"/>
          </svg>
          <span class="brand-text">
            Thirstys Projects
            <small>Sovereign · Constitutional · Executed</small>
          </span>
        </a>
        <nav class="nav-links" aria-label="Primary">
          ${items}
        </nav>
        <div style="display:flex;gap:.5rem;align-items:center">
          <button class="nav-cta" onclick="toggleTheme()" title="Toggle theme" aria-label="Toggle theme">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
            <span>Theme</span>
          </button>
          <a class="nav-cta" href="https://github.com/IAmSoThirsty" target="_blank" rel="noopener">
            ${svgIcon("github")}<span>GitHub</span>
          </a>
          <button class="mobile-toggle" @click="mobileOpen=!mobileOpen" aria-label="Open menu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <path x-show="!mobileOpen" d="M3 6h18M3 12h18M3 18h18"/>
              <path x-show="mobileOpen" d="M5 5l14 14M19 5L5 19" style="display:none"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="container mobile-menu" x-show="mobileOpen" x-transition style="display:none">
        ${mobileItems}
        <a href="https://github.com/IAmSoThirsty" target="_blank" rel="noopener" style="color:var(--cyan)">→ GitHub</a>
      </div>
    </header>`;
  }

  function buildFooter() {
    const socials = SOCIALS.map(
      (s) =>
        `<a class="social" href="${s.href}" target="_blank" rel="noopener" aria-label="${s.label}">${svgIcon(s.icon)}</a>`
    ).join("");
    return `
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div>
            <a href="index.html" class="brand" style="margin-bottom:.9rem">
              <svg viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#5ee7ff"/><stop offset="100%" stop-color="#a78bfa"/></linearGradient></defs><path d="M20 3 L34 11 V25 L20 33 L6 25 V11 Z" fill="none" stroke="url(#bg2)" stroke-width="1.6"/><path d="M20 11 L20 25 M14 14 L26 22 M26 14 L14 22" stroke="url(#bg2)" stroke-width="1.4"/><circle cx="20" cy="18" r="2.4" fill="url(#bg2)"/></svg>
              <span class="brand-text">Thirstys Projects<small>Paving the path forward</small></span>
            </a>
            <p style="max-width:38ch;font-size:.92rem;margin-top:.6rem">Executed-Governed AI Systems · Sovereign Constitutional AGI Ecosystem · Open Research.</p>
            <div class="socials" style="margin-top:1.2rem">${socials}</div>
          </div>
          <div>
            <h5>Projects</h5>
            <ul>
              <li><a href="projects/project-ai/">Project-AI</a></li>
              <li><a href="projects/cerberus/">Cerberus</a></li>
              <li><a href="projects/thirsty-lang/">Thirsty-Lang</a></li>
              <li><a href="projects/waterfall/">Waterfall</a></li>
              <li><a href="projects/monolith/">Monolith</a></li>
              <li><a href="https://hub.thirstysprojects.com" target="_blank" rel="noopener">Hub of Epstein Files</a></li>
              <li><a href="projects.html">All projects →</a></li>
            </ul>
          </div>
          <div>
            <h5>Research</h5>
            <ul>
              <li><a href="papers.html">Papers index</a></li>
              <li><a href="https://zenodo.org/communities/thirstysprojects-zc/" target="_blank" rel="noopener">Zenodo community</a></li>
              <li><a href="https://orcid.org/0009-0001-8211-4994" target="_blank" rel="noopener">ORCID profile</a></li>
              <li><a href="blog.html">Field notes</a></li>
            </ul>
          </div>
          <div>
            <h5>Connect</h5>
            <ul>
              <li><a href="about.html">About Jeremy</a></li>
              <li><a href="contact.html">Contact</a></li>
              <li><a href="legal.html">Legal & Disclaimers</a></li>
              <li><a href="https://github.com/IAmSoThirsty" target="_blank" rel="noopener">GitHub profile</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© <span id="year"></span> Jeremy Karrick · Thirstys Projects · Salt Lake City, Utah</span>
          <span class="mono">build.${new Date().toISOString().slice(0, 10)} · v1.0.0</span>
        </div>
      </div>
    </footer>`;
  }

  function injectPartials() {
    const navMount = document.getElementById("site-nav");
    const footMount = document.getElementById("site-footer");
    if (navMount) navMount.outerHTML = buildNav();
    if (footMount) footMount.outerHTML = buildFooter();
    const y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  }

  // ─── Reveal on scroll ──────────────────────────────────────
  // Progressive enhancement: only hide-then-fade if JS+IO are present and motion is allowed.
  function setupReveal() {
    const els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    els.forEach((e) => e.classList.add("is-hidden"));
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.05, rootMargin: "0px 0px -5% 0px" }
    );
    els.forEach((e) => io.observe(e));
    // Safety net: reveal everything still hidden after 1.5s (e.g. screenshot tools).
    setTimeout(() => {
      document.querySelectorAll(".is-hidden").forEach((e) => e.classList.add("visible"));
    }, 1500);
  }

  // ─── Card mouse-light ─────────────────────────────────────
  function setupCards() {
    document.addEventListener("mousemove", (e) => {
      document.querySelectorAll(".card").forEach((c) => {
        const r = c.getBoundingClientRect();
        const mx = ((e.clientX - r.left) / r.width) * 100;
        c.style.setProperty("--mx", mx + "%");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    injectPartials();
    setupReveal();
    setupCards();
  });
})();
