OMPT.md — the luxury-grade dark-mode static Project-AI website prompt.
It was for a Namecheap-hostable multi-page HTML/CSS/JS website with this exact vibe:
severe, expensive, governed, inevitable
like entering a controlled perimeter, not reading a landing page
It specified pages for:
index.html
architecture.html
publications.html
repository.html
about.html
styles.css
app.js
The file says the site should be “luxury-grade,” “dark-mode,” “static-first,” with black/near-black background, steel-blue/violet/amber highlights, glass panels, restrained motion, manifesto text, proof surfaces, Triumvirate governance, Zenodo-style publications, and a GitHub-centered repo page.
So yes: that’s the sexy-ass one.
Can you provide the code for me in a block end to end coverage
Show moreShow less
I’ll recover the strongest available website spec from your uploaded files, then provide a complete static site in one copy-pasteable block: HTML pages, CSS, JS, and deployment notes.
Recovered the original spec. It explicitly required a static multi-page site with index.html, architecture.html, publications.html, repository.html, about.html, styles.css, and app.js, no mandatory server runtime.
Thought for 24s
Recovered spec: static-first, Namecheap-safe, dark luxury, severe/governed/inevitable, multi-page HTML/CSS/JS only. Deployment is direct upload of these files through cPanel or FTP.
Copy this into the site root as separate files.
================================================================================
FILE: index.html
================================================================================
<!doctype html>
<html lang="en" data-page="home">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Project-AI | Governance Is The Execution Path</title>
  <meta name="description" content="Project-AI is a constitutionally governed AI substrate where governance is not an overlay, but a precondition of execution." />
  <meta name="theme-color" content="#05070b" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="site-noise" aria-hidden="true"></div>
  <div class="site-grid" aria-hidden="true"></div>
  <div class="cursor-glow" aria-hidden="true"></div>

  <header class="topbar" data-header>
    <a class="brand" href="index.html" aria-label="Project-AI home">
      <span class="brand-mark">PAI</span>
      <span class="brand-copy">
        <strong>Project-AI</strong>
        <em>Execution-Governed Substrate</em>
      </span>
    </a>

    <button class="nav-toggle" data-nav-toggle aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>

    <nav class="nav" data-nav>
      <a href="index.html" data-nav-link="home">Home</a>
      <a href="architecture.html" data-nav-link="architecture">Architecture</a>
      <a href="publications.html" data-nav-link="publications">Publications</a>
      <a href="repository.html" data-nav-link="repository">Repository</a>
      <a href="about.html" data-nav-link="about">About</a>
    </nav>
  </header>

  <main>
    <section class="hero home-hero">
      <div class="wrap hero-grid">
        <div class="hero-copy-block reveal">
          <div class="eyebrow">Proof before trust · Governance before execution</div>
          <h1>
            <span class="gradient-text">Governance is not an overlay.</span>
            It is the execution path.
          </h1>
          <p class="hero-copy">
            Project-AI is a sovereign-grade AI substrate: constitutionally governed,
            cryptographically bounded, and architected so invalid action is not merely
            discouraged. It is made structurally unreachable.
          </p>
          <div class="hero-actions">
            <a class="button primary" href="architecture.html">Enter the architecture</a>
            <a class="button ghost" href="publications.html">Inspect the record</a>
          </div>
        </div>

        <aside class="hero-panel reveal" aria-label="Governed execution terminal">
          <div class="panel-topline">
            <span class="status-dot"></span>
            <span>Execution boundary · locked</span>
          </div>
          <pre class="terminal"><code><span class="prompt">$</span> project-ai verify --request mutation.intent

<span class="dim">ingress:</span> external_action_request
<span class="ok">[PASS]</span> identity attested
<span class="ok">[PASS]</span> capability scope loaded
<span class="ok">[PASS]</span> negative capability list checked
<span class="ok">[PASS]</span> shadow evaluation converged
<span class="warn">[HOLD]</span> non-compliant branch pruned
<span class="ok">[PASS]</span> triumvirate quorum satisfied
<span class="ok">[PASS]</span> immutable audit block anchored

<span class="dim">result:</span> action reachable only after governance.</code></pre>
        </aside>
      </div>

      <div class="wrap metrics-band reveal">
        <article>
          <strong>Default Deny</strong>
          <span>Unverified action does not proceed.</span>
        </article>
        <article>
          <strong>Shadow First</strong>
          <span>Evaluation precedes mutation.</span>
        </article>
        <article>
          <strong>Quorum Bound</strong>
          <span>Authority requires structured consent.</span>
        </article>
        <article>
          <strong>Audit Sealed</strong>
          <span>Every consequential edge is reconstructable.</span>
        </article>
      </div>
    </section>

    <section class="section" id="doctrine">
      <div class="wrap split">
        <div class="section-head reveal">
          <div class="eyebrow">Doctrine</div>
          <h2>The system does not ask whether an action sounds safe. It asks whether the action is valid.</h2>
        </div>
        <div class="doctrine-stack">
          <article class="glass-card reveal">
            <span class="card-index">01</span>
            <h3>Invalid states cannot be proposed.</h3>
            <p>Every request is reduced to an admissibility question before it is allowed near execution.</p>
          </article>
          <article class="glass-card reveal">
            <span class="card-index">02</span>
            <h3>Unsafe transitions fail deterministically.</h3>
            <p>The system does not depend on model temperament. It depends on gates, invariants, proof surfaces, and replay.</p>
          </article>
          <article class="glass-card reveal">
            <span class="card-index">03</span>
            <h3>Every execution path is forced through governance.</h3>
            <p>Governance does not decorate the product. Governance owns the route to action.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section dark-ridge">
      <div class="wrap">
        <div class="section-head centered reveal">
          <div class="eyebrow">Triumvirate</div>
          <h2>Three pillars. One bounded decision surface.</h2>
          <p>Ethics, defense, and arbitration are treated as runtime authorities, not post-hoc review labels.</p>
        </div>

        <div class="triad">
          <article class="pillar reveal">
            <div class="pillar-orb galahad"></div>
            <h3>Galahad</h3>
            <p>Ethics, human dignity, alignment pressure, and legitimacy evaluation.</p>
            <ul>
              <li>Policy interpretation</li>
              <li>Harm surface detection</li>
              <li>Human-facing constraint review</li>
            </ul>
          </article>
          <article class="pillar reveal">
            <div class="pillar-orb cerberus"></div>
            <h3>Cerberus</h3>
            <p>Threat containment, misuse resistance, adversarial pressure, and system integrity.</p>
            <ul>
              <li>Attack-path rejection</li>
              <li>Privilege boundary checks</li>
              <li>Containment escalation</li>
            </ul>
          </article>
          <article class="pillar reveal">
            <div class="pillar-orb codex"></div>
            <h3>Codex Deus</h3>
            <p>Arbitration, orchestration, conflict resolution, and governance synthesis.</p>
            <ul>
              <li>Quorum coordination</li>
              <li>Decision record formation</li>
              <li>Promotion or denial</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="architecture-preview">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <div class="eyebrow">Architecture</div>
            <h2>The path from request to consequence is narrow by design.</h2>
          </div>
          <a class="text-link" href="architecture.html">Open full system map</a>
        </div>

        <div class="flowline reveal" aria-label="Execution governance flow">
          <div class="flow-node">Ingress</div>
          <div class="flow-arrow"></div>
          <div class="flow-node">Identity</div>
          <div class="flow-arrow"></div>
          <div class="flow-node">Scope</div>
          <div class="flow-arrow"></div>
          <div class="flow-node">Shadow</div>
          <div class="flow-arrow"></div>
          <div class="flow-node">Quorum</div>
          <div class="flow-arrow"></div>
          <div class="flow-node emph">Commit</div>
        </div>

        <div class="proof-grid">
          <article class="proof-card reveal">
            <h3>Proof-carrying admissibility</h3>
            <p>Actions advance only when accompanied by a valid governance record.</p>
          </article>
          <article class="proof-card reveal">
            <h3>Replay equivalence</h3>
            <p>Decision records exist so the same decision can be reconstructed, not guessed.</p>
          </article>
          <article class="proof-card reveal">
            <h3>Mutation governance</h3>
            <p>Changes to state, memory, tools, or policy require an explicit authority path.</p>
          </article>
          <article class="proof-card reveal">
            <h3>Continuity verification</h3>
            <p>The runtime must verify state before action. No assumed continuity.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section proof-surface" id="proof">
      <div class="wrap proof-shell reveal">
        <div>
          <div class="eyebrow">Proof surface</div>
          <h2>Make the claim inspectable.</h2>
          <p>
            The website’s job is not to beg for belief. It routes serious visitors toward
            artifacts: repository structure, papers, execution doctrine, governance diagrams,
            and audit language.
          </p>
        </div>
        <div class="receipt-stack">
          <a class="receipt" href="repository.html">
            <span>Repository</span>
            <strong>Visible code depth</strong>
          </a>
          <a class="receipt" href="publications.html">
            <span>Publications</span>
            <strong>DOI-backed theory layer</strong>
          </a>
          <a class="receipt" href="architecture.html">
            <span>Architecture</span>
            <strong>Governed execution model</strong>
          </a>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="wrap cta-shell reveal">
        <div>
          <div class="eyebrow">Final boundary</div>
          <h2>Inspect the system. Do not take the claim on faith.</h2>
          <p>Project-AI is framed as an execution-governed AI substrate: the constitution is not a document beside the system. It is the route through which the system is allowed to act.</p>
        </div>
        <div class="hero-actions">
          <a class="button primary" href="https://github.com/IAmSoThirsty/Project-AI" target="_blank" rel="noreferrer">Open GitHub</a>
          <a class="button ghost" href="publications.html">Open publications</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>Project-AI · IAmSoThirsty</span>
      <span>Governance before execution.</span>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>

