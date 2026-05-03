/* Renders Zenodo papers grid + filter + search on papers.html and the home spotlight */
(async function () {
  const grid = document.getElementById("papers-grid");
  const spotlight = document.getElementById("papers-spotlight");
  if (!grid && !spotlight) return;

  let papers = [];
  try {
    const res = await fetch("assets/data/papers.json");
    papers = await res.json();
  } catch (e) {
    if (grid) grid.innerHTML = "<p>Could not load papers.</p>";
    return;
  }

  function fmtDate(d) {
    try {
      return new Date(d).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch { return d; }
  }

  function paperCard(p) {
    const kw = (p.keywords || []).slice(0, 4).map((k) => `<span>${k}</span>`).join("");
    return `
      <article class="paper reveal">
        <div style="display:flex;justify-content:space-between;gap:.6rem">
          <span class="doi">${p.doi}</span>
          <span class="date">${fmtDate(p.date)}</span>
        </div>
        <h3>${p.title}</h3>
        <p>${(p.abstract || "").slice(0, 240)}${(p.abstract || "").length > 240 ? "…" : ""}</p>
        <div class="keywords">${kw}</div>
        <div class="paper-foot">
          <a href="${p.doi_url}" target="_blank" rel="noopener">→ Read on Zenodo</a>
          <a href="${p.zenodo_url}" target="_blank" rel="noopener" class="muted">Record</a>
        </div>
      </article>`;
  }

  if (spotlight) {
    spotlight.innerHTML = papers.slice(0, 6).map(paperCard).join("");
  }

  if (grid) {
    const tagSet = new Set();
    papers.forEach((p) => (p.keywords || []).forEach((k) => tagSet.add(k)));
    const TOP_TAGS = [...tagSet].slice(0, 12);

    const filterRow = document.getElementById("paper-filters");
    const searchInput = document.getElementById("paper-search");

    function render(filter, q) {
      const ql = (q || "").toLowerCase().trim();
      const filtered = papers.filter((p) => {
        const inTag = !filter || filter === "All" || (p.keywords || []).includes(filter);
        const inQ = !ql || (p.title + " " + (p.abstract || "")).toLowerCase().includes(ql);
        return inTag && inQ;
      });
      grid.innerHTML = filtered.length
        ? filtered.map(paperCard).join("")
        : '<p class="muted">No papers match.</p>';
      // re-trigger reveal observer
      grid.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
    }

    if (filterRow) {
      filterRow.innerHTML =
        `<button class="filter active" data-tag="All">All · ${papers.length}</button>` +
        TOP_TAGS.map((t) => `<button class="filter" data-tag="${t}">${t}</button>`).join("");
      filterRow.addEventListener("click", (e) => {
        const b = e.target.closest(".filter");
        if (!b) return;
        filterRow.querySelectorAll(".filter").forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
        render(b.dataset.tag, searchInput?.value);
      });
    }
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const active = filterRow?.querySelector(".filter.active");
        render(active?.dataset.tag || "All", searchInput.value);
      });
    }
    render("All", "");
  }
})();
