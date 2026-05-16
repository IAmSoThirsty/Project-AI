"""
Legion Research Skills
Web Search (DuckDuckGo), Wikipedia, Knowledge Base (Obsidian vault + project docs)
"""
import urllib.parse
from pathlib import Path
from typing import Any

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TIMEOUT = 10.0

# Obsidian vault — primary knowledge base
_OBSIDIAN_VAULT = Path("T:/Project-AI-vault")

# Fallback search roots if vault is unavailable
_FALLBACK_ROOTS = [
    _REPO_ROOT / "docs",
    _REPO_ROOT / "src" / "utf" / "docs",
    _REPO_ROOT,
]


# ── Web Search ────────────────────────────────────────────────────────────────

async def handle_web_search(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    query = msg
    for marker in ["search for", "search:", "google", "find", "look up", "lookup", "web search", "search the web for"]:
        if marker in msg.lower():
            idx = msg.lower().index(marker) + len(marker)
            query = msg[idx:].strip().lstrip(":").strip()
            break
    if not query:
        return {"success": False, "result": "Specify a search query."}
    if not _HTTPX:
        return {"success": False, "result": "httpx not available — install with: pip install httpx"}

    try:
        url = (
            "https://api.duckduckgo.com/?"
            + urllib.parse.urlencode({"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"})
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(url)
        data = r.json()

        results = []
        if data.get("AbstractText"):
            results.append(f"**{data.get('Heading', 'Result')}**\n{data['AbstractText']}")
            if data.get("AbstractURL"):
                results.append(f"Source: {data['AbstractURL']}")

        topics = [t for t in data.get("RelatedTopics", [])[:5] if isinstance(t, dict) and t.get("Text")]
        if topics and not results:
            results = [f"- {t['Text']}" for t in topics]

        if not results:
            return {"success": True, "result": f"No DuckDuckGo results for '{query}'. Try a more specific query."}
        return {"success": True, "result": "\n\n".join(results)}

    except Exception as e:
        return {"success": False, "result": f"Search error: {e}"}


# ── Wikipedia ─────────────────────────────────────────────────────────────────

async def handle_wikipedia(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    topic = msg
    for marker in ["wikipedia", "wiki", "what is", "who is", "define", "tell me about", "explain"]:
        if marker in msg.lower():
            idx = msg.lower().index(marker) + len(marker)
            topic = msg[idx:].strip().lstrip(":").strip()
            break
    if not topic:
        return {"success": False, "result": "Specify a topic to look up."}
    if not _HTTPX:
        return {"success": False, "result": "httpx not available — install with: pip install httpx"}

    try:
        title = urllib.parse.quote(topic.replace(" ", "_"))
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
                headers={"User-Agent": "Legion-AI/1.0 (Project-AI)"},
            )

        if r.status_code == 404:
            # Try search fallback
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                sr = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={"action": "query", "list": "search", "srsearch": topic, "format": "json", "srlimit": "1"},
                    headers={"User-Agent": "Legion-AI/1.0"},
                )
            hits = sr.json().get("query", {}).get("search", [])
            if not hits:
                return {"success": False, "result": f"No Wikipedia article found for '{topic}'."}
            title = urllib.parse.quote(hits[0]["title"].replace(" ", "_"))
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                r = await client.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
                    headers={"User-Agent": "Legion-AI/1.0"},
                )

        if r.status_code != 200:
            return {"success": False, "result": f"Wikipedia lookup failed (HTTP {r.status_code})."}

        data = r.json()
        result = f"**{data.get('title', topic)}**\n\n{data.get('extract', 'No summary available.')}"
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        if page_url:
            result += f"\n\n[Read more on Wikipedia]({page_url})"
        return {"success": True, "result": result}

    except Exception as e:
        return {"success": False, "result": f"Wikipedia error: {e}"}


# ── Knowledge Base (Obsidian vault) ───────────────────────────────────────────

def _search_vault(query: str, max_results: int = 4) -> list[dict]:
    """Search the Obsidian vault and fallback project docs for matching markdown files."""
    terms = [t.lower() for t in query.split() if len(t) > 2]
    if not terms:
        return []

    results = []
    search_roots: list[tuple[Path, str]] = []

    if _OBSIDIAN_VAULT.exists():
        search_roots.append((_OBSIDIAN_VAULT, "vault"))
    for root in _FALLBACK_ROOTS:
        if root.exists():
            search_roots.append((root, "docs"))

    for root, source in search_roots:
        for md_file in root.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                content_l = content.lower()
                score = sum(content_l.count(term) for term in terms)
                if score > 0 and all(term in content_l for term in terms[:2]):
                    # Find first relevant snippet
                    idx = content_l.find(terms[0])
                    snippet = content[max(0, idx - 80): idx + 400].strip()
                    try:
                        rel = md_file.relative_to(root)
                    except ValueError:
                        rel = md_file.name
                    results.append({"file": str(rel), "snippet": snippet, "score": score, "source": source})
            except Exception:
                continue
        if len(results) >= max_results * 2:
            break

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


async def handle_knowledge_base(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    query = msg
    for marker in ["knowledge base", "docs", "documentation", "find in docs", "search docs",
                   "search vault", "obsidian", "in the vault", "find in vault"]:
        if marker in msg.lower():
            idx = msg.lower().index(marker) + len(marker)
            query = msg[idx:].strip().lstrip(":").strip()
            break
    if not query:
        return {"success": False, "result": "Specify a term to search in the knowledge base."}

    results = _search_vault(query)

    if not results:
        source_label = "Obsidian vault" if _OBSIDIAN_VAULT.exists() else "project docs"
        return {"success": True, "result": f"No results found for '{query}' in the {source_label}."}

    vault_label = "Obsidian Vault" if _OBSIDIAN_VAULT.exists() else "Knowledge Base"
    lines = [f"**{vault_label}: '{query}'**\n"]
    for r in results:
        lines.append(f"📄 `{r['file']}`")
        snippet = r["snippet"][:450].replace("```", "")
        lines.append(f"```\n{snippet}\n```\n")

    return {"success": True, "result": "\n".join(lines)}