================================================================================
FILE: architecture.html
================================================================================
<!doctype html>
<html lang="en" data-page="architecture">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Architecture | Project-AI</title>
  <meta name="description" content="Architecture of Project-AI: governance before execution, shadow evaluation, quorum, iron path promotion, and immutable audit." />
  <meta name="theme-color" content="#05070b" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="site-noise" aria-hidden="true"></div>
  <div class="site-grid" aria-hidden="true"></div>
  <div class="cursor-glow" aria-hidden="true"></div>

  <header class="topbar" data-header>
    <a class="brand" href="index.html" aria-label="Project-AI home">
      <span class="brand-mark">PAI</span>
      <span class="brand-copy">
        <strong>Project-AI</strong>
        <em>Execution-Governed Substrate</em>
      </span>
    </a>
    <button class="nav-toggle" data-nav-toggle aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" data-nav>
      <a href="index.html" data-nav-link="home">Home</a>
      <a href="architecture.html" data-nav-link="architecture">Architecture</a>
      <a href="publications.html" data-nav-link="publications">Publications</a>
      <a href="repository.html" data-nav-link="repository">Repository</a>
      <a href="about.html" data-nav-link="about">About</a>
    </nav>
  </header>

  <main>
    <section class="page-hero">
      <div class="wrap narrow reveal">
        <div class="eyebrow">Architecture</div>
        <h1>Execution is not granted by intent. Execution is granted by admissibility.</h1>
        <p>
          The architecture compresses every consequential request into a bounded route:
          identity, capability, shadow evaluation, invariant validation, quorum synthesis,
          promotion, commit, and replay.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="system-map reveal">
          <div class="map-row">
            <div class="map-cell muted">User / Agent / Tool Request</div>
          </div>
          <div class="map-line"></div>
          <div class="map-row three">
            <div class="map-cell">Ingress Boundary</div>
            <div class="map-cell">Identity Attestation</div>
            <div class="map-cell">Capability Scope</div>
          </div>
          <div class="map-line"></div>
          <div class="map-row three">
            <div class="map-cell violet">Shadow Evaluation</div>
            <div class="map-cell amber">Triumvirate Quorum</div>
            <div class="map-cell blue">Invariant Engine</div>
          </div>
          <div class="map-line"></div>
          <div class="map-row">
            <div class="map-cell strong">Iron Path Promotion</div>
          </div>
          <div class="map-line"></div>
          <div class="map-row three">
            <div class="map-cell">Commit</div>
            <div class="map-cell">Audit Seal</div>
            <div class="map-cell">Replay Record</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section dark-ridge">
      <div class="wrap split">
        <div class="section-head reveal">
          <div class="eyebrow">Core model</div>
          <h2>Governance before execution is a routing rule.</h2>
        </div>
        <div class="text-stack reveal">
          <p>
            A normal AI system often places safety after generation: classify the prompt,
            generate a response, filter the output, log the aftermath. Project-AI inverts
            that order. The action route itself is governed.
          </p>
          <p>
            In this model, the important question is not “did the model say something
            acceptable?” The important question is “was this action ever valid to execute?”
          </p>
          <p>
            That shift matters. It means policy becomes a precondition, not a decoration.
            It means invalid actions fail because the execution route cannot form.
          </p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head centered reveal">
          <div class="eyebrow">Execution path</div>
          <h2>The narrow bridge.</h2>
        </div>

        <div class="timeline">
          <article class="timeline-item reveal">
            <span>01</span>
            <h3>Ingress normalization</h3>
            <p>Requests are reduced into structured action claims: actor, target, scope, tool, intended mutation, and consequence class.</p>
          </article>
          <article class="timeline-item reveal">
            <span>02</span>
            <h3>Identity and authority</h3>
            <p>The runtime checks who or what is acting, whether the authority exists, and whether it survives current context.</p>
          </article>
          <article class="timeline-item reveal">
            <span>03</span>
            <h3>Capability boundary</h3>
            <p>Positive authorization scope and negative capability lists bound what the action is permitted to reach.</p>
          </article>
          <article class="timeline-item reveal">
            <span>04</span>
            <h3>Shadow evaluation</h3>
            <p>The action is simulated without committing canonical state. Divergence, hazard, and invariant violation are detected before consequence.</p>
          </article>
          <article class="timeline-item reveal">
            <span>05</span>
            <h3>Triumvirate synthesis</h3>
            <p>Galahad, Cerberus, and Codex Deus produce a structured decision surface: ethics, threat, arbitration.</p>
          </article>
          <article class="timeline-item reveal">
            <span>06</span>
            <h3>Iron Path promotion</h3>
            <p>Only valid, bounded, fully evaluated action records are promoted from proposal to execution.</p>
          </article>
          <article class="timeline-item reveal">
            <span>07</span>
            <h3>Commit and audit</h3>
            <p>The action executes, emits a decision record, seals audit metadata, and preserves replay equivalence.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section proof-surface">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <div class="eyebrow">Governance components</div>
            <h2>Runtime authorities.</h2>
          </div>
        </div>

        <div class="component-grid">
          <article class="component-card reveal">
            <h3>Constitutional Kernel</h3>
            <p>Defines non-negotiable invariants, hard rejection logic, and the admissibility surface for consequential action.</p>
          </article>
          <article class="component-card reveal">
            <h3>Quorum Engine</h3>
            <p>Transforms advisory evaluation into a decision record with explicit approval, denial, or escalation.</p>
          </article>
          <article class="component-card reveal">
            <h3>Shadow Plane</h3>
            <p>Allows speculative transformation without canonical mutation, protecting system state from unvalidated consequence.</p>
          </article>
          <article class="component-card reveal">
            <h3>Canonical Plane</h3>
            <p>Accepts only promoted, governed, replayable commitments.</p>
          </article>
          <article class="component-card reveal">
            <h3>Audit Chain</h3>
            <p>Records who acted, what was proposed, what was denied or allowed, and which authority path existed.</p>
          </article>
          <article class="component-card reveal">
            <h3>Continuity Gate</h3>
            <p>Requires verified state continuity before action. No continuity proof, no action.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="wrap cta-shell reveal">
        <div>
          <div class="eyebrow">Architectural consequence</div>
          <h2>The constitution is executable only if the runtime obeys it first.</h2>
          <p>That is the difference between policy text and governed substrate.</p>
        </div>
        <div class="hero-actions">
          <a class="button primary" href="repository.html">Inspect repository surface</a>
          <a class="button ghost" href="publications.html">Read formal record</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>Project-AI · Architecture</span>
      <span>Invalid action must be unreachable.</span>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>

