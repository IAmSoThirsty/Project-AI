#!/usr/bin/env python3
"""
Thirsty-Lang_UTF_Reference_v1.pdf — Full visual enhancement build.
Dark cardinal / royal blue / gold theme. Spare no expense.
"""

import csv
import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
        Spacer, Table, TableStyle, Flowable, KeepTogether,
    )
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "reportlab", "--break-system-packages", "-q"])
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
        Spacer, Table, TableStyle, Flowable, KeepTogether,
    )

BASE     = Path(__file__).parent
MD_FILE  = BASE / "Thirsty-Lang_UTF_Reference_v1.md"
PDF_FILE = BASE / "Thirsty-Lang_UTF_Reference_v1.pdf"
CSV_FILE = BASE / "Thirsty-Lang_UTF_Source_Map.csv"
GITHUB   = "https://github.com/IAmSoThirsty/Project-AI/blob/main"

# ── Document geometry ──────────────────────────────────────────────────────────
PAGE_W, PAGE_H = letter          # 612 × 792 pt
L_MARGIN = R_MARGIN = 0.75 * inch
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN   # 504 pt  ≈  7 in

# ── Master colour palette ──────────────────────────────────────────────────────
CARDINAL       = colors.HexColor("#8B1A2B")   # Dark cardinal red — H1, title
CARDINAL_LIGHT = colors.HexColor("#FEF5F6")   # Pale callout background
ROYAL_BLUE     = colors.HexColor("#1A52A8")   # Royal blue — H2, subtitle, links
ROYAL_LIGHT    = colors.HexColor("#EEF4FF")   # Pale blue
GOLD           = colors.HexColor("#D4AF37")   # Gold — dividers, outlines, bullets
GOLD_DARK      = colors.HexColor("#8B6914")   # Dark gold shadow ring
GOLD_LIGHT     = colors.HexColor("#FDF8E1")   # Pale gold
AMBER          = colors.HexColor("#D4820A")   # Amber — H3
ORANGE         = colors.HexColor("#C0510A")   # Orange — H4
NEAR_BLACK     = colors.HexColor("#0D0D1A")   # Page bars, shield bg
DARK_NAVY      = colors.HexColor("#0D2B55")   # Callout text, meta
MID_GREY       = colors.HexColor("#777777")   # Footnote / meta
GREY_LIGHT     = colors.HexColor("#F4F4F4")   # Table alt rows
GREY_RULE      = colors.HexColor("#DDDDDD")   # Subtle grid
WHITE          = colors.white
BLACK          = colors.black

# Code dark theme  (GitHub Dark)
CODE_BG        = colors.HexColor("#0D1117")   # Background
CODE_TEXT      = colors.HexColor("#E6EDF3")   # Body text in code
CODE_COMMENT   = colors.HexColor("#8B949E")   # Dim (comments, secondary)
CODE_INLINE_FG = ROYAL_BLUE                   # Inline `code` — blue on white


