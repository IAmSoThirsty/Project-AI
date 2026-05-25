#!/usr/bin/env python3
"""
Generate Thirsty-Lang_UTF_Reference_v1.pdf from the markdown source.
Requires: reportlab
Install:  pip install reportlab
"""

import csv
import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.tableofcontents import TableOfContents
except ImportError:
    print("Installing reportlab...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "--break-system-packages", "-q"])
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.tableofcontents import TableOfContents

BASE = Path(__file__).parent
MD_FILE = BASE / "Thirsty-Lang_UTF_Reference_v1.md"
PDF_FILE = Path("T:/Thirsty-Lang_UTF_Reference_v1.2.pdf")
CSV_FILE = Path("T:/Thirsty-Lang_UTF_Source_Map_v1.2.csv")

# ═══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE UTF DATA - Enhanced Coverage for v1.2
# ═══════════════════════════════════════════════════════════════════════════════

# UTF Implementation Statistics (from src/utf/)
UTF_STATS = {
    "total_python_files": 41,
    "total_lines_of_code": 5995,
    "total_size_kb": 246.73,
    "modules": {
        "Thirsty-Lang (Tier 1)": {"files": 17, "lines": 4335, "desc": "Lexer, parser, interpreter, CLI"},
        "T.A.R.L. (Tier 3)": {"files": 6, "lines": 753, "desc": "Policy runtime and bytecode VM"},
        "Shadow Thirst (Tier 4)": {"files": 3, "lines": 262, "desc": "Mutation simulation layer"},
        "TSCG (Tier 5)": {"files": 3, "lines": 139, "desc": "Symbolic constitutional grammar"},
        "TSCG-B (Tier 6)": {"files": 3, "lines": 135, "desc": "Binary frame protocol"},
        "Test Suite": {"files": 8, "lines": 362, "desc": "Unit and integration tests"},
    },
    "examples": 7,
    "test_coverage": "7 test files, 362 test lines",
    "subdirectories": 19,
}

# UTF Examples (from src/utf/examples/)
UTF_EXAMPLES = [
    ("hello.thirsty", "Basic Hello World", """glass main() -> Int {
  pour("hello, thirsty world");
  return 0;
}"""),
    ("gods.thirstofgods", "Advanced: Classes, Async, Error Handling", """fountain WaterTracker {
  drink mut count: Int;
  
  glass init(start: Int) {
    this.count = start;
  }
  
  glass add(amount: Int) -> Int {
    this.count = this.count + amount;
    return this.count;
  }
  
  cascade glass current() -> Int {
    return this.count;
  }
}

glass main() -> Int {
  drink mut tracker: WaterTracker = new WaterTracker(3);
  pour(tracker.add(4));
  pour(await tracker.current());
  spillage {
    throw "oops";
  } cleanup error (e: Error) {
    pour(e);
  }
  return 0;
}"""),
    ("policy.tarl", "T.A.R.L. Policy", """policy PromotionGate {
  when actor.role == "builder" and mutation.risk <= 3 => ALLOW;
  when mutation.risk > 3 => ESCALATE;
  when actor.role != "builder" => DENY;
}"""),
    ("promote.shadowthirst", "Shadow Thirst Mutation", """mutation validated_canonical set_counter(value: Int) {
  shadow {
    drink mut temp: Int = value;
    temp = temp + 1;
  }
  invariant {
    length("ok");
  }
  canonical {
    canonical_counter = value;
  }
}"""),
]

# UTF Feature Matrix
UTF_FEATURE_MATRIX = [
    ["Tier", "Layer", "Purpose", "Key Features", "Status"],
    ["1", "Thirsty-Lang", "Source syntax", "Water metaphor keywords, type system", "✓ Implemented"],
    ["2", "Thirst of Gods", "Advanced dialect", "Extended stdlib, async/await patterns", "✓ Implemented"],
    ["3", "T.A.R.L.", "Policy/Runtime", "Governance policies, bytecode VM", "✓ Implemented"],
    ["4", "Shadow Thirst", "Mutation sim", "Shadow/invariant/canonical execution", "✓ Implemented"],
    ["5", "TSCG", "Symbolic grammar", "9 symbols (COG,DNT,SHD,INV,CAP,QRM,COM,ANC,RFX)", "✓ Implemented"],
    ["6", "TSCG-B", "Binary protocol", "Frame-based, CRC32+SHA256 integrity", "✓ Implemented"],
]

# Architecture Overview
ARCHITECTURE_OVERVIEW = [
    ["Component", "Location", "Files", "Lines", "Role"],
    ["Lexer", "src/utf/thirsty_lang/lexer.py", "1", "~500", "Tokenization"],
    ["Parser", "src/utf/thirsty_lang/parser.py", "1", "~800", "AST generation"],
    ["Interpreter", "src/utf/thirsty_lang/interpreter.py", "1", "~1200", "Execution engine"],
    ["CLI", "src/utf/thirsty_lang/cli.py", "1", "~300", "Command-line interface"],
    ["TARL Runtime", "src/utf/tarl/", "6", "753", "Policy enforcement"],
    ["Shadow Thirst", "src/utf/shadow_thirst/", "3", "262", "Mutation validation"],
    ["TSCG Parser", "src/utf/tscg/", "3", "139", "Symbolic grammar"],
    ["TSCG-B Codec", "src/utf/tscg_b/", "3", "135", "Binary serialization"],
]

# ── Colour palette ─────────────────────────────────────────────────────────────
BLUE_DARK  = colors.HexColor("#0D2B55")
BLUE_MID   = colors.HexColor("#1A4A8A")
BLUE_LIGHT = colors.HexColor("#E8F0FB")
TEAL       = colors.HexColor("#006666")
ORANGE     = colors.HexColor("#C0510A")
GREY_LIGHT = colors.HexColor("#F5F5F5")
GREY_RULE  = colors.HexColor("#CCCCCC")
WHITE      = colors.white
BLACK      = colors.black

# ── Styles ─────────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    styles = {
        # Title page
        "DocTitle": ps("DocTitle", fontSize=28, leading=34, textColor=BLUE_DARK,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8),
        "DocSubtitle": ps("DocSubtitle", fontSize=13, leading=18, textColor=BLUE_MID,
                          fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6),
        "DocMeta": ps("DocMeta", fontSize=9, leading=13, textColor=colors.grey,
                      fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4),

        # Section headings
        "H1": ps("H1", fontSize=18, leading=24, textColor=BLUE_DARK,
                 fontName="Helvetica-Bold", spaceBefore=24, spaceAfter=8,
                 borderPad=0),
        "H2": ps("H2", fontSize=14, leading=20, textColor=BLUE_MID,
                 fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=6),
        "H3": ps("H3", fontSize=11, leading=16, textColor=TEAL,
                 fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
        "H4": ps("H4", fontSize=10, leading=14, textColor=ORANGE,
                 fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3),

        # Body
        "Body": ps("Body", fontSize=9.5, leading=14, fontName="Helvetica",
                   textColor=BLACK, spaceBefore=2, spaceAfter=4,
                   leftIndent=0),
        "BodyIndent": ps("BodyIndent", fontSize=9.5, leading=14, fontName="Helvetica",
                         textColor=BLACK, spaceBefore=2, spaceAfter=4,
                         leftIndent=20),

        # Code / monospace
        "Code": ps("Code", fontSize=8, leading=11, fontName="Courier",
                   textColor=colors.HexColor("#1A1A1A"),
                   backColor=GREY_LIGHT, borderPad=4,
                   spaceBefore=4, spaceAfter=4, leftIndent=12),

        # Blockquote / callout
        "Callout": ps("Callout", fontSize=9, leading=13, fontName="Helvetica-Oblique",
                      textColor=BLUE_DARK, leftIndent=20, rightIndent=20,
                      spaceBefore=6, spaceAfter=6),

        # TOC
        "TOC1": ps("TOC1", fontSize=10, leading=14, fontName="Helvetica-Bold",
                   textColor=BLUE_DARK, leftIndent=0),
        "TOC2": ps("TOC2", fontSize=9, leading=13, fontName="Helvetica",
                   textColor=BLACK, leftIndent=18),
        "TOC3": ps("TOC3", fontSize=8.5, leading=12, fontName="Helvetica",
                   textColor=colors.grey, leftIndent=36),

        # Table header / cell
        "TH": ps("TH", fontSize=8, leading=11, fontName="Helvetica-Bold",
                 textColor=WHITE, alignment=TA_LEFT),
        "TD": ps("TD", fontSize=8, leading=11, fontName="Helvetica",
                 textColor=BLACK, alignment=TA_LEFT),
        "TDCode": ps("TDCode", fontSize=7.5, leading=10, fontName="Courier",
                     textColor=BLACK, alignment=TA_LEFT),
    }
    return styles


S = make_styles()

# ── Table styling ───────────────────────────────────────────────────────────────
def table_style(header_cols=None):
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_MID),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID",       (0, 0), (-1, -1), 0.4, GREY_RULE),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]
    return TableStyle(cmds)