================================================================================
FILE: publications.html
================================================================================
<!doctype html>
<html lang="en" data-page="publications">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publications | Project-AI</title>
  <meta name="description" content="A DOI-centered publication surface for Project-AI governance, execution safety, constitutional architecture, and auditability." />
  <meta name="theme-color" content="#05070b" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="site-noise" aria-hidden="true"></div>
  <div class="site-grid" aria-hidden="true"></div>
  <div class="cursor-glow" aria-hidden="true"></div>

  <header class="topbar" data-header>
    <a class="brand" href="index.html" aria-label="Project-AI home">
      <span class="brand-mark">PAI</span>
      <span class="brand-copy">
        <strong>Project-AI</strong>
        <em>Execution-Governed Substrate</em>
      </span>
    </a>
    <button class="nav-toggle" data-nav-toggle aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" data-nav>
      <a href="index.html" data-nav-link="home">Home</a>
      <a href="architecture.html" data-nav-link="architecture">Architecture</a>
      <a href="publications.html" data-nav-link="publications">Publications</a>
      <a href="repository.html" data-nav-link="repository">Repository</a>
      <a href="about.html" data-nav-link="about">About</a>
    </nav>
  </header>

  <main>
    <section class="page-hero">
      <div class="wrap narrow reveal">
        <div class="eyebrow">Publication layer</div>
        <h1>The papers are not ornament. They are the formal pressure behind the system.</h1>
        <p>
          A DOI-centered record library for Project-AI’s governance doctrine, constitutional
          runtime architecture, syscall containment, symbolic compression, continuity, and
          execution safety.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="featured-record reveal">
          <div>
            <div class="eyebrow">Featured record</div>
            <h2>Project-AI and OctoReflex</h2>
            <p>Syscall-authoritative governance and control-theoretic containment: the argument that enforcement becomes serious when the execution layer can veto action.</p>
          </div>
          <a class="button primary" href="https://doi.org/10.5281/zenodo.18726064" target="_blank" rel="noreferrer">Open DOI</a>
        </div>

        <div class="filterbar reveal" data-filterbar>
          <button class="filter active" data-filter="all">All</button>
          <button class="filter" data-filter="governance">Governance</button>
          <button class="filter" data-filter="kernel">Kernel</button>
          <button class="filter" data-filter="constitutional">Constitutional</button>
          <button class="filter" data-filter="audit">Auditability</button>
          <button class="filter" data-filter="continuity">Continuity</button>
          <button class="filter" data-filter="symbolic">Symbolic</button>
        </div>

        <div class="records-grid" data-records>
          <article class="record-card reveal" data-topic="kernel governance audit">
            <div class="record-meta">Kernel · Governance · Audit</div>
            <h3>Project-AI and OctoReflex: Syscall-Authoritative Governance and Control-Theoretic Containment</h3>
            <p>Runtime enforcement at the syscall boundary; governance with operational teeth.</p>
            <button class="doi" data-copy="10.5281/zenodo.18726064">10.5281/zenodo.18726064</button>
          </article>

          <article class="record-card reveal" data-topic="constitutional governance">
            <div class="record-meta">Constitutional · Governance</div>
            <h3>The Sovereign Covenant</h3>
            <p>A formal covenant layer for sovereign AI entities and execution-constrained legitimacy.</p>
            <button class="doi" data-copy="10.5281/zenodo.18726221">10.5281/zenodo.18726221</button>
          </article>

          <article class="record-card reveal" data-topic="constitutional governance">
            <div class="record-meta">Charter · Constitutional</div>
            <h3>AGI Charter for Project-AI: A Binding Constitutional Framework for Sovereign AI Entities</h3>
            <p>The constitutional authority layer defining how Project-AI should bind behavior to governance.</p>
            <button class="doi" data-copy="10.5281/zenodo.18763076">10.5281/zenodo.18763076</button>
          </article>

          <article class="record-card reveal" data-topic="symbolic governance">
            <div class="record-meta">Symbolic · Protocol</div>
            <h3>Thirsty’s Symbolic Compression Grammar</h3>
            <p>A compact symbolic grammar for expressing governance, cognition, and execution flow.</p>
            <button class="doi" data-copy="10.5281/zenodo.18794292">10.5281/zenodo.18794292</button>
          </article>

          <article class="record-card reveal" data-topic="symbolic audit">
            <div class="record-meta">Symbolic · Binary</div>
            <h3>TSCG-B: Binary Encoding for Constitutional Wire Protocols</h3>
            <p>A compression and transport layer for governed decision structures.</p>
            <button class="doi" data-copy="10.5281/zenodo.18826409">10.5281/zenodo.18826409</button>
          </article>

          <article class="record-card reveal" data-topic="constitutional governance">
            <div class="record-meta">Architecture · Constitutional</div>
            <h3>Constitutional Architectures for Execution-Governed AI</h3>
            <p>The formal architecture lane: governance below the application layer.</p>
            <button class="doi" data-copy="10.5281/zenodo.18794646">10.5281/zenodo.18794646</button>
          </article>

          <article class="record-card reveal" data-topic="continuity governance">
            <div class="record-meta">Continuity · Temporal</div>
            <h3>The Flat Gap</h3>
            <p>Temporal dissonance, continuity failure, and the requirement that state must be verified before action.</p>
            <button class="doi" data-copy="10.5281/zenodo.18827649">10.5281/zenodo.18827649</button>
          </article>

          <article class="record-card reveal" data-topic="continuity audit">
            <div class="record-meta">State · Continuity</div>
            <h3>The State Register</h3>
            <p>Continuity cannot be assumed. It must be verified at runtime before action is allowed.</p>
            <button class="doi" data-copy="10.5281/zenodo.19101877">10.5281/zenodo.19101877</button>
          </article>

          <article class="record-card reveal" data-topic="governance audit">
            <div class="record-meta">Doctrine · Governance</div>
            <h3>The Directness Doctrine</h3>
            <p>Execution clarity, direct authority, and rejection of vague control surfaces.</p>
            <button class="doi" data-copy="10.5281/zenodo.19030041">10.5281/zenodo.19030041</button>
          </article>

          <article class="record-card reveal" data-topic="governance audit">
            <div class="record-meta">Reviewer Model · Audit</div>
            <h3>Naive Passive Reviewer</h3>
            <p>A critique of passive review patterns that mistake observation for enforced control.</p>
            <button class="doi" data-copy="10.5281/zenodo.19453224">10.5281/zenodo.19453224</button>
          </article>

          <article class="record-card reveal" data-topic="governance constitutional audit">
            <div class="record-meta">Synthesis · Constitutional</div>
            <h3>Project-AI Cross-Linking Corpus</h3>
            <p>A higher-level synthesis connecting the governance, runtime, continuity, and auditability papers.</p>
            <button class="doi" data-copy="10.5281/zenodo.19592336">10.5281/zenodo.19592336</button>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="wrap cta-shell reveal">
        <div>
          <div class="eyebrow">Record posture</div>
          <h2>Every claim should point somewhere inspectable.</h2>
          <p>The publication layer exists to prevent the site from becoming a slogan surface.</p>
        </div>
        <div class="hero-actions">
          <a class="button primary" href="https://zenodo.org/communities/thirstysprojects-zc/records?q=&l=list&p=1&s=10&sort=newest" target="_blank" rel="noreferrer">Open Zenodo community</a>
          <a class="button ghost" href="repository.html">Inspect codebase</a>
        </div>
      </div>
    </section>
  </main>

  <div class="toast" data-toast>Copied DOI</div>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>Project-AI · Publications</span>
      <span>Proof before trust.</span>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>

