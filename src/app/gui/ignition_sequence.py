#                                           [2026-03-04 21:09]
#                                          Productivity: Active
"""
Cinematic Ignition Sequence for Project-AI Prime.
Features: Leather book, ray of light, holographic runes, and flying pages.
"""

import math
from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSignal,
    QPointF,
)
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QFont
from PyQt6.QtWidgets import QWidget, QApplication


class RuneItem:
    def __init__(self, char, angle, radius):
        self.char = char
        self.angle = angle
        self.radius = radius
        self.opacity = 0.0


class IgnitionSequence(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()

        self.animation_step = 0
        self.book_scale = 0.5
        self.runes = [RuneItem(chr(0x16A0 + i), i * 30, 200) for i in range(12)]
        self.flying_pages = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def update_animation(self):
        self.animation_step += 1

        # Phase 1: Ray of Light Intensity
        # Phase 2: Rune Illumination
        if self.animation_step > 50:
            for rune in self.runes:
                rune.opacity = min(1.0, rune.opacity + 0.05)
                rune.angle += 2

        # Phase 3: Book Scaling
        if self.animation_step > 100:
            self.book_scale = min(1.0, self.book_scale + 0.01)

        # Phase 4: Flying Pages
        if self.animation_step > 150:
            if len(self.flying_pages) < 20 and self.animation_step % 5 == 0:
                self.flying_pages.append({"y": 0, "rot": 0, "opacity": 1.0})

            for page in self.flying_pages:
                page["y"] -= 20
                page["rot"] += 5
                page["opacity"] -= 0.05

        # End of sequence
        if self.animation_step > 250:
            self.timer.stop()
            self.finished.emit()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()

        # Ray of Light (Radial Gradient)
        gradient = QRadialGradient(QPointF(center), self.width() // 2)
        gradient.setColorAt(
            0,
            QColor(
                255, 255, 200, int(150 * math.sin(self.animation_step * 0.05) + 100)
            ),
        )
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), gradient)

        # 3D Leather Book Representation (Stylized)
        painter.save()
        painter.translate(center)
        painter.scale(self.book_scale, self.book_scale)

        # Book shadow
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(-150, -200, 300, 400, 20, 20)

        # Book Cover
        painter.setBrush(QColor(60, 30, 10))
        painter.setPen(QColor(100, 70, 40))
        painter.drawRoundedRect(-140, -190, 280, 380, 15, 15)

        # Sovereign Seal
        painter.setPen(QColor(212, 175, 55))  # Gold
        painter.setFont(QFont("Georgia", 24, QFont.Weight.Bold))
        painter.drawText(
            -100, -50, 200, 100, Qt.AlignmentFlag.AlignCenter, "PROJECT-AI\nPRIME"
        )
        painter.restore()

        # Holographic Runes
        painter.setFont(QFont("Courier New", 18))
        for rune in self.runes:
            if rune.opacity > 0:
                painter.save()
                painter.translate(center)
                x = rune.radius * math.cos(math.radians(rune.angle))
                y = rune.radius * math.sin(math.radians(rune.angle))
                painter.setPen(QColor(0, 255, 255, int(rune.opacity * 255)))
                painter.drawText(int(x), int(y), rune.char)
                painter.restore()

        # Flying Pages
        for page in self.flying_pages:
            if page["opacity"] > 0:
                painter.save()
                painter.translate(center.x(), center.y() + page["y"])
                painter.rotate(page["rot"])
                painter.setBrush(QColor(255, 255, 240, int(page["opacity"] * 255)))
                painter.drawRect(-50, -70, 100, 140)
                painter.restore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