# ── Paragraph styles ───────────────────────────────────────────────────────────
def ps(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    # ── Title page ──
    "DocTitle": ps("DocTitle", fontSize=30, leading=36,
                   textColor=GOLD, fontName="Helvetica-Bold",
                   alignment=TA_CENTER, spaceAfter=6),
    "DocSubtitle": ps("DocSubtitle", fontSize=14, leading=19,
                      textColor=ROYAL_BLUE, fontName="Helvetica",
                      alignment=TA_CENTER, spaceAfter=4),
    "DocMeta": ps("DocMeta", fontSize=9, leading=13,
                  textColor=MID_GREY, fontName="Helvetica",
                  alignment=TA_CENTER, spaceAfter=3),
    "TitleTagline": ps("TitleTagline", fontSize=11, leading=16,
                       fontName="Helvetica-Oblique", alignment=TA_CENTER,
                       textColor=AMBER, spaceAfter=24),

    # ── Section headings ──
    "H1": ps("H1", fontSize=19, leading=25, textColor=GOLD,
             fontName="Helvetica-Bold", spaceBefore=20, spaceAfter=6),
    "H2": ps("H2", fontSize=14, leading=20, textColor=ROYAL_BLUE,
             fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4),
    "H3": ps("H3", fontSize=11, leading=16, textColor=AMBER,
             fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3),
    "H4": ps("H4", fontSize=10, leading=14, textColor=ORANGE,
             fontName="Helvetica-Bold", spaceBefore=7, spaceAfter=2),

    # ── Body ──
    "Body": ps("Body", fontSize=9.5, leading=14.5, fontName="Helvetica",
               textColor=BLACK, spaceBefore=1, spaceAfter=4),
    "BodyIndent": ps("BodyIndent", fontSize=9.5, leading=14.5,
                     fontName="Helvetica", textColor=BLACK,
                     spaceBefore=1, spaceAfter=3, leftIndent=18),

    # ── Code ── (dark bg, cardinal border, page-splitting safe via Paragraph)
    "Code": ps("Code", fontSize=7.8, leading=11.5, fontName="Courier",
               textColor=CODE_TEXT, backColor=CODE_BG,
               borderPad=10, borderWidth=1.5, borderColor=CARDINAL,
               spaceBefore=6, spaceAfter=6, leftIndent=6, rightIndent=6),

    # ── Callout / blockquote ── (gold border card)
    "Callout": ps("Callout", fontSize=9, leading=13.5,
                  fontName="Helvetica-Oblique", textColor=DARK_NAVY,
                  backColor=GOLD_LIGHT,
                  borderPad=9, borderWidth=1.5, borderColor=GOLD,
                  leftIndent=6, rightIndent=6,
                  spaceBefore=6, spaceAfter=6),

    # ── TOC ──
    "TOC1": ps("TOC1", fontSize=10, leading=14, fontName="Helvetica-Bold",
               textColor=GOLD, leftIndent=0),
    "TOC2": ps("TOC2", fontSize=9, leading=13, fontName="Helvetica",
               textColor=ROYAL_BLUE, leftIndent=18),
    "TOC3": ps("TOC3", fontSize=8.5, leading=12, fontName="Helvetica",
               textColor=MID_GREY, leftIndent=36),

    # ── Table cells ──
    "TH": ps("TH", fontSize=8, leading=11, fontName="Helvetica-Bold",
             textColor=GOLD, alignment=TA_LEFT),
    "TD": ps("TD", fontSize=8, leading=11.5, fontName="Helvetica",
             textColor=BLACK, alignment=TA_LEFT),
    "TDCode": ps("TDCode", fontSize=7.5, leading=10.5, fontName="Courier",
                 textColor=ROYAL_BLUE, alignment=TA_LEFT),
    "TDLink": ps("TDLink", fontSize=7.5, leading=10.5, fontName="Courier",
                 textColor=ROYAL_BLUE, alignment=TA_LEFT),
}


# ── Table style ────────────────────────────────────────────────────────────────
def table_style():
    return TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0),  NEAR_BLACK),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  CARDINAL),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        # Body rows
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        # Grid — cardinal lines on border, subtle on body
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, CARDINAL),
        ("LINEABOVE",     (0, 0), (-1, 0),  1.5, CARDINAL),
        ("LINEBEFORE",    (0, 0), (0, -1),  1.5, CARDINAL),
        ("LINEAFTER",     (-1, 0),(-1, -1), 1.5, CARDINAL),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_RULE),
        # Padding
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