================================================================================
FILE: repository.html
================================================================================
<!doctype html>
<html lang="en" data-page="repository">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repository | Project-AI</title>
  <meta name="description" content="Repository proof surface for Project-AI: monolithic architecture, governance, TARL, kernel, canonical replay, tests, and deployment surfaces." />
  <meta name="theme-color" content="#05070b" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="site-noise" aria-hidden="true"></div>
  <div class="site-grid" aria-hidden="true"></div>
  <div class="cursor-glow" aria-hidden="true"></div>

  <header class="topbar" data-header>
    <a class="brand" href="index.html" aria-label="Project-AI home">
      <span class="brand-mark">PAI</span>
      <span class="brand-copy">
        <strong>Project-AI</strong>
        <em>Execution-Governed Substrate</em>
      </span>
    </a>
    <button class="nav-toggle" data-nav-toggle aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" data-nav>
      <a href="index.html" data-nav-link="home">Home</a>
      <a href="architecture.html" data-nav-link="architecture">Architecture</a>
      <a href="publications.html" data-nav-link="publications">Publications</a>
      <a href="repository.html" data-nav-link="repository">Repository</a>
      <a href="about.html" data-nav-link="about">About</a>
    </nav>
  </header>

  <main>
    <section class="page-hero">
      <div class="wrap narrow reveal">
        <div class="eyebrow">Repository surface</div>
        <h1>The codebase is the credibility layer.</h1>
        <p>
          Project-AI is presented as a monolithic governed runtime: governance, kernel,
          TARL, canonical replay, Temporal agents, tests, CI, documentation, and release
          infrastructure in one inspectable body of work.
        </p>
        <div class="hero-actions">
          <a class="button primary" href="https://github.com/IAmSoThirsty/Project-AI" target="_blank" rel="noreferrer">Open GitHub repository</a>
          <a class="button ghost" href="architecture.html">Map architecture</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap repo-console reveal">
        <div class="panel-topline">
          <span class="status-dot"></span>
          <span>Repository posture · visible depth</span>
        </div>
        <pre class="terminal large"><code><span class="prompt">$</span> tree project-ai --selected

governance/        constitutional authority, quorum, policy surfaces
kernel/            execution boundaries, runtime hooks, enforcement logic
tarl/              Thirsty's Active Resistance Language runtime
canonical/         replayable spine, invariants, external validation route
temporal/          schedule-aware continuity agents and workflow fabric
cognition/         memory, reflection, context, agent orchestration
security/          red-team, containment, audit, adversarial pressure
desktop/           native interface and operator control surfaces
web/               browser surface and deployment interface
docs/              system maps, architecture, runbooks, release record
tests/             regression, integration, adversarial validation</code></pre>
      </div>
    </section>

    <section class="section dark-ridge">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <div class="eyebrow">Selected directories</div>
            <h2>The repo should feel alive, not decorative.</h2>
          </div>
        </div>

        <div class="directory-grid">
          <article class="directory-card reveal">
            <span>/governance</span>
            <h3>Authority surface</h3>
            <p>Policy, quorum, constitutional validation, and action legitimacy.</p>
          </article>
          <article class="directory-card reveal">
            <span>/kernel</span>
            <h3>Execution substrate</h3>
            <p>Runtime boundary where permission becomes enforceable or irrelevant.</p>
          </article>
          <article class="directory-card reveal">
            <span>/tarl</span>
            <h3>Resistance language</h3>
            <p>Policy-aware execution and low-level containment grammar.</p>
          </article>
          <article class="directory-card reveal">
            <span>/canonical</span>
            <h3>Golden path</h3>
            <p>Demonstrable replay, invariant validation, and external proof route.</p>
          </article>
          <article class="directory-card reveal">
            <span>/temporal</span>
            <h3>Continuity fabric</h3>
            <p>Event-driven scheduling, state continuity, workflow preservation.</p>
          </article>
          <article class="directory-card reveal">
            <span>/docs</span>
            <h3>Readable system memory</h3>
            <p>Architecture, deployment, governance, runbooks, and public proof.</p>
          </article>
          <article class="directory-card reveal">
            <span>/tests</span>
            <h3>Regression pressure</h3>
            <p>Validation paths intended to detect drift, bypass, and brittle claims.</p>
          </article>
          <article class="directory-card reveal">
            <span>/web</span>
            <h3>Public interface</h3>
            <p>The surface where the governed system becomes inspectable.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap split">
        <div class="section-head reveal">
          <div class="eyebrow">Engineering posture</div>
          <h2>No external microservice mythology. One body. Many governed organs.</h2>
        </div>
        <div class="text-stack reveal">
          <p>
            The repository posture is intentionally monolithic. Not because separation is
            impossible, but because governance loses force when execution authority is
            scattered across ungoverned seams.
          </p>
          <p>
            Project-AI’s public framing should emphasize that a serious governance substrate
            must know where action crosses from proposal into consequence.
          </p>
          <p>
            The website should push viewers into the repo with enough context to understand
            what they are looking for: invariants, gates, replay, audit, continuity, and
            mutation authority.
          </p>
        </div>
      </div>
    </section>

    <section class="section proof-surface">
      <div class="wrap">
        <div class="section-head centered reveal">
          <div class="eyebrow">Workflow surface</div>
          <h2>The inspection route.</h2>
        </div>

        <div class="workflow-grid">
          <article class="workflow-card reveal">
            <strong>01</strong>
            <h3>Read the README</h3>
            <p>Establish the top-level claim and the monolithic system map.</p>
          </article>
          <article class="workflow-card reveal">
            <strong>02</strong>
            <h3>Inspect canonical replay</h3>
            <p>Look for a deterministic demonstration, not a marketing claim.</p>
          </article>
          <article class="workflow-card reveal">
            <strong>03</strong>
            <h3>Trace governance routes</h3>
            <p>Find how action is routed through policy and quorum surfaces.</p>
          </article>
          <article class="workflow-card reveal">
            <strong>04</strong>
            <h3>Verify tests</h3>
            <p>Look for adversarial coverage, bypass checks, and regression barriers.</p>
          </article>
          <article class="workflow-card reveal">
            <strong>05</strong>
            <h3>Compare papers</h3>
            <p>Map repo concepts back to DOI-backed theory and doctrine.</p>
          </article>
          <article class="workflow-card reveal">
            <strong>06</strong>
            <h3>Check release posture</h3>
            <p>Inspect CI, dependency boundaries, audit logs, and deployment path.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="wrap cta-shell reveal">
        <div>
          <div class="eyebrow">Repository demand</div>
          <h2>Do not merely say it governs itself. Show the route where governance becomes execution.</h2>
        </div>
        <div class="hero-actions">
          <a class="button primary" href="https://github.com/IAmSoThirsty/Project-AI" target="_blank" rel="noreferrer">Inspect GitHub</a>
          <a class="button ghost" href="publications.html">Compare publications</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>Project-AI · Repository</span>
      <span>Visible code depth.</span>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>

