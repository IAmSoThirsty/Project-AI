"""
Thirsty-Lang Documentation Site Generator.

Reads all Markdown files from src/utf/docs/ and generates a static HTML
documentation site.  No external dependencies required — the generator
uses stdlib only (pathlib, re, html, textwrap).

Output: docs/_site/  (default; configurable via --output)

Usage:
    python -m thirsty_lang.docs_generator
    python -m thirsty_lang.docs_generator --output /path/to/site
    thirsty docs [--output /path/to/site]

Features:
  - Table of contents sidebar with all docs
  - Per-page HTML with navigation
  - Syntax highlighting class hooks (thirsty/python/json code blocks)
  - Responsive CSS (single embedded stylesheet — no CDN required)
  - Search index (docs_search.json) for client-side keyword search
"""

from __future__ import annotations

import html
import json
import re
import shutil
import textwrap
from pathlib import Path
from typing import NamedTuple

_DOCS_DIR = Path(__file__).parents[1] / "docs"
_DEFAULT_OUTPUT = Path(__file__).parents[2] / "docs" / "_site"

# Doc ordering: human-friendly sequence for the sidebar
_DOC_ORDER = [
    "THIRSTY_LANG_SPEC",
    "THIRSTY_EBNF_GRAMMAR",
    "THIRSTY_TYPE_SYSTEM",
    "THIRSTY_RUNTIME_SEMANTICS",
    "THIRSTY_MODULE_SYSTEM",
    "THIRSTY_STANDARD_LIBRARY",
    "THIRSTY_ERROR_CODES",
    "THIRSTY_CONFORMANCE",
    "TRIUMVIRATE_SPEC",
    "PSIA_SPEC",
    "TARL_BOUNDARY",
    "SHADOW_THIRST_SPEC",
    "TSCG_ROLE",
    "TSCG_B_ROLE",
    "THIRST_OF_GODS_SPEC",
    "THIRST_MANIFESTO",
    "CANONICAL_STACK",
    "GREAT_WELLS",
    "PACKAGES_AND_GREAT_WELLS",
    "SACRED_TEXTS",
    "JS_PYTHON_PARITY",
]

_CSS = """
:root {
  --bg: #0d1117; --surface: #161b22; --border: #30363d;
  --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
  --green: #3fb950; --yellow: #d29922; --red: #f85149;
  --code-bg: #0d1117; --sidebar-w: 280px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg); color: var(--text);
  display: flex; min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Sidebar */
#sidebar {
  width: var(--sidebar-w); min-height: 100vh;
  background: var(--surface); border-right: 1px solid var(--border);
  position: fixed; top: 0; left: 0; overflow-y: auto;
  padding: 1rem 0;
}
#sidebar h1 { font-size: 1rem; color: var(--accent); padding: 0.5rem 1.25rem 1rem; border-bottom: 1px solid var(--border); }
#sidebar ul { list-style: none; padding: 0.5rem 0; }
#sidebar li a {
  display: block; padding: 0.35rem 1.25rem;
  font-size: 0.875rem; color: var(--muted);
}
#sidebar li a:hover, #sidebar li a.active {
  color: var(--text); background: rgba(88,166,255,0.08);
  text-decoration: none;
}
#sidebar .group { font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--muted); padding: 1rem 1.25rem 0.25rem; }

/* Content */
#content {
  margin-left: var(--sidebar-w); padding: 2rem 3rem;
  max-width: 900px; width: 100%;
}
h1 { font-size: 1.75rem; margin-bottom: 1rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border); }
h2 { font-size: 1.25rem; margin: 1.75rem 0 0.75rem; }
h3 { font-size: 1rem; margin: 1.25rem 0 0.5rem; color: var(--accent); }
p { line-height: 1.7; margin-bottom: 1rem; }
ul, ol { margin: 0.5rem 0 1rem 1.5rem; }
li { line-height: 1.7; margin-bottom: 0.2rem; }

/* Code */
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.875rem;
  background: var(--code-bg); color: #79c0ff;
  padding: 0.1em 0.4em; border-radius: 4px;
}
pre {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 1rem; overflow-x: auto; margin-bottom: 1rem;
}
pre code { background: none; padding: 0; color: var(--text); }
.lang-thirsty pre code .kw { color: #ff7b72; }
.lang-thirsty pre code .str { color: #a5d6ff; }
.lang-thirsty pre code .num { color: #79c0ff; }
.lang-thirsty pre code .cmt { color: var(--muted); font-style: italic; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; font-size: 0.9rem; }
th { background: var(--surface); color: var(--accent); text-align: left;
  padding: 0.5rem 0.75rem; border: 1px solid var(--border); }
td { padding: 0.4rem 0.75rem; border: 1px solid var(--border); vertical-align: top; }
tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

/* Search */
#search-box {
  width: 100%; padding: 0.4rem 0.75rem; margin-bottom: 0.5rem;
  background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
  color: var(--text); font-size: 0.875rem;
}

/* Admonitions */
.note { background: rgba(88,166,255,0.08); border-left: 3px solid var(--accent);
  padding: 0.75rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; }
.warn { background: rgba(210,153,34,0.1); border-left: 3px solid var(--yellow);
  padding: 0.75rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; }

@media (max-width: 768px) {
  #sidebar { display: none; }
  #content { margin-left: 0; padding: 1rem; }
}
"""

