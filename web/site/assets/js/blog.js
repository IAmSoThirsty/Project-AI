/* Blog index renderer */
(async function () {
  const grid = document.getElementById("blog-grid");
  const teaser = document.getElementById("blog-teaser");
  if (!grid && !teaser) return;
  let posts = [];
  try {
    const r = await fetch("assets/data/posts.json");
    posts = await r.json();
  } catch { if (grid) grid.innerHTML = "<p>Could not load posts.</p>"; return; }
  posts.sort((a, b) => (a.date < b.date ? 1 : -1));

  function card(p) {
    const tags = (p.tags || [])
      .map((t, i) => `<span class="tag ${i === 0 ? "cyan" : ""}">${t}</span>`)
      .join("");
    const href = p.external || `blog/${p.slug}.html`;
    const tgt = p.external ? ' target="_blank" rel="noopener"' : "";
    return `
      <a href="${href}"${tgt} class="card reveal" style="display:block">
        <div class="ix">
          <span class="mono">${new Date(p.date).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
          <span class="mono">${p.external ? "Zenodo" : "Field note"}</span>
        </div>
        <h3>${p.title}</h3>
        <p>${p.excerpt}</p>
        <div class="tags">${tags}</div>
        <div class="card-arrow">Read
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </div>
      </a>`;
  }

  if (teaser) {
    teaser.innerHTML = posts.slice(0, 3).map(card).join("");
    teaser.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
  }
  if (grid) {
    grid.innerHTML = posts.map(card).join("");
    grid.querySelectorAll(".reveal").forEach((el) => el.classList.add("visible"));
  }
})();