# ── XML escaping ───────────────────────────────────────────────────────────────
def esc(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


# ── File-path detector → GitHub link ─────────────────────────────────────────
_PATH_RE = re.compile(
    r'^[a-zA-Z][a-zA-Z0-9_\-]*(\/[a-zA-Z0-9_\-\.]+)+(\.[a-zA-Z]{1,6})?$'
)

def maybe_link(raw: str) -> str:
    """Return blue underlined GitHub link for file paths; plain blue Courier otherwise."""
    s = raw.strip()
    if _PATH_RE.match(s) and '/' in s:
        url = f"{GITHUB}/{s}"
        return (f'<a href="{url}">'
                f'<font name="Courier" size="8" color="#1A52A8"><u>{esc(raw)}</u></font>'
                f'</a>')
    return f'<font name="Courier" size="8" color="#1A52A8">{esc(raw)}</font>'


# ── Inline formatters ──────────────────────────────────────────────────────────
def fmt_inline(text):
    parts = re.split(r"`([^`]+)`", esc(text))
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(maybe_link(p))
        else:
            out.append(p)
    return "".join(out)


def fmt_bold_italic(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text)
    return text


def fmt_line(text):
    return fmt_bold_italic(fmt_inline(text))


# ── Gold rule helper ───────────────────────────────────────────────────────────
def gold_rule(width="100%", thickness=0.8, before=4, after=4):
    return HRFlowable(width=width, thickness=thickness, color=CARDINAL,
                      spaceBefore=before, spaceAfter=after)


# ── Shield badge (title page) ─────────────────────────────────────────────────
class ShieldBadge(Flowable):
    """Centered circular badge: dark bg, gold ring, blue water drop, white UTF."""
    HEIGHT = 110

    def wrap(self, aw, ah):
        self._aw = aw
        return (aw, self.HEIGHT)

    def draw(self):
        c   = self.canv
        cx  = self._aw / 2
        cy  = self.HEIGHT / 2
        R   = 42

        # Outer shadow ring
        c.setFillColor(GOLD_DARK)
        c.setStrokeColor(colors.Color(0, 0, 0, 0))
        c.circle(cx + 1.5, cy - 1.5, R + 2, fill=1, stroke=0)

        # Main dark circle
        c.setFillColor(NEAR_BLACK)
        c.setStrokeColor(CARDINAL)
        c.setLineWidth(2.8)
        c.circle(cx, cy, R, fill=1, stroke=1)

        # Inner cardinal ring (thin)
        c.setFillColor(colors.Color(0, 0, 0, 0))
        c.setStrokeColor(colors.HexColor("#5A0F1A"))
        c.setLineWidth(0.8)
        c.circle(cx, cy, R - 5, fill=0, stroke=1)

        # ── Blue water drop (teardrop pointing down) ──
        W, H = 14, 28            # half-width, total height
        dx = cx
        dy = cy + 5              # shift drop slightly up so UTF sits on it

        c.setFillColor(ROYAL_BLUE)
        p = c.beginPath()
        p.moveTo(dx, dy + H * 0.42)           # top centre
        # left curve → tip
        p.curveTo(dx - W * 1.35, dy + H * 0.15,
                  dx - W * 1.10, dy - H * 0.28,
                  dx,            dy - H * 0.58)
        # right curve ← back to top
        p.curveTo(dx + W * 1.10, dy - H * 0.28,
                  dx + W * 1.35, dy + H * 0.15,
                  dx,            dy + H * 0.42)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

        # Highlight glint (small lighter ellipse, upper-left of drop)
        c.setFillColor(colors.HexColor("#6BACD6"))
        gx1, gy1 = dx - W * 0.55, dy + H * 0.08
        gx2, gy2 = dx - W * 0.15, dy + H * 0.38
        c.ellipse(gx1, gy1, gx2, gy2, fill=1, stroke=0)

        # "UTF" text in white
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 15)
        c.drawCentredString(dx, dy - 7, "UTF")


# ── Title page ────────────────────────────────────────────────────────────────
def title_page():
    story = []
    story.append(Spacer(1, 0.9 * inch))

    # Badge — centred above headline
    story.append(ShieldBadge())
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph("Thirsty-Lang and the UTF", S["DocTitle"]))
    story.append(Paragraph("Universal Thirsty Family", S["DocSubtitle"]))
    story.append(Spacer(1, 0.1 * inch))

    story.append(gold_rule(width="55%", thickness=2.5, before=4, after=12))

    story.append(Paragraph(
        "A Complete Technical, Architectural, and Governance Reference",
        S["TitleTagline"]))
    story.append(Spacer(1, 0.22 * inch))

    # Meta table — styled card
    repo_link = (f'<a href="{GITHUB}" color="#1A52A8">'
                 f'<u>IAmSoThirsty/Project-AI</u></a>')
    meta = [
        ("Author",     "Thirsty's Projects LLC"),
        ("Version",    "1.2"),
        ("Date",       "2026-05-15"),
        ("Repository", repo_link),
        ("Status",     "Authoritative Reference — Compiled from Repository Sources"),
        ("License",    "MIT"),
    ]
    for k, v in meta:
        story.append(Paragraph(
            f'<font color="#8B1A2B"><b>{k}:</b></font>&nbsp;&nbsp;'
            f'<font color="#444444">{v}</font>',
            S["DocMeta"]))

    story.append(Spacer(1, 0.35 * inch))
    story.append(gold_rule(width="78%", thickness=0.8, before=4, after=16))

    story.append(Paragraph(
        "Thirsty-Lang is the human-readable orchestration layer for governance-bound "
        "execution inside Project-AI. The UTF — Universal Thirsty Family — is the "
        "broader family of languages, encodings, runtimes, and symbolic systems that "
        "carry Project-AI's constitutional execution model across source code, policy, "
        "bytecode, simulation, and runtime enforcement.",
        S["Callout"]))

    return story