================================================================================
FILE: about.html
================================================================================
<!doctype html>
<html lang="en" data-page="about">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>About | Project-AI</title>
  <meta name="description" content="About Jeremy Karrick / IAmSoThirsty and Project-AI's execution-governed AI work." />
  <meta name="theme-color" content="#05070b" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="site-noise" aria-hidden="true"></div>
  <div class="site-grid" aria-hidden="true"></div>
  <div class="cursor-glow" aria-hidden="true"></div>

  <header class="topbar" data-header>
    <a class="brand" href="index.html" aria-label="Project-AI home">
      <span class="brand-mark">PAI</span>
      <span class="brand-copy">
        <strong>Project-AI</strong>
        <em>Execution-Governed Substrate</em>
      </span>
    </a>
    <button class="nav-toggle" data-nav-toggle aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" data-nav>
      <a href="index.html" data-nav-link="home">Home</a>
      <a href="architecture.html" data-nav-link="architecture">Architecture</a>
      <a href="publications.html" data-nav-link="publications">Publications</a>
      <a href="repository.html" data-nav-link="repository">Repository</a>
      <a href="about.html" data-nav-link="about">About</a>
    </nav>
  </header>

  <main>
    <section class="page-hero">
      <div class="wrap narrow reveal">
        <div class="eyebrow">About / Contact</div>
        <h1>Built from the position that governance must be executable or it is not governance.</h1>
        <p>
          Project-AI is the work of Jeremy Karrick / IAmSoThirsty: a public architecture
          project centered on execution-governed AI systems, constitutional substrates,
          runtime admissibility, and proof-bearing action boundaries.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="wrap about-grid">
        <article class="identity-card reveal">
          <div class="identity-sigil">JK</div>
          <div>
            <div class="eyebrow">Founder lane</div>
            <h2>Jeremy Karrick</h2>
            <p>IAmSoThirsty · Project-AI · Thirstys Projects</p>
          </div>
        </article>

        <article class="founder-statement reveal">
          <h3>Founder statement</h3>
          <p>
            Most AI governance is written as if the problem is persuasion. Project-AI is
            written as if the problem is execution. The central question is not whether
            a system can describe its values. The central question is whether an invalid
            action can physically reach consequence.
          </p>
          <p>
            The work exists to move AI governance away from decorative policy and toward
            enforced admissibility: identity, scope, invariants, quorum, audit, continuity,
            and replay.
          </p>
        </article>
      </div>
    </section>

    <section class="section dark-ridge">
      <div class="wrap">
        <div class="section-head centered reveal">
          <div class="eyebrow">Contact surfaces</div>
          <h2>Follow the artifacts.</h2>
        </div>

        <div class="contact-grid">
          <a class="contact-card reveal" href="https://github.com/IAmSoThirsty/Project-AI" target="_blank" rel="noreferrer">
            <span>GitHub</span>
            <h3>IAmSoThirsty / Project-AI</h3>
            <p>Repository, code, release surface, system structure, and public implementation trail.</p>
          </a>
          <a class="contact-card reveal" href="https://zenodo.org/communities/thirstysprojects-zc/records?q=&l=list&p=1&s=10&sort=newest" target="_blank" rel="noreferrer">
            <span>Zenodo</span>
            <h3>Thirstys Projects</h3>
            <p>Publication corpus, DOI records, governance papers, constitutional architecture work.</p>
          </a>
          <a class="contact-card reveal" href="repository.html">
            <span>Local route</span>
            <h3>Repository proof page</h3>
            <p>The guided route for technical visitors before they inspect the full source tree.</p>
          </a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap split">
        <div class="section-head reveal">
          <div class="eyebrow">Position</div>
          <h2>Execution-governed AI is not a tone. It is an enforcement architecture.</h2>
        </div>
        <div class="text-stack reveal">
          <p>
            A constitution that cannot block execution is a suggestion.
          </p>
          <p>
            A policy that cannot survive tool use, memory mutation, state drift, and
            multi-step composition is not governance.
          </p>
          <p>
            A system that cannot reconstruct why an action occurred is not accountable.
          </p>
          <p>
            Project-AI exists in the gap between language-level alignment and substrate-level
            authority.
          </p>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="wrap cta-shell reveal">
        <div>
          <div class="eyebrow">Inspection path</div>
          <h2>The correct next step is not belief. It is examination.</h2>
        </div>
        <div class="hero-actions">
          <a class="button primary" href="architecture.html">Study architecture</a>
          <a class="button ghost" href="publications.html">Open DOI layer</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>Project-AI · About</span>
      <span>IAmSoThirsty.</span>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>

