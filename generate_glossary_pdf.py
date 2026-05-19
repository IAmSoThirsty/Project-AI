#!/usr/bin/env python3
r"""
Generate T:\INTERNAL_NAME_GLOSSARY.pdf from docs/INTERNAL_NAME_GLOSSARY.md
Uses the same reportlab stack as generate_pdf.py.
"""

import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
        Spacer, Table, TableStyle,
    )
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "reportlab", "--break-system-packages", "-q"])
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
        Spacer, Table, TableStyle,
    )

BASE     = Path(__file__).parent
MD_FILE  = BASE / "docs" / "INTERNAL_NAME_GLOSSARY.md"
PDF_FILE = Path("T:/") / "INTERNAL_NAME_GLOSSARY.pdf"

PAGE_W, PAGE_H = letter
L_MARGIN = R_MARGIN = 0.75 * inch
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN

# ── Palette ──────────────────────────────────────────────────────────────────
CARDINAL    = colors.HexColor("#8B1A2B")
ROYAL_BLUE  = colors.HexColor("#1A52A8")
GOLD        = colors.HexColor("#D4AF37")
AMBER       = colors.HexColor("#D4820A")
NEAR_BLACK  = colors.HexColor("#0D0D1A")
DARK_NAVY   = colors.HexColor("#0D2B55")
MID_GREY    = colors.HexColor("#777777")
GREY_LIGHT  = colors.HexColor("#F4F4F4")
GREY_RULE   = colors.HexColor("#DDDDDD")
GOLD_LIGHT  = colors.HexColor("#FDF8E1")
CODE_BG     = colors.HexColor("#0D1117")
CODE_TEXT   = colors.HexColor("#E6EDF3")
WHITE       = colors.white
BLACK       = colors.black

# ── Styles ───────────────────────────────────────────────────────────────────
def ps(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    "DocTitle":   ps("DocTitle",   fontSize=26, leading=32, textColor=GOLD,
                     fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6),
    "DocSubtitle":ps("DocSubtitle",fontSize=12, leading=17, textColor=ROYAL_BLUE,
                     fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4),
    "DocMeta":    ps("DocMeta",    fontSize=9,  leading=13, textColor=MID_GREY,
                     fontName="Helvetica", alignment=TA_CENTER, spaceAfter=3),
    "H1":         ps("H1",         fontSize=18, leading=24, textColor=GOLD,
                     fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=5),
    "H2":         ps("H2",         fontSize=13, leading=19, textColor=ROYAL_BLUE,
                     fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
    "H3":         ps("H3",         fontSize=10, leading=15, textColor=AMBER,
                     fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=2),
    "H4":         ps("H4",         fontSize=9,  leading=13, textColor=CARDINAL,
                     fontName="Helvetica-Bold", spaceBefore=5, spaceAfter=1),
    "Body":       ps("Body",       fontSize=9,  leading=14, fontName="Helvetica",
                     textColor=BLACK, spaceBefore=1, spaceAfter=3),
    "Callout":    ps("Callout",    fontSize=8.5,leading=13, fontName="Helvetica-Oblique",
                     textColor=DARK_NAVY, backColor=GOLD_LIGHT,
                     borderPad=8, borderWidth=1.2, borderColor=GOLD,
                     leftIndent=6, rightIndent=6, spaceBefore=5, spaceAfter=5),
    "Code":       ps("Code",       fontSize=7.5,leading=11, fontName="Courier",
                     textColor=CODE_TEXT, backColor=CODE_BG,
                     borderPad=8, borderWidth=1.2, borderColor=CARDINAL,
                     spaceBefore=4, spaceAfter=4, leftIndent=6, rightIndent=6),
    "TH":         ps("TH",         fontSize=8,  leading=11, fontName="Helvetica-Bold",
                     textColor=GOLD, alignment=TA_LEFT),
    "TD":         ps("TD",         fontSize=8,  leading=11, fontName="Helvetica",
                     textColor=BLACK, alignment=TA_LEFT),
    "TDCode":     ps("TDCode",     fontSize=7.5,leading=10, fontName="Courier",
                     textColor=ROYAL_BLUE, alignment=TA_LEFT),
}


def esc(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def fmt_inline(text):
    parts = re.split(r"`([^`]+)`", esc(text))
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(f'<font name="Courier" size="8" color="#1A52A8">{esc(p)}</font>')
        else:
            out.append(p)
    return "".join(out)


def fmt_line(text):
    text = fmt_inline(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text)
    # strip markdown links [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text


def gold_rule(width="100%", thickness=0.8, before=4, after=4):
    return HRFlowable(width=width, thickness=thickness, color=CARDINAL,
                      spaceBefore=before, spaceAfter=after)


def table_style():
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NEAR_BLACK),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  GOLD),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, CARDINAL),
        ("LINEABOVE",     (0, 0), (-1, 0),  1.5, CARDINAL),
        ("LINEBEFORE",    (0, 0), (0, -1),  1.5, CARDINAL),
        ("LINEAFTER",     (-1, 0),(-1, -1), 1.5, CARDINAL),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_RULE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])


