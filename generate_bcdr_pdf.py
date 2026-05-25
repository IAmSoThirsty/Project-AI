#!/usr/bin/env python3
"""Convert BCDR markdown to PDF using reportlab"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import re

def parse_markdown_to_elements(md_text):
    """Convert markdown to reportlab elements"""
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        spaceBefore=20,
        borderWidth=2,
        borderColor=colors.black,
        borderPadding=5
    ))

    styles.add(ParagraphStyle(
        name='CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2a2a2a'),
        spaceAfter=10,
        spaceBefore=15
    ))

    styles.add(ParagraphStyle(
        name='CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#3a3a3a'),
        spaceAfter=8,
        spaceBefore=12
    ))

    styles.add(ParagraphStyle(
        name='CustomCode',
        fontName='Courier',
        fontSize=8,
        leftIndent=20,
        rightIndent=20,
        textColor=HexColor('#333333'),
        backColor=HexColor('#f4f4f4')
    ))

    elements = []
    lines = md_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip frontmatter
        if line.strip() == '---' and i < 20:
            i += 1
            while i < len(lines) and lines[i].strip() != '---':
                i += 1
            i += 1
            continue

        # Headers
        if line.startswith('# '):
            elements.append(Paragraph(line[2:], styles['CustomTitle']))
            elements.append(Spacer(1, 0.1*inch))
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], styles['CustomH2']))
            elements.append(Spacer(1, 0.1*inch))
        elif line.startswith('### '):
            elements.append(Paragraph(line[4:], styles['CustomH3']))
        elif line.startswith('#### '):
            elements.append(Paragraph(f"<b>{line[5:]}</b>", styles['Normal']))

        # Horizontal rule
        elif line.strip() == '---':
            elements.append(Spacer(1, 0.2*inch))

        # Code blocks
        elif line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                code_text = '\n'.join(code_lines)
                elements.append(Preformatted(code_text, styles['CustomCode']))
                elements.append(Spacer(1, 0.1*inch))

        # Tables (simple parsing)
        elif '|' in line and i + 1 < len(lines) and '|' in lines[i+1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                if not lines[i].strip().startswith('|---'):
                    cells = [c.strip() for c in lines[i].split('|')[1:-1]]
                    table_lines.append(cells)
                i += 1

            if table_lines:
                table = Table(table_lines)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.15*inch))
            i -= 1

        # Bold text
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            text = line.strip()[2:-2]
            elements.append(Paragraph(f"<b>{text}</b>", styles['Normal']))

        # Regular paragraph
        elif line.strip() and not line.startswith('#'):
            # Handle inline bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            # Handle inline code
            text = re.sub(r'`(.*?)`', r'<font name="Courier" size="8">\1</font>', text)
            elements.append(Paragraph(text, styles['Normal']))

        # Empty line
        elif not line.strip() and elements:
            elements.append(Spacer(1, 0.05*inch))

        i += 1

    return elements

def convert_md_to_pdf():
    # Read markdown
    md_path = Path("docs/operations/PROJECT_AI_BCDR_PLAN.md")
    md_content = md_path.read_text(encoding='utf-8')

    # Output path
    output_path = Path("PROJECT_AI_BCDR_PLAN.pdf")

    # Create PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Convert markdown to elements
    elements = parse_markdown_to_elements(md_content)

    # Build PDF
    doc.build(elements)

    print(f"PDF generated: {output_path.absolute()}")
    return output_path

if __name__ == "__main__":
    convert_md_to_pdf()
