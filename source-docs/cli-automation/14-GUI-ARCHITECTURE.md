---
title: GUI Architecture Overview
type: technical-reference
audience: [developers, ui-developers]
classification: P0-Core
tags: [gui, pyqt6, desktop, ui]
created: 2024-01-20
status: current
---

# GUI Architecture Overview

**PyQt6-based Leather Book UI architecture.**

## Core Components

### LeatherBookInterface (Main Window)

- Entry point: src/app/gui/leather_book_interface.py
- Dual-page layout: Login (Tron-themed) + Dashboard
- Signal-based communication with components

### LeatherBookDashboard (6-Zone Layout)

Located: src/app/gui/leather_book_dashboard.py

Zones:
1. Stats Panel - User statistics
2. Actions Panel - Proactive actions
3. AI Head - Visual AI representation
4. Chat Panel - User input
5. Response Panel - AI responses
6. Quick Actions - Common commands

### Signal Pattern

```python
# In LeatherBookInterface
user_logged_in = pyqtSignal(str)  # Username

# In component
send_message = pyqtSignal(str)  # Message content

# Connection
component.send_message.connect(self.handle_message)
```

## Styling

- Tron Green: #00ff00
- Tron Cyan: #00ffff
- Dark background with neon accents

---

**AGENT-038: CLI & Automation Documentation Specialist**