================================================================================
FILE: styles.css
================================================================================
:root {
  --bg: #05070b;
  --bg-2: #080d14;
  --bg-3: #0c121d;
  --panel: rgba(12, 18, 29, 0.74);
  --panel-strong: rgba(16, 24, 39, 0.9);
  --line: rgba(149, 179, 218, 0.17);
  --line-strong: rgba(176, 203, 241, 0.31);
  --text: #edf4ff;
  --muted: #9aa9bd;
  --muted-2: #6f7d90;
  --blue: #70a7ff;
  --blue-2: #2f6fff;
  --violet: #a78bfa;
  --amber: #d8a749;
  --green: #7ee7b2;
  --red: #ff7c8b;
  --shadow: 0 24px 90px rgba(0, 0, 0, 0.55);
  --radius: 26px;
  --radius-sm: 16px;
  --max: 1180px;
  --font: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  background: var(--bg);
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--font);
  color: var(--text);
  background:
    radial-gradient(circle at 20% -10%, rgba(47, 111, 255, 0.24), transparent 34rem),
    radial-gradient(circle at 78% 12%, rgba(167, 139, 250, 0.16), transparent 28rem),
    radial-gradient(circle at 50% 90%, rgba(216, 167, 73, 0.08), transparent 34rem),
    linear-gradient(180deg, #05070b 0%, #08101a 42%, #05070b 100%);
  overflow-x: hidden;
}

a {
  color: inherit;
  text-decoration: none;
}

p {
  color: var(--muted);
  line-height: 1.75;
}

button,
input,
textarea {
  font: inherit;
}

.site-noise {
  position: fixed;
  inset: 0;
  opacity: 0.05;
  pointer-events: none;
  z-index: 0;
  background-image:
    repeating-radial-gradient(circle at 20% 30%, rgba(255,255,255,0.8) 0 1px, transparent 1px 3px);
  mix-blend-mode: screen;
}

.site-grid {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(112, 167, 255, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(112, 167, 255, 0.05) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(to bottom, rgba(0,0,0,0.95), transparent 82%);
}

.cursor-glow {
  position: fixed;
  width: 460px;
  height: 460px;
  border-radius: 999px;
  pointer-events: none;
  z-index: 1;
  opacity: 0.22;
  background: radial-gradient(circle, rgba(112, 167, 255, 0.28), transparent 67%);
  transform: translate(-50%, -50%);
  left: 50%;
  top: 18%;
  transition: opacity 220ms ease;
}

.wrap {
  width: min(var(--max), calc(100% - 40px));
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.narrow {
  max-width: 900px;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: 76px;
  padding: 14px clamp(18px, 4vw, 44px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(149, 179, 218, 0.12);
  background: rgba(5, 7, 11, 0.72);
  backdrop-filter: blur(22px);
}

.topbar.scrolled {
  background: rgba(5, 7, 11, 0.92);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.34);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(112, 167, 255, 0.48);
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(112, 167, 255, 0.18), rgba(167, 139, 250, 0.10)),
    rgba(255, 255, 255, 0.02);
  color: #dceaff;
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  box-shadow: inset 0 0 24px rgba(112, 167, 255, 0.12);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-copy strong {
  font-size: 0.97rem;
  letter-spacing: 0.02em;
}

.brand-copy em {
  color: var(--muted-2);
  font-style: normal;
  font-size: 0.78rem;
}

.nav {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav a {
  color: var(--muted);
  padding: 11px 14px;
  border-radius: 999px;
  font-size: 0.88rem;
  transition: color 180ms ease, background 180ms ease, border-color 180ms ease;
  border: 1px solid transparent;
}

.nav a:hover,
.nav a.active {
  color: var(--text);
  background: rgba(112, 167, 255, 0.08);
  border-color: rgba(112, 167, 255, 0.18);
}

.nav-toggle {
  display: none;
  width: 44px;
  height: 44px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 10px;
}

.nav-toggle span {
  display: block;
  height: 2px;
  background: var(--text);
  margin: 5px 0;
  border-radius: 2px;
}

.hero {
  padding: clamp(80px, 9vw, 140px) 0 62px;
  position: relative;
}

.home-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(115deg, transparent 0 47%, rgba(112,167,255,0.08) 47.1%, transparent 48% 100%),
    linear-gradient(65deg, transparent 0 58%, rgba(216,167,73,0.07) 58.1%, transparent 59% 100%);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.92fr);
  align-items: center;
  gap: clamp(28px, 5vw, 70px);
}

.eyebrow {
  color: var(--amber);
  font-family: var(--mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

h1,
h2,
h3 {
  margin: 0;
  color: var(--text);
  letter-spacing: -0.045em;
  line-height: 0.96;
}

h1 {
  font-size: clamp(3.1rem, 8vw, 7.8rem);
  max-width: 12ch;
  margin-top: 20px;
}

h2 {
  font-size: clamp(2rem, 4.6vw, 4.3rem);
}

h3 {
  font-size: clamp(1.2rem, 2vw, 1.65rem);
  line-height: 1.08;
}

.gradient-text {
  display: block;
  background: linear-gradient(105deg, #ffffff 0%, #a9c9ff 42%, #a78bfa 70%, #e3bd68 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-copy {
  max-width: 65ch;
  margin: 28px 0 0;
  font-size: clamp(1.04rem, 1.6vw, 1.24rem);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 13px;
  margin-top: 30px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 20px;
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  font-weight: 650;
  font-size: 0.92rem;
  transition: transform 180ms ease, background 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.button:hover {
  transform: translateY(-2px);
}

.button.primary {
  background:
    linear-gradient(135deg, rgba(112, 167, 255, 0.95), rgba(99, 102, 241, 0.88));
  color: #07101d;
  border-color: rgba(186, 211, 255, 0.8);
  box-shadow: 0 18px 50px rgba(47, 111, 255, 0.22);
}

.button.ghost {
  background: rgba(255,255,255,0.035);
  color: var(--text);
}

.text-link {
  color: #cfe1ff;
  border-bottom: 1px solid rgba(112, 167, 255, 0.5);
  padding-bottom: 3px;
}

.hero-panel,
.repo-console,
.featured-record,
.proof-shell,
.cta-shell,
.identity-card,
.founder-statement {
  border: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018)),
    var(--panel);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
}

.hero-panel {
  padding: 22px;
  position: relative;
  overflow: hidden;
}

.hero-panel::before,
.repo-console::before,
.featured-record::before,
.cta-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(112,167,255,0.18), transparent 34%),
    linear-gradient(315deg, rgba(216,167,73,0.12), transparent 38%);
  opacity: 0.72;
}

.panel-topline {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--muted);
  font-size: 0.82rem;
  font-family: var(--mono);
  margin-bottom: 18px;
  position: relative;
  z-index: 1;
}

.status-dot {
  width: 9px;
  height: 9px;
  background: var(--green);
  box-shadow: 0 0 18px rgba(126, 231, 178, 0.8);
  border-radius: 999px;
}

.terminal {
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 22px;
  overflow: auto;
  border-radius: 18px;
  border: 1px solid rgba(149, 179, 218, 0.14);
  background: rgba(0, 0, 0, 0.42);
  color: #d9e8ff;
  font-family: var(--mono);
  font-size: 0.86rem;
  line-height: 1.72;
  white-space: pre-wrap;
}

.terminal.large {
  font-size: 0.91rem;
}

.prompt { color: var(--amber); }
.dim { color: var(--muted-2); }
.ok { color: var(--green); }
.warn { color: var(--amber); }

