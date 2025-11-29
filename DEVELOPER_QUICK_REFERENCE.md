# Leather Book UI - Developer Quick Reference

## File Locations

| File | Purpose | Status |
|------|---------|--------|
| `src/app/gui/leather_book_interface.py` | Main container with login/dashboard switching | ✅ Ready |
| `src/app/gui/leather_book_dashboard.py` | 6-zone dashboard with chat and AI head | ✅ Ready |
| `src/app/main.py` | Application entry point | ✅ Updated |

## Quick Start Commands

Run the application:

    cd c:\Users\Jeremy\Documents\GitHub\Project-AI
    python -m src.app.main

## Component Reference

### LeatherBookInterface

**Location**: `src/app/gui/leather_book_interface.py`

Main window with left Tron page and right page switcher.

Usage: `window = LeatherBookInterface()`

Then: `window.switch_to_main_dashboard(username="user")`

Signals: `user_logged_in(str)`, `page_changed(int)`

### LeatherBookDashboard

**Location**: `src/app/gui/leather_book_dashboard.py`

Main dashboard with 6-zone layout (stats, actions, AI head, chat, response).

Usage: `dashboard = LeatherBookDashboard(username="user")`

Signals: `send_message(str)`

Methods: `add_ai_response(response: str)`

### StatsPanel

Display system metrics (top-left). Updates every 1 second.

Displays: Uptime, Memory, CPU, Session time

### ProactiveActionsPanel

Show background tasks (top-right).

Contains: Scrollable task list, ANALYZE button, OPTIMIZE button

### UserChatPanel

Chat message input (bottom-left).

Signal: `message_sent(str)` emitted when user clicks SEND

### AINeuralHead

Central AI visualization (center).

Methods: `start_thinking()`, `stop_thinking()`

Shows status: READY, THINKING, RESPONDING

### AIResponsePanel

Message history display (bottom-right).

Methods: `add_user_message(message: str)`, `add_ai_response(response: str)`

## Color Constants

Tron (Left page, primary):

- TRON_GREEN = "#00ff00"
- TRON_CYAN = "#00ffff"
- TRON_BLACK = "#0a0a0a"

Leather (Right page):

- LEATHER_BROWN = "#8b7355"
- LEATHER_DARK = "#2a2a1a"
- LEATHER_DARKER = "#1a1a0f"

UI Elements:

- PANEL_BG = "#0f0f0f"
- INPUT_BG = "#1a1a1a"
- TEXT_COLOR = "#e0e0e0"

## Styling

Glow effects:

- Strong glow (titles): `text-shadow: 0px 0px 15px #00ffff;`
- Medium glow (text): `text-shadow: 0px 0px 10px #00ff00;`
- Subtle glow: `text-shadow: 0px 0px 5px #00ff00;`

Border styling:

- Standard border: `border: 2px solid #00ff00;`
- Focus/hover: `border: 2px solid #00ffff;`
- Rounded corners: `border-radius: 5px;`

## Animation Timings

| Element | Interval | Formula |
|---------|----------|---------|
| Face eyes | 50ms | `sin(frame * 0.05)` |
| Face mouth | 50ms | `cos(frame * 0.05)` |
| Stats update | 1000ms | Counter increment |
| UI refresh | 50ms | `update()` call |

## Common Integration Tasks

### Connect AI Backend

    dashboard = LeatherBookDashboard(username)
    
    def process_ai_message(user_message: str):
        response = ai_model.generate_response(user_message)
        dashboard.add_ai_response(response)
    
    dashboard.send_message.connect(process_ai_message)

### Connect Database

Save messages by overriding AIResponsePanel.add_ai_response():

    def add_ai_response(self, response: str):
        db.save_message(user=username, content=response, is_ai=True)
        super().add_ai_response(response)

### Connect Real System Stats

Replace simulated values in StatsPanel._update_stats():

    import psutil
    
    memory_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=0.1)

## Common Customization Tasks

### Change Animation Speed

Modify timer interval in `LeatherBookDashboard.__init__`:

    self.animation_timer.start(50)  # milliseconds

### Add New Panel

    class NewPanel(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            # Add widgets...

### Add New Button

    new_btn = QPushButton("MY BUTTON")
    new_btn.setStyleSheet("""
        QPushButton {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
        }
    """)
    new_btn.clicked.connect(callback_function)

## Testing Checklist

- Application starts without errors
- Login page displays correctly
- User can enter credentials and submit
- Dashboard displays after login
- Stats panel updates every second
- AI head animates smoothly (50ms timer)
- Chat message can be sent
- User message appears in response panel
- AI message can be added to response panel
- Thinking animation works (colors change)
- All buttons are clickable
- All text is readable (sufficient contrast)
- Window resizes without crashing

## Troubleshooting

### Face doesn't animate

Cause: animation_timer not started

Fix: Check `self.animation_timer.start(50)` in `__init__`

### Stats don't update

Cause: stats_timer not started or update_stats() not connected

Fix: Check timer interval and connection in StatsPanel

### Colors look wrong

Cause: Stylesheet not applied or overridden

Fix: Check setStyleSheet() calls and inheritance chain

---

**Version**: 1.0  
**Status**: Production Ready ✅
