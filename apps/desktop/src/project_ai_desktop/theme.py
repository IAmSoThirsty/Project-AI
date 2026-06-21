"""OMPT-derived Qt development theme."""

STYLESHEET = """
QWidget { background: #05070b; color: #edf4ff; font-family: "Segoe UI"; font-size: 14px; }
QMainWindow { background: #05070b; }
QFrame#sidebar { background: #080d14; border-right: 1px solid #25334a; }
QLabel#brand { color: #edf4ff; font-size: 22px; font-weight: 700; padding: 20px 14px; }
QLabel#eyebrow { color: #d8a749; font-family: Consolas; font-size: 11px; text-transform: uppercase; }
QLabel#title { font-size: 28px; font-weight: 700; }
QLabel#muted { color: #9aa9bd; }
QListWidget { background: transparent; border: 0; outline: 0; padding: 6px; }
QListWidget::item { color: #9aa9bd; padding: 13px 14px; margin: 2px 0; border-radius: 8px; }
QListWidget::item:selected { color: #edf4ff; background: #172947; border-left: 3px solid #70a7ff; }
QPushButton { background: #162947; border: 1px solid #34547e; border-radius: 8px; padding: 9px 16px; }
QPushButton:hover { background: #203a64; border-color: #70a7ff; }
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox { background: #080d14; border: 1px solid #25334a; border-radius: 8px; padding: 9px; selection-background-color: #2f6fff; }
QTableWidget { background: #080d14; alternate-background-color: #0c121d; border: 1px solid #25334a; gridline-color: #25334a; }
QHeaderView::section { background: #0c121d; color: #9aa9bd; border: 0; border-bottom: 1px solid #25334a; padding: 8px; }
QGroupBox { border: 1px solid #25334a; border-radius: 12px; margin-top: 12px; padding: 18px 12px 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #70a7ff; }
QStatusBar { background: #080d14; color: #9aa9bd; border-top: 1px solid #25334a; }
"""