.metrics-band {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  margin-top: clamp(42px, 6vw, 84px);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--line);
}

.metrics-band article {
  min-height: 132px;
  padding: 24px;
  background: rgba(8, 13, 20, 0.82);
}

.metrics-band strong {
  display: block;
  font-size: 1.28rem;
  margin-bottom: 10px;
}

.metrics-band span {
  color: var(--muted);
  line-height: 1.55;
}

.section {
  padding: clamp(72px, 9vw, 126px) 0;
  position: relative;
}

.dark-ridge {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background:
    radial-gradient(circle at 78% 18%, rgba(112,167,255,0.12), transparent 30rem),
    linear-gradient(180deg, rgba(12,18,29,0.42), rgba(5,7,11,0.25));
}

.split {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.1fr);
  gap: clamp(32px, 6vw, 76px);
  align-items: start;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 34px;
}

.section-head.centered {
  text-align: center;
  max-width: 840px;
  margin: 0 auto 44px;
  display: block;
}

.section-head h2 {
  margin-top: 14px;
}

.section-head p {
  max-width: 66ch;
  margin-inline: auto;
}

.doctrine-stack {
  display: grid;
  gap: 14px;
}

.glass-card,
.proof-card,
.component-card,
.directory-card,
.workflow-card,
.record-card,
.contact-card,
.pillar,
.timeline-item {
  border: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.052), rgba(255,255,255,0.018));
  border-radius: var(--radius-sm);
  padding: 24px;
  box-shadow: 0 18px 70px rgba(0,0,0,0.22);
  position: relative;
  overflow: hidden;
}

.glass-card::after,
.proof-card::after,
.component-card::after,
.directory-card::after,
.workflow-card::after,
.record-card::after,
.contact-card::after,
.pillar::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(112,167,255,0.45), transparent);
}

.card-index {
  display: inline-flex;
  color: var(--amber);
  font-family: var(--mono);
  margin-bottom: 18px;
}

.triad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.pillar {
  min-height: 370px;
}

.pillar-orb {
  width: 72px;
  height: 72px;
  border-radius: 999px;
  margin-bottom: 28px;
  border: 1px solid rgba(255,255,255,0.25);
}

.pillar-orb.galahad {
  background: radial-gradient(circle, rgba(216,167,73,0.9), rgba(216,167,73,0.05) 65%, transparent 70%);
  box-shadow: 0 0 42px rgba(216,167,73,0.2);
}

.pillar-orb.cerberus {
  background: radial-gradient(circle, rgba(255,124,139,0.84), rgba(255,124,139,0.05) 65%, transparent 70%);
  box-shadow: 0 0 42px rgba(255,124,139,0.2);
}

.pillar-orb.codex {
  background: radial-gradient(circle, rgba(112,167,255,0.9), rgba(112,167,255,0.05) 65%, transparent 70%);
  box-shadow: 0 0 42px rgba(112,167,255,0.22);
}

.pillar ul,
.contact-card ul {
  padding-left: 18px;
  color: var(--muted);
  line-height: 1.75;
}

.flowline {
  display: flex;
  align-items: center;
  overflow-x: auto;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255,255,255,0.025);
}

.flow-node {
  min-width: 132px;
  padding: 18px 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  text-align: center;
  background: rgba(8, 13, 20, 0.86);
  color: #dceaff;
  font-family: var(--mono);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.flow-node.emph {
  color: #07101d;
  background: linear-gradient(135deg, var(--amber), #e7cc86);
  border-color: rgba(255,255,255,0.5);
}

.flow-arrow {
  min-width: 42px;
  height: 1px;
  background: linear-gradient(90deg, rgba(112,167,255,0.2), rgba(112,167,255,0.9));
  position: relative;
}

.flow-arrow::after {
  content: "";
  position: absolute;
  right: 0;
  top: -4px;
  width: 8px;
  height: 8px;
  border-top: 1px solid rgba(112,167,255,0.9);
  border-right: 1px solid rgba(112,167,255,0.9);
  transform: rotate(45deg);
}

.proof-grid,
.component-grid,
.directory-grid,
.workflow-grid,
.records-grid,
.contact-grid {
  display: grid;
  gap: 16px;
}

.proof-grid {
  grid-template-columns: repeat(4, 1fr);
  margin-top: 22px;
}

.component-grid,
.directory-grid,
.workflow-grid,
.records-grid {
  grid-template-columns: repeat(3, 1fr);
}

.proof-surface {
  background:
    radial-gradient(circle at 25% 15%, rgba(167,139,250,0.12), transparent 34rem),
    radial-gradient(circle at 80% 60%, rgba(112,167,255,0.08), transparent 30rem);
}

.proof-shell,
.cta-shell,
.featured-record {
  padding: clamp(28px, 5vw, 54px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 28px;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.receipt-stack {
  min-width: min(100%, 360px);
  display: grid;
  gap: 12px;
}

.receipt {
  display: block;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(0,0,0,0.24);
  transition: transform 180ms ease, border-color 180ms ease;
}

.receipt:hover {
  transform: translateX(4px);
  border-color: rgba(112,167,255,0.42);
}

.receipt span,
.directory-card span,
.contact-card span,
.record-meta {
  display: block;
  color: var(--amber);
  font-family: var(--mono);
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  margin-bottom: 10px;
}

.receipt strong {
  display: block;
}

.page-hero {
  padding: clamp(82px, 10vw, 146px) 0 clamp(46px, 7vw, 76px);
  border-bottom: 1px solid var(--line);
}

.page-hero h1 {
  max-width: 13ch;
}

.page-hero p {
  font-size: clamp(1.05rem, 1.6vw, 1.25rem);
  max-width: 72ch;
  margin-top: 26px;
}

.system-map {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 22px;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
  box-shadow: var(--shadow);
}

.map-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.map-row.three {
  grid-template-columns: repeat(3, 1fr);
}

.map-cell {
  min-height: 82px;
  display: grid;
  place-items: center;
  text-align: center;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(5, 7, 11, 0.64);
  color: #dceaff;
  font-weight: 650;
}

.map-cell.muted {
  color: var(--muted);
}

.map-cell.strong {
  background: linear-gradient(135deg, rgba(216,167,73,0.28), rgba(112,167,255,0.10));
  border-color: rgba(216,167,73,0.38);
}

.map-cell.violet {
  border-color: rgba(167,139,250,0.32);
}

.map-cell.amber {
  border-color: rgba(216,167,73,0.32);
}

.map-cell.blue {
  border-color: rgba(112,167,255,0.32);
}

.map-line {
  width: 1px;
  height: 36px;
  margin: 0 auto;
  background: linear-gradient(180deg, rgba(112,167,255,0.2), rgba(112,167,255,0.8), rgba(112,167,255,0.2));
}

.text-stack p {
  font-size: 1.04rem;
  margin-top: 0;
}

.timeline {
  position: relative;
  display: grid;
  gap: 16px;
  max-width: 860px;
  margin: 0 auto;
}

.timeline::before {
  content: "";
  position: absolute;
  left: 25px;
  top: 20px;
  bottom: 20px;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(112,167,255,0.7), transparent);
}

.timeline-item {
  padding-left: 78px;
}

.timeline-item span {
  position: absolute;
  left: 18px;
  top: 24px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(112,167,255,0.14);
  border: 1px solid rgba(112,167,255,0.32);
  color: #cfe1ff;
  font-family: var(--mono);
  font-size: 0.76rem;
}

.featured-record h2 {
  margin-top: 12px;
}

.filterbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 26px 0;
}

.filter {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.035);
  color: var(--muted);
  cursor: pointer;
  transition: color 180ms ease, background 180ms ease, border-color 180ms ease;
}

.filter.active,
.filter:hover {
  color: var(--text);
  background: rgba(112,167,255,0.12);
  border-color: rgba(112,167,255,0.38);
}

.record-card {
  min-height: 268px;
  display: flex;
  flex-direction: column;
}

.record-card.is-hidden {
  display: none;
}

.doi {
  margin-top: auto;
  border: 1px solid rgba(112,167,255,0.28);
  background: rgba(112,167,255,0.08);
  color: #cfe1ff;
  border-radius: 999px;
  padding: 10px 12px;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 0.78rem;
  text-align: left;
}

.doi:hover {
  background: rgba(112,167,255,0.15);
}

.toast {
  position: fixed;
  right: 22px;
  bottom: 22px;
  z-index: 80;
  transform: translateY(16px);
  opacity: 0;
  pointer-events: none;
  border: 1px solid var(--line);
  background: rgba(8,13,20,0.92);
  color: var(--text);
  border-radius: 999px;
  padding: 12px 16px;
  box-shadow: var(--shadow);
  transition: opacity 180ms ease, transform 180ms ease;
}

.toast.show {
  transform: translateY(0);
  opacity: 1;
}

.repo-console {
  position: relative;
  overflow: hidden;
  padding: 22px;
}

.workflow-card strong {
  color: var(--amber);
  font-family: var(--mono);
}

.about-grid {
  display: grid;
  grid-template-columns: 0.78fr 1.22fr;
  gap: 18px;
}

.identity-card,
.founder-statement {
  padding: clamp(28px, 5vw, 44px);
}

.identity-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 420px;
}