# ── Page template ─────────────────────────────────────────────────────────────
class GlossaryDoc(SimpleDocTemplate):
    def afterPage(self):
        cv = self.canv
        cv.saveState()
        w, h = PAGE_W, PAGE_H

        # Header
        cv.setFillColor(NEAR_BLACK)
        cv.rect(0, h - 32, w, 32, fill=1, stroke=0)
        cv.setStrokeColor(CARDINAL)
        cv.setLineWidth(1.5)
        cv.line(0, h - 33, w, h - 33)
        cv.setFillColor(GOLD)
        cv.setFont("Helvetica-Bold", 8)
        cv.drawString(0.45 * inch, h - 19, "Project-AI — Internal Name Glossary")
        cv.setFillColor(colors.HexColor("#AAAAAA"))
        cv.setFont("Helvetica", 7.5)
        cv.drawRightString(w - 0.45 * inch, h - 19, "Thirsty's Projects LLC")

        # Footer
        cv.setFillColor(NEAR_BLACK)
        cv.rect(0, 0, w, 22, fill=1, stroke=0)
        cv.setStrokeColor(CARDINAL)
        cv.setLineWidth(1.5)
        cv.line(0, 22, w, 22)
        cv.setFillColor(GOLD)
        cv.setFont("Helvetica", 7.5)
        cv.drawString(0.45 * inch, 7, "Engineering Reference — All rights reserved")
        cv.drawCentredString(w / 2, 7, f"— {self.page} —")
        cv.drawRightString(w - 0.45 * inch, 7, "2026-05-19")

        cv.restoreState()


# ── Title page ────────────────────────────────────────────────────────────────
def title_page():
    story = [Spacer(1, 1.1 * inch)]
    story.append(Paragraph("Project-AI", S["DocTitle"]))
    story.append(Paragraph("Internal Name Glossary — Engineering Reference", S["DocSubtitle"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(gold_rule(width="60%", thickness=2, before=4, after=12))

    meta = [
        ("Owner",    "Thirsty's Projects LLC"),
        ("Version",  "1.0"),
        ("Date",     "2026-05-19"),
        ("Entries",  "120 names across 14 functional categories"),
        ("Status",   "Authoritative Reference — Compiled from Repository Sources"),
    ]
    for k, v in meta:
        story.append(Paragraph(
            f'<font color="#8B1A2B"><b>{k}:</b></font>&nbsp;&nbsp;'
            f'<font color="#444444">{v}</font>',
            S["DocMeta"]))

    story.append(Spacer(1, 0.4 * inch))
    story.append(gold_rule(width="80%", thickness=0.8, before=4, after=14))
    story.append(Paragraph(
        "Every unusual, mythic, or project-specific name used in Project-AI mapped "
        "to plain engineering terminology and functional descriptions. "
        "Entries are grouped by functional area and alphabetical within each section.",
        S["Callout"]))
    story.append(PageBreak())
    return story


# ── Markdown parser ───────────────────────────────────────────────────────────
def parse_md(md_text):
    lines = md_text.splitlines()
    story = []
    i = 0
    in_code    = False
    code_buf   = []
    in_table   = False
    table_rows = []
    first_h1   = True

    def flush_code():
        nonlocal code_buf
        if code_buf:
            raw  = "\n".join(code_buf)
            safe = esc(raw).replace("\n", "<br/>").replace(" ", "&nbsp;")
            story.append(Paragraph(safe, S["Code"]))
        code_buf.clear()

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
                style = S["TH"] if ri == 0 else (
                    S["TDCode"] if (cell.startswith("`") and cell.endswith("`")) else S["TD"]
                )
                if style is S["TDCode"]:
                    cell = cell[1:-1]
                rl_row.append(Paragraph(fmt_line(cell), style))
            while len(rl_row) < col_count:
                rl_row.append(Paragraph("", S["TD"]))
            rl_rows.append(rl_row)
        t = Table(rl_rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(table_style())
        story.append(t)
        story.append(Spacer(1, 8))
        table_rows.clear()
        in_table = False

    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.startswith("```"):
            if not in_code:
                if in_table:
                    flush_table()
                in_code = True
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

        # Blank
        if not line.strip():
            story.append(Spacer(1, 4))
            i += 1
            continue

        # HR
        if re.match(r"^---+$", line.strip()):
            story.append(gold_rule(thickness=0.6, before=4, after=4))
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
                story.append(gold_rule(thickness=2, before=0, after=3))
                story.append(Paragraph(text, S[hs]))
                story.append(gold_rule(thickness=0.5, before=0, after=6))
            elif level == 2:
                story.append(Paragraph(text, S[hs]))
                story.append(gold_rule(width="35%", thickness=0.5, before=0, after=5))
            else:
                story.append(Paragraph(text, S[hs]))
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            story.append(Paragraph(fmt_line(line[2:]), S["Callout"]))
            i += 1
            continue

        # Bullet
        bm = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if bm:
            indent = len(bm.group(1))
            li = (f'<font color="#8B1A2B" size="10">◆</font>'
                  f'&nbsp;&nbsp;{fmt_line(bm.group(2))}')
            story.append(Paragraph(li, ParagraphStyle(
                "BL", parent=S["Body"], leftIndent=14 + indent * 10,
                spaceBefore=1, spaceAfter=2)))
            i += 1
            continue

        # Numbered list
        nm = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if nm:
            story.append(Paragraph(fmt_line(nm.group(2)), ParagraphStyle(
                "NL", parent=S["Body"], leftIndent=20, spaceBefore=1, spaceAfter=2)))
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


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # Skip the leading intro block (everything before the first ## heading)
    lines = md_text.splitlines()
    start = 0
    for idx, ln in enumerate(lines):
        if ln.startswith("## "):
            start = idx
            break
    md_body = "\n".join(lines[start:])

    doc = GlossaryDoc(
        str(PDF_FILE),
        pagesize=letter,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=0.65 * inch,
        bottomMargin=0.48 * inch,
    )

    story = title_page()
    story.extend(parse_md(md_body))

    print(f"Building PDF ({len(story)} flowables)...")
    doc.build(story)
    print(f"PDF written -> {PDF_FILE}")


if __name__ == "__main__":
    build()