# ── Page template (header / footer) ───────────────────────────────────────────
class DocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.doc_title = kwargs.pop("doc_title", "")
        super().__init__(*args, **kwargs)

    def afterPage(self):
        cv = self.canv
        cv.saveState()
        w, h = PAGE_W, PAGE_H

        # ── Header bar ──
        cv.setFillColor(NEAR_BLACK)
        cv.rect(0, h - 34, w, 34, fill=1, stroke=0)
        # Cardinal accent line under header
        cv.setStrokeColor(CARDINAL)
        cv.setLineWidth(1.5)
        cv.line(0, h - 35.5, w, h - 35.5)

        cv.setFillColor(GOLD)
        cv.setFont("Helvetica-Bold", 8.5)
        cv.drawString(0.45 * inch, h - 21,
                      "Thirsty-Lang & UTF — Universal Thirsty Family Reference v1.2")
        cv.setFillColor(colors.HexColor("#AAAAAA"))
        cv.setFont("Helvetica", 7.5)
        cv.drawRightString(w - 0.45 * inch, h - 21, "Thirsty's Projects LLC")

        # ── Footer bar ──
        cv.setFillColor(NEAR_BLACK)
        cv.rect(0, 0, w, 24, fill=1, stroke=0)
        # Cardinal accent line above footer
        cv.setStrokeColor(CARDINAL)
        cv.setLineWidth(1.5)
        cv.line(0, 24, w, 24)

        cv.setFillColor(GOLD)
        cv.setFont("Helvetica", 7.5)
        cv.drawString(0.45 * inch, 8, "© 2026 Thirsty's Projects LLC | MIT License")
        cv.drawCentredString(w / 2, 8, f"— {self.page} —")
        cv.drawRightString(w - 0.45 * inch, 8, "2026-05-15")

        cv.restoreState()