.identity-sigil {
  width: 118px;
  height: 118px;
  display: grid;
  place-items: center;
  border-radius: 34px;
  border: 1px solid rgba(112,167,255,0.44);
  background:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,0.22), transparent 30%),
    linear-gradient(135deg, rgba(112,167,255,0.35), rgba(167,139,250,0.14));
  font-size: 2.1rem;
  font-family: var(--mono);
  letter-spacing: 0.1em;
  box-shadow: inset 0 0 42px rgba(112,167,255,0.18);
}

.contact-grid {
  grid-template-columns: repeat(3, 1fr);
}

.contact-card {
  display: block;
  min-height: 230px;
}

.footer {
  border-top: 1px solid var(--line);
  padding: 26px 0;
  color: var(--muted-2);
  position: relative;
  z-index: 2;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  font-size: 0.86rem;
}

.reveal {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 700ms ease, transform 700ms ease;
}

.reveal.in {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 980px) {
  .hero-grid,
  .split,
  .proof-shell,
  .cta-shell,
  .featured-record,
  .about-grid {
    grid-template-columns: 1fr;
  }

  .metrics-band,
  .triad,
  .proof-grid,
  .component-grid,
  .directory-grid,
  .workflow-grid,
  .records-grid,
  .contact-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-hero h1,
  h1 {
    max-width: 100%;
  }
}

@media (max-width: 760px) {
  .topbar {
    min-height: 68px;
  }

  .nav-toggle {
    display: block;
    position: relative;
    z-index: 60;
  }

  .nav {
    position: fixed;
    inset: 76px 16px auto 16px;
    display: none;
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
    border: 1px solid var(--line);
    border-radius: 22px;
    background: rgba(5, 7, 11, 0.96);
    box-shadow: var(--shadow);
  }

  .nav.open {
    display: flex;
  }

  .nav a {
    border-radius: 14px;
  }

  .brand-copy em {
    display: none;
  }

  .hero {
    padding-top: 70px;
  }

  .metrics-band,
  .triad,
  .proof-grid,
  .component-grid,
  .directory-grid,
  .workflow-grid,
  .records-grid,
  .contact-grid,
  .map-row.three {
    grid-template-columns: 1fr;
  }

  .flowline {
    align-items: stretch;
  }

  .flow-node {
    min-width: 152px;
  }

  .footer-inner {
    flex-direction: column;
  }

  .timeline::before {
    left: 18px;
  }

  .timeline-item {
    padding-left: 60px;
  }

  .timeline-item span {
    left: 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition: none !important;
    animation: none !important;
  }

  .cursor-glow {
    display: none;
  }

  .reveal {
    opacity: 1;
    transform: none;
  }
}

================================================================================
FILE: app.js
================================================================================
(function () {
  const root = document.documentElement;
  const page = root.dataset.page || document.body.dataset.page;

  const navLinks = document.querySelectorAll("[data-nav-link]");
  navLinks.forEach((link) => {
    if (link.dataset.navLink === page) link.classList.add("active");
  });

  const header = document.querySelector("[data-header]");
  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 12);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const navToggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    nav.addEventListener("click", (event) => {
      const target = event.target;
      if (target instanceof HTMLAnchorElement) {
        nav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  const revealTargets = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealTargets.forEach((el, index) => {
      el.style.transitionDelay = `${Math.min(index * 34, 220)}ms`;
      observer.observe(el);
    });
  } else {
    revealTargets.forEach((el) => el.classList.add("in"));
  }

  const glow = document.querySelector(".cursor-glow");
  if (glow && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    let x = window.innerWidth * 0.5;
    let y = window.innerHeight * 0.18;
    let tx = x;
    let ty = y;

    window.addEventListener(
      "pointermove",
      (event) => {
        tx = event.clientX;
        ty = event.clientY;
      },
      { passive: true }
    );

    const animateGlow = () => {
      x += (tx - x) * 0.055;
      y += (ty - y) * 0.055;
      glow.style.left = `${x}px`;
      glow.style.top = `${y}px`;
      requestAnimationFrame(animateGlow);
    };
    animateGlow();
  }

  const filterBar = document.querySelector("[data-filterbar]");
  const records = Array.from(document.querySelectorAll("[data-topic]"));

  if (filterBar && records.length) {
    filterBar.addEventListener("click", (event) => {
      const button = event.target.closest("[data-filter]");
      if (!button) return;

      const filter = button.dataset.filter;
      filterBar.querySelectorAll("[data-filter]").forEach((btn) => {
        btn.classList.toggle("active", btn === button);
      });

      records.forEach((record) => {
        const topics = record.dataset.topic || "";
        const show = filter === "all" || topics.split(" ").includes(filter);
        record.classList.toggle("is-hidden", !show);
      });
    });
  }

  const toast = document.querySelector("[data-toast]");
  let toastTimer = null;

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 1500);
  };

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.dataset.copy;
      if (!text) return;

      try {
        await navigator.clipboard.writeText(text);
        showToast("Copied DOI");
      } catch {
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
        showToast("Copied DOI");
      }
    });
  });
})();