_JS = r"""
const idx = {};
fetch('docs_search.json').then(r => r.json()).then(data => {
  data.forEach(d => { idx[d.slug] = d; });
  document.getElementById('search-box').addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('#sidebar li[data-slug]').forEach(li => {
      const slug = li.dataset.slug;
      const doc = idx[slug] || {};
      const hay = ((doc.title || '') + ' ' + (doc.text || '')).toLowerCase();
      li.style.display = (!q || hay.includes(q)) ? '' : 'none';
    });
  });
});
// Highlight active sidebar link
const current = location.pathname.split('/').pop();
document.querySelectorAll('#sidebar a').forEach(a => {
  if (a.getAttribute('href') === current) a.classList.add('active');
});
"""


class DocPage(NamedTuple):
    stem: str          # e.g. "THIRSTY_LANG_SPEC"
    title: str
    html_body: str
    plain_text: str    # for search index


# ---------------------------------------------------------------------------
# Markdown → HTML (stdlib-only, no markdown library required)
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    return html.escape(text)


def _md_to_html(md: str) -> tuple[str, str]:
    """Convert Markdown to HTML. Returns (html_body, plain_text)."""
    lines = md.splitlines()
    out: list[str] = []
    plain: list[str] = []
    i = 0

    def _inline(text: str) -> str:
        """Process inline Markdown: bold, italic, code, links."""
        # Code spans (must come first to avoid escaping their contents)
        parts = re.split(r"`([^`]+)`", text)
        result = []
        for j, part in enumerate(parts):
            if j % 2 == 1:
                result.append(f"<code>{_escape(part)}</code>")
            else:
                # Escape HTML, then apply other inline rules
                part = _escape(part)
                # Bold **text**
                part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
                # Italic *text*
                part = re.sub(r"\*(.+?)\*", r"<em>\1</em>", part)
                # Links [text](url)
                part = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', part)
                result.append(part)
        return "".join(result)

    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_table = False
    in_list = False
    list_type = ""

    def flush_code():
        nonlocal in_code, code_lang, code_lines
        code_html = "\n".join(_escape(l) for l in code_lines)
        lang_class = f"lang-{code_lang}" if code_lang else ""
        out.append(f'<div class="{lang_class}"><pre><code>{code_html}</code></pre></div>')
        plain.extend(code_lines)
        code_lines.clear()
        in_code = False
        code_lang = ""

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            out.append(f"</{list_type}>")
            in_list = False

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            if not in_code:
                flush_list()
                in_code = True
                code_lang = line[3:].strip()
            else:
                flush_code()
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Blank line
        if not line.strip():
            flush_list()
            in_table = False
            out.append("")
            i += 1
            continue

        # ATX headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush_list()
            level = len(m.group(1))
            text = _inline(m.group(2))
            anchor = re.sub(r"[^\w\s-]", "", m.group(2).lower()).strip().replace(" ", "-")
            out.append(f'<h{level} id="{anchor}">{text}</h{level}>')
            plain.append(m.group(2))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", line):
            flush_list()
            out.append("<hr>")
            i += 1
            continue

        # Table
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|?[-| :]+\|?$", lines[i + 1]):
            flush_list()
            if not in_table:
                out.append("<table>")
                in_table = True
                # Header row
                cells = [c.strip() for c in line.strip("|").split("|")]
                out.append("<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in cells) + "</tr>")
                i += 2  # skip separator
            continue

        if in_table and "|" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells) + "</tr>")
            plain.append(" ".join(c for c in cells))
            i += 1
            continue

        if in_table:
            out.append("</table>")
            in_table = False

        # Unordered list
        m = re.match(r"^[-*+]\s+(.*)", line)
        if m:
            if not in_list or list_type != "ul":
                flush_list()
                out.append("<ul>")
                in_list = True
                list_type = "ul"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            plain.append(m.group(1))
            i += 1
            continue

        # Ordered list
        m = re.match(r"^\d+\.\s+(.*)", line)
        if m:
            if not in_list or list_type != "ol":
                flush_list()
                out.append("<ol>")
                in_list = True
                list_type = "ol"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            plain.append(m.group(1))
            i += 1
            continue

        flush_list()

        # Paragraph
        out.append(f"<p>{_inline(line)}</p>")
        plain.append(line)
        i += 1

    if in_code:
        flush_code()
    flush_list()
    if in_table:
        out.append("</table>")

    return "\n".join(out), " ".join(plain)