# ── Markdown → ReportLab flowables ────────────────────────────────────────────
def parse_md(md_text):
    lines = md_text.splitlines()
    story = []
    i = 0
    in_code    = False
    code_buf   = []
    in_table   = False
    table_rows = []
    first_h1   = True   # suppress PageBreak before the very first H1

    # ── flush helpers ──
    def flush_code():
        nonlocal code_buf
        if code_buf:
            raw  = "\n".join(code_buf)
            safe = esc(raw).replace("\n", "<br/>").replace(" ", "&nbsp;")
            story.append(Paragraph(safe, S["Code"]))
            story.append(Spacer(1, 4))
        code_buf = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        col_count  = max(len(r) for r in table_rows)
        col_w      = USABLE_W / max(col_count, 1)
        col_widths = [col_w] * col_count
        rl_rows    = []

        for ri, row in enumerate(table_rows):
            rl_row = []
            for cell in row:
                cell = cell.strip()
                if ri == 0:
                    rl_row.append(Paragraph(fmt_line(cell), S["TH"]))
                elif cell.startswith("`") and cell.endswith("`"):
                    inner  = cell[1:-1]
                    linked = maybe_link(inner)
                    rl_row.append(Paragraph(linked, S["TDLink"]))
                else:
                    rl_row.append(Paragraph(fmt_line(cell), S["TD"]))
            while len(rl_row) < col_count:
                rl_row.append(Paragraph("", S["TD"]))
            rl_rows.append(rl_row)

        t = Table(rl_rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(table_style())
        story.append(t)
        story.append(Spacer(1, 10))
        table_rows.clear()
        in_table = False

    # ── main parsing loop ──
    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.startswith("```"):
            if not in_code:
                if in_table:
                    flush_table()
                in_code  = True
                code_buf = []
            else:
                flush_code()
                in_code = False
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Table row
        if line.startswith("|"):
            cells = [c for c in line.split("|") if c != ""]
            if all(re.match(r"^[\s\-:]+$", c) for c in cells):
                i += 1
                continue
            in_table = True
            table_rows.append(cells)
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # Blank line
        if not line.strip():
            story.append(Spacer(1, 5))
            i += 1
            continue

        # HR — gold rule
        if re.match(r"^---+$", line.strip()):
            story.append(gold_rule(thickness=1.0, before=6, after=6))
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text  = fmt_line(m.group(2))
            hs    = ["H1", "H2", "H3", "H4"][level - 1]

            if level == 1:
                if not first_h1:
                    story.append(PageBreak())
                first_h1 = False
                story.append(gold_rule(thickness=2.5, before=0, after=3))
                story.append(Paragraph(text, S[hs]))
                story.append(gold_rule(thickness=0.6, before=0, after=8))

            elif level == 2:
                story.append(Paragraph(text, S[hs]))
                story.append(gold_rule(width="40%", thickness=0.5,
                                       before=0, after=6))
            else:
                story.append(Paragraph(text, S[hs]))

            i += 1
            continue

        # Blockquote → styled callout card
        if line.startswith("> "):
            story.append(Paragraph(fmt_line(line[2:]), S["Callout"]))
            i += 1
            continue

        # Bullet list — gold bullet
        bm = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if bm:
            indent = len(bm.group(1))
            li = (f'<font color="#8B1A2B" size="10">◆</font>'
                  f'&nbsp;&nbsp;{fmt_line(bm.group(2))}')
            bullet_style = ParagraphStyle(
                "BL", parent=S["Body"],
                leftIndent=14 + indent * 10,
                spaceBefore=1, spaceAfter=2,
            )
            story.append(Paragraph(li, bullet_style))
            i += 1
            continue

        # Numbered list
        nm = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if nm:
            story.append(Paragraph(
                fmt_line(nm.group(2)),
                ParagraphStyle("NL", parent=S["Body"], leftIndent=20,
                               spaceBefore=1, spaceAfter=2)))
            i += 1
            continue

        # Normal paragraph
        story.append(Paragraph(fmt_line(line), S["Body"]))
        i += 1

    if in_code:
        flush_code()
    if in_table:
        flush_table()

    return story


# ── Source map ────────────────────────────────────────────────────────────────
SOURCE_MAP = [
    ("T.A.R.L. = Thirsty's Active Resistance Language",
     "tarl/README.md; tarl/docs/ARCHITECTURE.md; tarl/docs/WHITEPAPER.md",
     "Title and abstract of all three documents", "HIGH",
     "Consistent across 3 documents"),
    ("T.A.R.L. = Trust and Authorization Runtime Layer",
     "tarl_os/README.md",
     "Integration section comment", "MEDIUM",
     "Alternative framing; one location only — documented conflict"),
    ("UTF canonical stack has 6 members",
     "src/utf/docs/CANONICAL_STACK.md",
     "Numbered list 1-6", "HIGH", "Primary source"),
    ("UTF README describes amplified bootstrap",
     "src/utf/README.md",
     "Full document; 'What is executable now' section", "HIGH", "Primary source"),
    ("Thirsty-Lang keyword set (complete)",
     "src/utf/thirsty_lang/token.py",
     "KEYWORDS dict + TokenType enum", "HIGH", "Definitive keyword list"),
    ("Thirsty-Lang lexer fully implemented",
     "src/utf/thirsty_lang/lexer.py",
     "Complete Python class; Lexer.lex()", "HIGH", ""),
    ("Shadow Thirst 6 analyzers",
     "src/utf/shadow_thirst/core.py",
     "analyze() function returns 6 AnalysisResult per mutation", "HIGH", ""),
    ("Shadow Thirst promote/reject verdict",
     "src/utf/shadow_thirst/core.py",
     "promote() returns PROMOTE or REJECT", "HIGH", ""),
    ("TSCG 9 core symbols",
     "src/utf/tscg/core.py",
     "CORE_SYMBOLS dict", "HIGH",
     "COG DNT SHD INV CAP QRM COM ANC RFX"),
    ("TSCG-B magic = TSGB",
     "src/utf/tscg_b/core.py",
     "MAGIC = b'TSGB'", "HIGH", ""),
    ("TSCG-B CRC32 + SHA-256 integrity",
     "src/utf/tscg_b/core.py",
     "pack_text() and unpack_frame()", "HIGH", ""),
    ("TARL policy default = DENY",
     "src/utf/tarl/core.py",
     "evaluate() returns 'DENY' when no rule matches", "HIGH",
     "Fail-closed behavior"),
    ("TarlVerdict: ALLOW/DENY/ESCALATE",
     "tarl/spec.py", "TarlVerdict enum", "HIGH", ""),
    ("TarlRuntime LRU cache + parallel eval",
     "tarl/runtime.py",
     "TarlRuntime class with _decision_cache and ThreadPoolExecutor", "HIGH", ""),
    ("TARL 8 subsystems layered architecture",
     "tarl/docs/ARCHITECTURE.md; tarl/docs/WHITEPAPER.md",
     "Layer 0-7 documented in both docs", "HIGH", ""),
    ("TARL bytecode format TARL_BYTECODE_V1",
     "tarl/docs/WHITEPAPER.md",
     "Section 3.2 Bytecode Format", "HIGH", ""),
    ("TARL OS 29 subsystems ~13600 LOC",
     "tarl_os/TARL_OS_COMPLETE_IMPLEMENTATION_REPORT.md",
     "Executive Summary section", "MEDIUM",
     "Self-reported; not independently verified"),
    ("TARL OS v2 vs v3 conflict",
     "tarl_os/README.md (v2) vs tarl_os/TARL_OS_COMPLETE_IMPLEMENTATION_REPORT.md (v3)",
     "Two documents with different version numbers", "DOCUMENTED CONFLICT",
     "Report is newer (2026-02-08 vs 2026-01-30)"),
    ("5 constitutional rules with actions",
     "tarl_os/security/thirstys_constitution.thirsty",
     "initConstitution() pushes 5 rule objects", "HIGH", ""),
    ("Enforcement gateway fail-closed",
     "tarl_os/security/thirstys_enforcement_gateway.thirsty",
     "!enforcementActive → allowed:false 'Gateway offline'", "HIGH", ""),
    ("Iron Path full pipeline with crypto",
     "governance/iron_path.py",
     "_execute_stage() with role_sig, policy_binding, sha256", "HIGH", ""),
    ("build.tarl uses Thirsty-Lang syntax",
     "build.tarl",
     "drink/glass/pour/shield/thirsty keywords", "HIGH", ""),
    ("Scheduler 8 priority levels",
     "tarl_os/kernel/scheduler.thirsty",
     "PRIORITY_REALTIME=0 through PRIORITY_IDLE=7", "HIGH", ""),
    ("PSIA acronym expansion", "None",
     "Inferred from src/psia/ directory", "LOW",
     "Undocumented — needs confirmation"),
    ("Triumvirate server implementation",
     "governance/triumvirate_server.py",
     "SQLite-backed audit log, 3-pillar consensus, port 8001", "HIGH", ""),
    ("Hello Thirsty example",
     "src/utf/examples/hello.thirsty",
     "glass main() -> Int { pour('hello, thirsty world'); return 0; }",
     "HIGH", ""),
    ("PromotionGate policy example",
     "src/utf/examples/policy.tarl",
     "policy PromotionGate { ... } with 3 rules", "HIGH", ""),
    ("Shadow mutation example",
     "src/utf/examples/promote.shadowthirst",
     "mutation validated_canonical set_counter(value: Int) {...}",
     "HIGH", ""),
    ("Ed25519 key rotation",
     "src/psia/crypto/anchor.py",
     "rotate_key(), verify_with_history(), KeyVersion dataclass",
     "HIGH", "Phase 6 implementation"),
    ("Triumvirate SQLite audit persistence",
     "governance/triumvirate_server.py",
     "_init_db(), _write_decision(), governance/audit.db",
     "HIGH", "Phase 6 implementation"),
]


def write_csv():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Claim", "Source File", "Evidence", "Confidence", "Notes"])
        w.writerows(SOURCE_MAP)
    print(f"CSV: {CSV_FILE}")


# ── PDF builder ───────────────────────────────────────────────────────────────
def build_pdf():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # Strip markdown title block (up to first HR)
    lines = md_text.splitlines()
    start = 0
    for idx, ln in enumerate(lines):
        if re.match(r"^---+$", ln.strip()):
            start = idx + 1
            break
    md_body = "\n".join(lines[start:])

    doc = DocTemplate(
        str(PDF_FILE),
        pagesize=letter,
        doc_title="Thirsty-Lang & UTF Reference v1.2",
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=0.72 * inch,
        bottomMargin=0.52 * inch,
    )

    story = []
    story.extend(title_page())
    story.extend(parse_md(md_body))

    print(f"Building PDF ({len(story)} flowables)...")
    doc.build(story)
    print(f"PDF written: {PDF_FILE}")


if __name__ == "__main__":
    write_csv()
    build_pdf()
    print("Done.")
