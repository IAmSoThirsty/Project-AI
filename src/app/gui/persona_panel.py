# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / persona_panel.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / persona_panel.py

# T-A-R-L (Thirsty's Active Resistance Language): MAXIMUM (+10x stronger)
# Technical Spec: [/docs/TARL_SPEC.md]
# Job Board Panel - Capability Expansion UI.

import logging
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QProgressBar,
    QFrame,
)

from src.app.core.ai_systems import AIPersona, FourLaws

logger = logging.getLogger(__name__)


class SkillWidget(QFrame):
    """A single skill cell in the high-density Skill Tree."""

    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.setFixedSize(140, 80)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setFrameShape(QFrame.Shape.Box)

        status_color = "#00ffff" if self.skill.unlocked else "#444444"
        self.setStyleSheet(f"""
            SkillWidget {{
                background-color: #050505;
                border: 1px solid {status_color};
                border-radius: 4px;
            }}
            QLabel {{
                color: {status_color};
            }}
        """)

        name = QLabel(self.skill.name)
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setFont(QFont("Inter", 8, QFont.Weight.Bold))

        req = QLabel(f"LVL {self.skill.level_required}")
        req.setAlignment(Qt.AlignmentFlag.AlignCenter)
        req.setStyleSheet("font-size: 9px; color: #888888;")

        layout.addWidget(name)
        layout.addWidget(req)


class JobBoardPanel(QWidget):
    """The High-Density Job Board UI for Partner Capability Expansion."""

    job_changed = pyqtSignal(str)
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.persona: AIPersona | None = None
        self.job_widgets = {}
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(self._get_high_density_stylesheet())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header: Cathedral Density Aesthetics
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)

        back_btn = QPushButton("◄ ESC")
        back_btn.setFixedWidth(80)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)

        title_layout = QVBoxLayout()
        title = QLabel("JOB BOARD")
        title.setObjectName("MainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("PARTNER CAPABILITY EXPANSION (Skill Progression Platform)")
        subtitle.setObjectName("SubTitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout, 1)

        tarl_link = QLabel(
            '<a href="file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/docs/TARL_SPEC.md" style="color: #00ff00; text-decoration: none;">T-A-R-L SPEC (Defensive Logic)</a>'
        )
        tarl_link.setOpenExternalLinks(True)
        tarl_link.setStyleSheet("font-size: 9px;")
        header_layout.addWidget(tarl_link)

        layout.addWidget(header_frame)

        # Main Content Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_jobs_tab(), "💠 JOBS")
        self.tabs.addTab(self.create_skill_tree_tab(), "🌳 SKILLS")
        self.tabs.addTab(self.create_laws_tab(), "📜 LAWS")

        layout.addWidget(self.tabs)

    def create_jobs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.job_grid_widget = QWidget()
        self.job_grid = QGridLayout(self.job_grid_widget)
        self.job_grid.setSpacing(20)

        scroll.setWidget(self.job_grid_widget)
        layout.addWidget(scroll)
        return widget

    def create_skill_tree_tab(self) -> QWidget:
        widget = QWidget()
        self.skill_layout = QVBoxLayout(widget)
        self.no_job_label = QLabel("SELECT A JOB TO VIEW SKILL TREE")
        self.no_job_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.skill_layout.addWidget(self.no_job_label)
        return widget

    def create_laws_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        laws_display = QTextEdit()
        laws_display.setReadOnly(True)
        laws_display.setMarkdown(
            "# T-A-R-L ALIGNMENT PROTOCOLS (Asimovian Ethical Constraints)\n\n"
            + "\n\n".join([f"> **{law}**" for law in FourLaws.LAWS])
        )
        layout.addWidget(laws_display)
        return widget

    def set_persona(self, persona: AIPersona):
        self.persona = persona
        self.refresh_jobs()

    def refresh_jobs(self):
        while self.job_grid.count():
            item = self.job_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.persona:
            return

        row, col = 0, 0
        for job in self.persona.jobs.values():
            card = self._create_job_card(job)
            self.job_grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _create_job_card(self, job) -> QWidget:
        card = QFrame()
        card.setObjectName("JobCard")
        is_active = self.persona.active_job_id == job.job_id
        if is_active:
            card.setProperty("active", True)

        layout = QVBoxLayout(card)

        name = QLabel(job.name.upper())
        name.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ffff;")

        rank = QLabel(f"RANK: {self.persona.get_rank_name(job.job_id)}")
        rank.setStyleSheet("color: #888888; font-size: 10px;")

        prog_bar = QProgressBar()
        prog_bar.setMaximum(100)
        xp_percent = job.xp % 100
        prog_bar.setValue(xp_percent)

        btn = QPushButton("SELECT" if not is_active else "ACTIVE")
        btn.setEnabled(not is_active)
        btn.clicked.connect(lambda: self._on_job_selected(job.job_id))

        layout.addWidget(name)
        layout.addWidget(rank)
        layout.addWidget(prog_bar)
        layout.addWidget(btn)
        return card

    def _on_job_selected(self, job_id: str):
        if self.persona:
            self.persona.set_active_job(job_id)
            self.refresh_jobs()
            self.refresh_skill_tree()
            self.job_changed.emit(job_id)

    def refresh_skill_tree(self):
        while self.skill_layout.count():
            item = self.skill_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.persona or not self.persona.active_job_id:
            self.skill_layout.addWidget(QLabel("SELECT A JOB TO VIEW SKILL TREE"))
            return

        active_job = self.persona.jobs[self.persona.active_job_id]

        title = QLabel(
            f"{active_job.name} - NEURAL SKILL TREE (Capability Augmentation)"
        )
        title.setStyleSheet("font-size: 16px; color: #00ffff; margin-bottom: 10px;")
        self.skill_layout.addWidget(title)

        grid_container = QWidget()
        grid = QGridLayout(grid_container)

        skills = list(active_job.skills.values())
        for i, skill in enumerate(skills):
            widget = SkillWidget(skill)
            grid.addWidget(widget, i // 4, i % 4)

        self.skill_layout.addWidget(grid_container)
        self.skill_layout.addStretch()

    def _get_high_density_stylesheet(self) -> str:
        return """
        QWidget {
            background-color: #050505;
            color: #ffffff;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }
        #HeaderFrame {
            border-bottom: 1px solid #00ffff;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #002222, stop:1 #050505);
        }
        #MainTitle {
            color: #00ffff;
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 2px;
        }
        #SubTitle {
            color: #008888;
            font-size: 10px;
            letter-spacing: 4px;
        }
        QTabWidget::pane {
            border: 1px solid #004444;
            top: -1px;
            background: #050505;
        }
        QTabBar::tab {
            background: #0a0a0a;
            color: #008888;
            padding: 12px 30px;
            border: 1px solid #004444;
            border-bottom: none;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #002222;
            color: #00ffff;
            border: 1px solid #00ffff;
            border-bottom: 1px solid #050505;
        }
        #JobCard {
            background: #0a0a0a;
            border: 1px solid #004444;
            border-radius: 8px;
            padding: 15px;
        }
        #JobCard[active="true"] {
            border: 1px solid #00ffff;
            background: #001111;
        }
        QPushButton {
            background: #00ffff;
            color: #050505;
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:disabled {
            background: #004444;
            color: #008888;
        }
        QProgressBar {
            border: 1px solid #004444;
            background: #050505;
            height: 6px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #00ffff;
        }
        QTextEdit {
            background: #0a0a0a;
            border: 1px solid #004444;
            color: #cccccc;
            padding: 10px;
        }
        """


# For compatibility during transition
PersonaPanel = JobBoardPanel