def _page_title(md: str, stem: str) -> str:
    """Extract the first H1 from the doc or fall back to the stem."""
    m = re.search(r"^#\s+(.+)", md, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return stem.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Site builder
# ---------------------------------------------------------------------------

def _render_page(page: DocPage, all_pages: list[DocPage], output_dir: Path) -> None:
    sidebar_links = []
    for p in all_pages:
        cls = ' class="active"' if p.stem == page.stem else ""
        sidebar_links.append(
            f'  <li data-slug="{p.stem}"><a href="{p.stem}.html"{cls}>'
            f"{_escape(p.title)}</a></li>"
        )

    sidebar_html = "\n".join(sidebar_links)

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_escape(page.title)} — Thirsty-Lang</title>
  <style>{_CSS}</style>
</head>
<body>
<nav id="sidebar">
  <h1>Thirsty-Lang</h1>
  <div style="padding: 0.5rem 1.25rem;">
    <input id="search-box" type="search" placeholder="Search docs…">
  </div>
  <ul>
{sidebar_html}
  </ul>
</nav>
<main id="content">
{page.html_body}
</main>
<script>{_JS}</script>
</body>
</html>"""

    (output_dir / f"{page.stem}.html").write_text(page_html, encoding="utf-8")


def build_site(
    docs_dir: Path | None = None,
    output_dir: Path | None = None,
    quiet: bool = False,
) -> Path:
    """
    Build the static documentation site.

    Args:
        docs_dir:   Path to Markdown source files (default: src/utf/docs/)
        output_dir: Where to write the generated site (default: docs/_site/)
        quiet:      Suppress progress output

    Returns:
        The output directory path.
    """
    if docs_dir is None:
        docs_dir = _DOCS_DIR
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT

    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect and order doc files
    all_md = {f.stem: f for f in docs_dir.glob("*.md")}
    ordered_stems: list[str] = []
    for stem in _DOC_ORDER:
        if stem in all_md:
            ordered_stems.append(stem)
    # Append any docs not in the order list
    for stem in sorted(all_md.keys()):
        if stem not in ordered_stems:
            ordered_stems.append(stem)

    pages: list[DocPage] = []
    search_index: list[dict] = []

    for stem in ordered_stems:
        md_file = all_md.get(stem)
        if md_file is None:
            continue
        md = md_file.read_text(encoding="utf-8")
        title = _page_title(md, stem)
        body_html, plain_text = _md_to_html(md)
        page = DocPage(stem=stem, title=title, html_body=body_html, plain_text=plain_text)
        pages.append(page)
        search_index.append({
            "slug": stem,
            "title": title,
            "text": plain_text[:2000],
        })
        if not quiet:
            print(f"  + {stem}.html")

    # Render all pages (done in a second pass so sidebar is complete)
    for page in pages:
        _render_page(page, pages, output_dir)

    # Write search index
    (output_dir / "docs_search.json").write_text(
        json.dumps(search_index, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write index.html redirecting to first page
    first = pages[0].stem if pages else "THIRSTY_LANG_SPEC"
    (output_dir / "index.html").write_text(
        f'<!DOCTYPE html><html><head>'
        f'<meta http-equiv="refresh" content="0;url={first}.html">'
        f'<title>Thirsty-Lang Docs</title></head><body>'
        f'<a href="{first}.html">Go to docs</a></body></html>',
        encoding="utf-8",
    )

    if not quiet:
        print(f"\nSite generated: {output_dir}")
        print(f"  {len(pages)} pages, {len(search_index)} search entries")
        print(f"  Open: {output_dir / 'index.html'}")

    return output_dir


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate the Thirsty-Lang documentation site"
    )
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--docs", default=None, help="Source docs directory")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args(argv)

    build_site(
        docs_dir=Path(args.docs) if args.docs else None,
        output_dir=Path(args.output) if args.output else None,
        quiet=args.quiet,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