# ── Helper: escape XML-unsafe chars for Paragraph ──────────────────────────────
def esc(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


# ── Inline code formatter ───────────────────────────────────────────────────────
def fmt_inline(text):
    """Replace `backtick` spans with Courier font tags."""
    parts = re.split(r"`([^`]+)`", esc(text))
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(f'<font name="Courier" size="8" color="#1A1A1A">{p}</font>')
        else:
            out.append(p)
    return "".join(out)


def fmt_bold_italic(text):
    """Handle **bold** and *italic* markdown in Paragraph text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",   r"<i>\1</i>", text)
    return text


def fmt_line(text):
    return fmt_bold_italic(fmt_inline(text))


# ── Markdown → ReportLab flowables ─────────────────────────────────────────────
def parse_md(md_text):
    lines = md_text.splitlines()
    story = []
    i = 0
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            raw = "\n".join(code_buf)
            safe = esc(raw).replace("\n", "<br/>").replace(" ", "&nbsp;")
            story.append(Paragraph(safe, S["Code"]))
            story.append(Spacer(1, 4))
        code_buf = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        # Build ReportLab table
        col_count = max(len(r) for r in table_rows)
        col_w = (6.5 * inch) / max(col_count, 1)
        col_widths = [col_w] * col_count

        rl_rows = []
        for ri, row in enumerate(table_rows):
            rl_row = []
            style = S["TH"] if ri == 0 else S["TD"]
            for cell in row:
                cell = cell.strip()
                # Use monospace if looks like code
                if cell.startswith("`") and cell.endswith("`"):
                    cell = cell[1:-1]
                    style = S["TDCode"]
                rl_row.append(Paragraph(fmt_line(cell), style))
            # Pad short rows
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
            # Skip separator rows like |---|---|
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
        if line.strip() == "":
            story.append(Spacer(1, 4))
            i += 1
            continue

        # HR
        if re.match(r"^---+$", line.strip()):
            story.append(HRFlowable(width="100%", thickness=0.5, color=GREY_RULE,
                                    spaceAfter=6, spaceBefore=6))
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text = fmt_line(m.group(2))
            hs = ["H1", "H2", "H3", "H4"][level - 1]
            if level == 1:
                story.append(PageBreak())
                story.append(HRFlowable(width="100%", thickness=1.5,
                                        color=BLUE_DARK, spaceAfter=4))
            story.append(Paragraph(text, S[hs]))
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            story.append(Paragraph(fmt_line(line[2:]), S["Callout"]))
            i += 1
            continue

        # Bullet list
        bm = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if bm:
            indent = len(bm.group(1))
            style_name = "BodyIndent" if indent > 0 else "Body"
            bullet_style = ParagraphStyle(
                "Bullet", parent=S[style_name],
                leftIndent=12 + indent * 8,
                bulletIndent=4 + indent * 8,
                bulletText="•",
            )
            story.append(Paragraph(fmt_line(bm.group(2)), bullet_style))
            i += 1
            continue

        # Numbered list
        nm = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if nm:
            story.append(Paragraph(fmt_line(nm.group(2)),
                                   ParagraphStyle("Num", parent=S["Body"],
                                                  leftIndent=20)))
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


# ── Page template (header/footer) ───────────────────────────────────────────────
class DocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.doc_title = kwargs.pop("doc_title", "")
        super().__init__(*args, **kwargs)

    def handle_pageBegin(self):
        super().handle_pageBegin()

    def afterPage(self):
        canvas = self.canv
        canvas.saveState()
        w, h = letter

        # Header bar
        canvas.setFillColor(BLUE_DARK)
        canvas.rect(0, h - 32, w, 32, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(0.4 * inch, h - 20,
                          "Thirsty-Lang & UTF — Universal Thirsty Family Reference v1.0")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(w - 0.4 * inch, h - 20, "Project-AI | Confidential")

        # Footer
        canvas.setFillColor(BLUE_DARK)
        canvas.rect(0, 0, w, 22, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(0.4 * inch, 7, "© 2026 Project-AI Team | MIT License")
        canvas.drawCentredString(w / 2, 7, f"Page {self.page}")
        canvas.drawRightString(w - 0.4 * inch, 7, "2026-05-12")
        canvas.restoreState()


# ── Title page ──────────────────────────────────────────────────────────────────
def title_page():
    story = []
    story.append(Spacer(1, 1.4 * inch))

    # Logo-style accent bar (ReportLab drawing — no emoji, fonts don't support them)
    from reportlab.platypus import Flowable
    class TitleAccent(Flowable):
        def draw(self):
            self.canv.setFillColor(BLUE_MID)
            self.canv.circle(0, 0, 28, fill=1, stroke=0)
            self.canv.setFillColor(WHITE)
            self.canv.setFont("Helvetica-Bold", 22)
            self.canv.drawCentredString(0, -8, "UTF")
        def wrap(self, aw, ah):
            return (aw, 72)
    story.append(TitleAccent())
    story.append(Paragraph("Thirsty-Lang and the UTF", S["DocTitle"]))
    story.append(Paragraph("Universal Thirsty Family", S["DocSubtitle"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="60%", thickness=2, color=BLUE_MID,
                             hAlign="CENTER", spaceAfter=16))
    story.append(Paragraph(
        "A Complete Technical, Architectural, and Governance Reference",
        ParagraphStyle("SubLine", fontSize=11, leading=16,
                       alignment=TA_CENTER, fontName="Helvetica-Oblique",
                       textColor=TEAL, spaceAfter=30)))
    story.append(Spacer(1, 0.3 * inch))

    meta = [
        ("Version", "1.2"),
        ("Date", "2026-05-12"),
        ("Repository", "IAmSoThirsty/Project-AI"),
        ("Status", "Authoritative Reference — Compiled from Repository Sources"),
        ("License", "MIT"),
    ]
    for k, v in meta:
        story.append(Paragraph(
            f'<b><font color="#0D2B55">{k}:</font></b>&nbsp;&nbsp;{v}',
            S["DocMeta"]))

    story.append(Spacer(1, 0.5 * inch))
    story.append(HRFlowable(width="80%", thickness=0.5, color=GREY_RULE,
                             hAlign="CENTER", spaceAfter=20))

    callout_text = (
        "Thirsty-Lang is the human-readable orchestration layer for governance-bound "
        "execution inside Project-AI. The UTF — Universal Thirsty Family — is the "
        "broader family of languages, encodings, runtimes, and symbolic systems that "
        "carry Project-AI's constitutional execution model across source code, policy, "
        "bytecode, simulation, and runtime enforcement."
    )
    story.append(Paragraph(callout_text, S["Callout"]))
    # No PageBreak here — the first H1 in body already prepends one
    return story


# ── Build source map CSV ────────────────────────────────────────────────────────
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
     "Numbered list 1-6", "HIGH",
     "Primary source"),
    ("UTF README describes amplified bootstrap",
     "src/utf/README.md",
     "Full document; 'What is executable now' section", "HIGH",
     "Primary source"),
    ("Thirsty-Lang keyword set (complete)",
     "src/utf/thirsty_lang/token.py",
     "KEYWORDS dict + TokenType enum", "HIGH",
     "Definitive keyword list"),
    ("Thirsty-Lang lexer fully implemented",
     "src/utf/thirsty_lang/lexer.py",
     "Complete Python class; Lexer.lex()", "HIGH",
     ""),
    ("Shadow Thirst 6 analyzers",
     "src/utf/shadow_thirst/core.py",
     "analyze() function returns 6 AnalysisResult per mutation", "HIGH",
     ""),
    ("Shadow Thirst promote/reject verdict",
     "src/utf/shadow_thirst/core.py",
     "promote() function returns PROMOTE or REJECT", "HIGH",
     ""),
    ("TSCG 9 core symbols",
     "src/utf/tscg/core.py",
     "CORE_SYMBOLS dict", "HIGH",
     "COG DNT SHD INV CAP QRM COM ANC RFX"),
    ("TSCG-B magic = TSGB",
     "src/utf/tscg_b/core.py",
     "MAGIC = b'TSGB'", "HIGH",
     ""),
    ("TSCG-B CRC32 + SHA-256 integrity",
     "src/utf/tscg_b/core.py",
     "pack_text() and unpack_frame()", "HIGH",
     ""),
    ("TARL policy default = DENY",
     "src/utf/tarl/core.py",
     "evaluate() returns 'DENY' when no rule matches (line 151)", "HIGH",
     "Fail-closed behavior"),
    ("TarlVerdict: ALLOW/DENY/ESCALATE",
     "tarl/spec.py",
     "TarlVerdict enum", "HIGH",
     ""),
    ("TarlRuntime LRU cache + parallel eval",
     "tarl/runtime.py",
     "TarlRuntime class with _decision_cache and ThreadPoolExecutor", "HIGH",
     ""),
    ("TARL 8 subsystems layered architecture",
     "tarl/docs/ARCHITECTURE.md; tarl/docs/WHITEPAPER.md",
     "Layer 0-7 documented in both docs", "HIGH",
     ""),
    ("TARL bytecode format TARL_BYTECODE_V1",
     "tarl/docs/WHITEPAPER.md",
     "Section 3.2 Bytecode Format", "HIGH",
     ""),
    ("TARL OS 29 subsystems ~13600 LOC",
     "tarl_os/TARL_OS_COMPLETE_IMPLEMENTATION_REPORT.md",
     "Executive Summary section", "MEDIUM",
     "Self-reported; not independently verified"),
    ("TARL OS v2 vs v3 conflict",
     "tarl_os/README.md (v2.0) vs tarl_os/TARL_OS_COMPLETE_IMPLEMENTATION_REPORT.md (v3.0)",
     "Two documents with different version numbers", "DOCUMENTED CONFLICT",
     "Report is newer (2026-02-08 vs 2026-01-30)"),
    ("5 constitutional rules with actions",
     "tarl_os/security/thirstys_constitution.thirsty",
     "initConstitution() pushes 5 rule objects with action fields", "HIGH",
     ""),
    ("Enforcement gateway fail-closed",
     "tarl_os/security/thirstys_enforcement_gateway.thirsty",
     "!enforcementActive branch returns allowed:false 'Gateway offline'", "HIGH",
     ""),
    ("Iron Path full pipeline with crypto",
     "governance/iron_path.py",
     "_execute_stage() with role_sig, policy_binding, sha256 hash", "HIGH",
     ""),
    ("build.tarl uses Thirsty-Lang syntax",
     "build.tarl",
     "Full file: drink/glass/pour/shield/thirsty keywords", "HIGH",
     ""),
    ("Scheduler 8 priority levels",
     "tarl_os/kernel/scheduler.thirsty",
     "PRIORITY_REALTIME=0 through PRIORITY_IDLE=7", "HIGH",
     ""),
    ("PSIA acronym expansion",
     "None",
     "Inferred from src/psia/ directory name and Shadow Thirst spec", "LOW",
     "Undocumented — needs confirmation"),
    ("Triumvirate server implementation",
     "governance/triumvirate_server.py",
     "File exists — content not read", "LOW",
     "Needs further inspection"),
    ("Hello Thirsty example",
     "src/utf/examples/hello.thirsty",
     "glass main() -> Int { pour('hello, thirsty world'); return 0; }", "HIGH",
     ""),
    ("PromotionGate policy example",
     "src/utf/examples/policy.tarl",
     "policy PromotionGate { ... } with 3 rules", "HIGH",
     ""),
    ("Shadow mutation example",
     "src/utf/examples/promote.shadowthirst",
     "mutation validated_canonical set_counter(value: Int) { shadow invariant canonical }", "HIGH",
     ""),
]


def write_csv():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Claim", "Source File", "Evidence", "Confidence", "Notes"])
        writer.writerows(SOURCE_MAP)
    print(f"CSV written: {CSV_FILE}")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE ENHANCEMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def implementation_statistics_section():
    """Generate comprehensive UTF implementation statistics section."""
    story = []
    story.append(PageBreak())
    story.append(Paragraph("UTF Implementation Statistics", S["H1"]))
    
    # Summary table
    summary_data = [
        ["Metric", "Value"],
        ["Total Python Files", str(UTF_STATS["total_python_files"])],
        ["Total Lines of Code", f'{UTF_STATS["total_lines_of_code"]:,}'],
        ["Total Size", f'{UTF_STATS["total_size_kb"]} KB'],
        ["Example Files", str(UTF_STATS["examples"])],
        ["Test Coverage", UTF_STATS.get("test_coverage", "N/A")],
        ["Subdirectories", str(UTF_STATS["subdirectories"])],
    ]
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
    summary_table.setStyle(table_style())
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Module breakdown
    story.append(Paragraph("Module Breakdown", S["H2"]))
    module_data = [["Module", "Files", "Lines", "Description"]]
    for name, stats in UTF_STATS["modules"].items():
        module_data.append([
            name,
            str(stats["files"]),
            f'{stats["lines"]:,}',
            stats.get("desc", "")
        ])
    module_table = Table(module_data, colWidths=[2.2*inch, 0.8*inch, 1*inch, 2*inch])
    module_table.setStyle(table_style())
    story.append(module_table)
    
    return story

def utf_feature_matrix_section():
    """Generate UTF tier feature comparison matrix."""
    story = []
    story.append(PageBreak())
    story.append(Paragraph("UTF Feature Matrix — Six-Tier Architecture", S["H1"]))
    story.append(Paragraph(
        "The Universal Thirsty Family implements a governance-first execution model "
        "across six integrated tiers, each building upon the previous layer.",
        S["Body"]
    ))
    story.append(Spacer(1, 0.15*inch))
    
    feature_table = Table(UTF_FEATURE_MATRIX, 
                         colWidths=[0.5*inch, 1.5*inch, 1.3*inch, 2.2*inch, 1*inch])
    feature_table.setStyle(table_style())
    story.append(feature_table)
    
    return story

def architecture_overview_section():
    """Generate detailed architecture component overview."""
    story = []
    story.append(PageBreak())
    story.append(Paragraph("Architecture Overview — Component Directory", S["H1"]))
    story.append(Paragraph(
        "UTF is implemented as a cohesive Python package under src/utf/ with clear "
        "separation of concerns across lexing, parsing, interpretation, policy "
        "enforcement, mutation validation, and serialization.",
        S["Body"]
    ))
    story.append(Spacer(1, 0.15*inch))
    
    arch_table = Table(ARCHITECTURE_OVERVIEW,
                      colWidths=[1.3*inch, 2*inch, 0.6*inch, 0.7*inch, 1.4*inch])
    arch_table.setStyle(table_style())
    story.append(arch_table)
    
    return story

def comprehensive_examples_section():
    """Generate all UTF examples with detailed explanations."""
    story = []
    story.append(PageBreak())
    story.append(Paragraph("UTF Examples — Proof of Concept Walkthroughs", S["H1"]))
    story.append(Paragraph(
        "The following examples demonstrate UTF capabilities across all tiers, "
        "from basic Thirsty-Lang syntax through Shadow Thirst mutation validation. "
        "All examples are executable via the UTF CLI.",
        S["Body"]
    ))
    
    for filename, title, code in UTF_EXAMPLES:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Example: {title}", S["H2"]))
        story.append(Paragraph(f"<i>File: src/utf/examples/{filename}</i>", S["Body"]))
        story.append(Spacer(1, 0.1*inch))
        
        # Split code into lines and wrap in Code style
        for line in code.split('\n'):
            if line.strip():
                story.append(Paragraph(line.replace(" ", "&nbsp;"), S["Code"]))
            else:
                story.append(Spacer(1, 2))
        
        # Add execution command
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            f'<i>Execute:</i> <font face="Courier" size="8">python -m src.utf.thirsty_lang {filename}</font>',
            S["Body"]
        ))
    
    return story


# ── Main PDF builder ────────────────────────────────────────────────────────────
def build_pdf():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # Remove the title block — we build it manually
    # Strip everything up to and including the first HR line
    lines = md_text.splitlines()
    start = 0
    hr_count = 0
    for idx, ln in enumerate(lines):
        if re.match(r"^---+$", ln.strip()):
            hr_count += 1
            if hr_count == 1:
                start = idx + 1
                break
    md_body = "\n".join(lines[start:])

    doc = DocTemplate(
        str(PDF_FILE),
        pagesize=letter,
        doc_title="Thirsty-Lang & UTF Reference v1.2 — Comprehensive",
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.5 * inch,
    )

    story = []

    # Title page
    story.extend(title_page())
    
    # ═══ COMPREHENSIVE COVERAGE ENHANCEMENT ═══
    # NEW: Implementation statistics (jaw-dropping data)
    print("Adding implementation statistics...")
    story.extend(implementation_statistics_section())
    
    # NEW: UTF feature matrix (6-tier comparison)
    print("Adding UTF feature matrix...")
    story.extend(utf_feature_matrix_section())
    
    # NEW: Architecture overview (component directory)
    print("Adding architecture overview...")
    story.extend(architecture_overview_section())
    
    # NEW: Comprehensive examples (all POCs with walkthroughs)
    print("Adding comprehensive examples...")
    story.extend(comprehensive_examples_section())

    # Body from Markdown
    print("Parsing markdown body...")
    body_story = parse_md(md_body)
    story.extend(body_story)

    print(f"Building comprehensive PDF ({len(story)} flowables)...")
    doc.build(story)
    print(f"✓ PDF written: {PDF_FILE}")
    print(f"  Total size: {PDF_FILE.stat().st_size // 1024} KB")
    print(f"  Comprehensive coverage: Statistics, Features, Architecture, Examples + Full Reference")


if __name__ == "__main__":
    write_csv()
    build_pdf()
    print("Done.")
