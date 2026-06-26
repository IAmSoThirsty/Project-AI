/* Project gallery + tag filter — used on projects.html and home featured */
(async function () {
  const grid = document.getElementById("projects-grid");
  const featured = document.getElementById("projects-featured");
  if (!grid && !featured) return;

  let projects = [];
  try {
    const r = await fetch("assets/data/projects.json");
    projects = await r.json();
  } catch (e) {
    if (grid) grid.innerHTML = "<p>Could not load projects.</p>";
    return;
  }

  const ACCENTS = { cyan: "cyan", violet: "violet", amber: "amber", rose: "rose", emerald: "emerald" };

  function projCard(p, idx) {
    const tags = (p.tags || [])
      .slice(0, 4)
      .map((t, i) => `<span class="tag ${i === 0 ? ACCENTS[p.accent] || "cyan" : ""}">${t}</span>`)
      .join("");
    const link = p.page || p.github;
    const isInternal = !!p.page;
    const target = isInternal ? "" : ' target="_blank" rel="noopener"';
    return `
      <a href="${link}"${target} class="card reveal" style="display:block;text-decoration:none">
        <div class="ix">
          <span>${String(idx + 1).padStart(2, "0")} / ${String(projects.length).padStart(2, "0")}</span>
          <span class="mono">${(p.tags || [])[0] || ""}</span>
        </div>
        <h3>${p.name}</h3>
        <p style="margin-bottom:.6rem;color:var(--ink-2);font-size:.92rem;font-style:italic">${p.tagline}</p>
        <p>${p.summary}</p>
        <div class="tags">${tags}</div>
        <div class="card-arrow">
          ${isInternal ? "Open dossier" : "View on GitHub"}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </div>
      </a>`;
  }

  if (featured) {
    const f = projects.filter((p) => p.featured).slice(0, 6);
    featured.innerHTML = f.map(projCard).join("");
    featured.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
  }

  if (grid) {
    const tagSet = new Set();
    projects.forEach((p) => (p.tags || []).forEach((t) => tagSet.add(t)));
    const TAGS = ["All", ...[...tagSet].sort()];
    const filterRow = document.getElementById("project-filters");

    function render(tag) {
      const list = !tag || tag === "All" ? projects : projects.filter((p) => (p.tags || []).includes(tag));
      grid.innerHTML = list.map(projCard).join("");
      grid.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
    }
    if (filterRow) {
      filterRow.innerHTML = TAGS.map(
        (t, i) => `<button class="filter ${i === 0 ? "active" : ""}" data-tag="${t}">${t}</button>`
      ).join("");
      filterRow.addEventListener("click", (e) => {
        const b = e.target.closest(".filter");
        if (!b) return;
        filterRow.querySelectorAll(".filter").forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
        render(b.dataset.tag);
      });
    }
    render("All");
  }
})();
