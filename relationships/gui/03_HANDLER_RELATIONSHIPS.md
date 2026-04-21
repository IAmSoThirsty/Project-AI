# Handler Relationships Map

## Component: DashboardHandlers [[src/app/gui/dashboard_handlers.py]]
**File:** `src/app/gui/dashboard_handlers.py`  
**Lines:** 400+  
**Role:** Event handlers routed through governance pipeline

---

## 1. HANDLER ARCHITECTURE

### Governance-Routed Pattern
```
OLD PATTERN (Direct):
Handler → Core System → Database

NEW PATTERN (Governance):
Handler → Desktop Adapter → Router → Governance → Core System → Database
             ↓ (fallback)
          Core System (if governance unavailable)
```

### Import Structure
```python
# Lines 1-15
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QWidget
from app.interfaces.desktop.integration import get_desktop_adapter
from app.security.data_validation import (
    sanitize_input,
    validate_email,
    validate_length,
)
```

---

## 2. HANDLER METHOD INVENTORY

### 2.1 Learning Path Handler
```python
def generate_learning_path(self):
    """Generate a learning path based on user input (governance-routed)"""
    # Lines 19-61
```

**Flow:**
```
1. User enters interest in self.interest_input (QLineEdit)
2. User selects skill level from self.skill_level (QComboBox)
3. User clicks "Generate" button
4. Handler validates input:
   ├── sanitize_input(interest, max_length=200)
   └── validate_length(interest, min_len=1, max_len=200)
5. If valid:
   ├── Call get_desktop_adapter()
   ├── adapter.execute("learning.generate_path", params)
   ├── If success → display path in self.learning_path_display
   └── If failure → log error + display error message
6. If adapter fails:
   └── Fallback to direct call: self.learning_manager.generate_path()
```

**Relationships:**
```
self.interest_input: QLineEdit (user input)
self.skill_level: QComboBox (beginner/intermediate/advanced)
self.learning_path_display: QTextEdit (output display)
self.user_manager: UserManager (current user context)
self.learning_manager: LearningRequestManager (fallback)
```

**Signals/Slots:**
```python
# Connection (likely in parent Dashboard)
generate_button.clicked.connect(self.generate_learning_path)
```

---

### 2.2 Data File Loader Handler
```python
def load_data_file(self):
    """Load a data file for analysis (governance-routed)"""
    # Lines 63-98
```

**Flow:**
```
1. User clicks "Load Data" button
2. QFileDialog.getOpenFileName() opens file picker
   ├── Filter: "Data Files (*.csv *.xlsx *.json);;All Files (*.*)"
   └── Returns: (file_path, selected_filter)
3. If file selected:
   ├── Call get_desktop_adapter()
   ├── adapter.execute("data.load_file", {"file_path": file_path})
   ├── If success:
   │   ├── Extract columns from response
   │   ├── Populate self.column_selector (QComboBox)
   │   └── Call self.show_basic_stats()
   └── If failure:
       └── QMessageBox.warning with error
4. If adapter fails:
   └── Fallback to direct call: self.data_analyzer.load_data(file_path)
```

**Relationships:**
```
self.column_selector: QComboBox (column selection dropdown)
self.data_analyzer: DataAnalysisManager (fallback)
get_desktop_adapter(): DesktopAdapter (governance routing)
```

**Signals/Slots:**
```python
# Connection (likely in parent Dashboard)
load_button.clicked.connect(self.load_data_file)
```

---

### 2.3 Data Analysis Performer Handler
```python
def perform_analysis(self):
    """Perform selected data analysis"""
    # Lines 100-150 (estimated)
```

**Flow:**
```
1. User selects column from self.column_selector
2. User selects analysis type (mean, median, clustering, etc.)
3. User clicks "Analyze" button
4. Handler validates selection
5. Call get_desktop_adapter()
6. adapter.execute("data.analyze", params)
7. Display results in analysis panel
```

**Relationships:**
```
self.column_selector: QComboBox (selected column)
self.analysis_type: QComboBox (analysis method)
self.analysis_results: QTextEdit (output display)
```

---

### 2.4 Security Resources Handler
```python
def load_security_resources(self):
    """Load security resources from GitHub (governance-routed)"""
    # Lines 150-200 (estimated)
```

**Flow:**
```
1. User selects category from self.security_category
2. Handler calls get_desktop_adapter()
3. adapter.execute("security.load_resources", {"category": category})
4. Populates self.resources_list (QListWidget)
5. User can double-click to open resource
```

**Relationships:**
```
self.security_category: QComboBox (CTF, exploits, tools, etc.)
self.resources_list: QListWidget (GitHub repos)
self.security_manager: SecurityResourcesManager (fallback)
```

---

### 2.5 Location Tracking Handler
```python
def toggle_location_tracking(self):
    """Enable/disable location tracking (governance-routed)"""
    # Lines 200-250 (estimated)
```

**Flow:**
```
1. User clicks self.location_toggle (QPushButton)
2. Handler calls get_desktop_adapter()
3. adapter.execute("location.toggle", {})
4. Updates button text and state
5. If enabled, starts location updates in StatsPanel
```

**Relationships:**
```
self.location_toggle: QPushButton (On/Off button)
self.location_tracker: LocationTracker (fallback)
StatsPanel.location_label: QLabel (display target)
```

---

### 2.6 Emergency Alert Handler
```python
def send_emergency_alert(self):
    """Send emergency alert to contacts (governance-routed)"""
    # Lines 250-300 (estimated)
```

**Flow:**
```
1. User clicks self.alert_button
2. Handler calls get_desktop_adapter()
3. adapter.execute("emergency.send_alert", {})
4. Sends emails to emergency contacts
5. Displays confirmation/error message
```

**Relationships:**
```
self.alert_button: QPushButton (red emergency button)
self.emergency_manager: EmergencyAlertManager (fallback)
self.emergency_contacts: list[str] (email addresses)
```

---

## 3. GOVERNANCE INTEGRATION PATTERN

### Standard Handler Template
```python
def handler_method(self):
    """Description (governance-routed)"""
    # Step 1: Validate input
    sanitized_input = sanitize_input(user_input, max_length=X)
    if not validate_length(sanitized_input, min_len=Y, max_len=X):
        QMessageBox.warning(self, "Input Error", "Invalid input")
        return
    
    # Step 2: Try governance-routed execution
    try:
        adapter = get_desktop_adapter()
        response = adapter.execute(
            "module.action",
            {
                "param1": sanitized_input,
                "user": self.user_manager.current_user,
            }
        )
        
        if response["status"] == "success":
            result = response["result"]
            # Update UI with result
            self.display_widget.setText(result)
        else:
            error_msg = response.get("error", "Unknown error")
            logger.error(f"Operation failed: {error_msg}")
            QMessageBox.warning(self, "Error", error_msg)
    
    # Step 3: Fallback to direct call
    except Exception as e:
        logger.error(f"Governance routing failed: {e}")
        # Direct call to core system
        result = self.core_system.method(sanitized_input)
        self.display_widget.setText(result)
```

---

## 4. ADAPTER EXECUTION MAPPING

### Governance Routes (Lines 36-45)
```python
adapter.execute("learning.generate_path", params)
# Routes to: CognitionKernel → LearningRequestManager.generate_path()

adapter.execute("data.load_file", params)
# Routes to: CognitionKernel → DataAnalysisManager.load_data()

adapter.execute("data.analyze", params)
# Routes to: CognitionKernel → DataAnalysisManager.analyze_column()

adapter.execute("security.load_resources", params)
# Routes to: CognitionKernel → SecurityResourcesManager.fetch_resources()

adapter.execute("location.toggle", params)
# Routes to: CognitionKernel → LocationTracker.toggle_tracking()

adapter.execute("emergency.send_alert", params)
# Routes to: CognitionKernel → EmergencyAlertManager.send_alert()
```

---

## 5. HANDLER-TO-UI RELATIONSHIPS

### Learning Path Handler
```
generate_learning_path()
        ↓
Accesses UI Components:
├── self.interest_input.text() → Read
├── self.skill_level.currentText() → Read
└── self.learning_path_display.setText() → Write
```

### Data File Handler
```
load_data_file()
        ↓
Accesses UI Components:
├── QFileDialog.getOpenFileName() → Dialog
├── self.column_selector.clear() → Modify
├── self.column_selector.addItems() → Modify
└── self.show_basic_stats() → Call another handler
```

### All Handlers Pattern
```
User clicks button → Handler called
                         ↓
Handler reads from input widgets (QLineEdit, QComboBox, etc.)
                         ↓
Handler validates + sanitizes input
                         ↓
Handler calls governance adapter OR direct core system
                         ↓
Handler writes to output widgets (QTextEdit, QLabel, QListWidget, etc.)
                         ↓
Handler shows feedback (QMessageBox, status updates)
```

---

## 6. ERROR HANDLING LAYERS

### Layer 1: Input Validation
```python
# Before processing
interest = sanitize_input(self.interest_input.text(), max_length=200)
if not validate_length(interest, min_len=1, max_len=200):
    QMessageBox.warning(self, "Input Error", "Interest must be 1-200 characters")
    return
```

### Layer 2: Governance Execution
```python
try:
    response = adapter.execute("action", params)
    if response["status"] == "success":
        # Handle success
    else:
        error_msg = response.get("error", "Unknown error")
        logger.error(f"Action failed: {error_msg}")
        QMessageBox.warning(self, "Error", error_msg)
```

### Layer 3: Fallback Execution
```python
except Exception as e:
    logger.error(f"Governance routing failed: {e}")
    # Fallback to direct call
    result = self.core_system.method(params)
```

### Layer 4: UI Feedback
```python
# Always provide feedback
if success:
    QMessageBox.information(self, "Success", "Operation completed")
else:
    QMessageBox.critical(self, "Error", error_message)
```

---

## 7. LOGGING STRATEGY

### Per-Handler Logging
```python
import logging
logger = logging.getLogger(__name__)

# In handler methods
logger.error(f"Learning path generation failed: {error_msg}")
logger.error(f"Failed to load data file through governance: {e}")
logger.warning(f"Governance unavailable, using fallback")
logger.info(f"Data file loaded successfully: {file_path}")
```

### Logged Events
- Input validation failures
- Governance execution errors
- Fallback activations
- Successful operations (info level)
- User selections (debug level)

---

## 8. SIGNAL/SLOT CONNECTIONS (Inferred)

### Button Connections
```python
# In parent Dashboard class (likely dashboard.py or dashboard_main.py)
from app.gui.dashboard_handlers import DashboardHandlers

class Dashboard(QWidget, DashboardHandlers):
    def __init__(self):
        super().__init__()
        
        # Learning Path tab
        self.generate_button.clicked.connect(self.generate_learning_path)
        
        # Data Analysis tab
        self.load_button.clicked.connect(self.load_data_file)
        self.analyze_button.clicked.connect(self.perform_analysis)
        
        # Security Resources tab
        self.security_category.currentTextChanged.connect(
            self.load_security_resources
        )
        self.resources_list.itemDoubleClicked.connect(
            self.open_security_resource
        )
        
        # Location Tracker tab
        self.location_toggle.clicked.connect(self.toggle_location_tracking)
        self.clear_history_btn.clicked.connect(self.clear_location_history)
        
        # Emergency Alert tab
        self.alert_button.clicked.connect(self.send_emergency_alert)
        self.save_contacts_btn.clicked.connect(self.save_emergency_contacts)
```

---

## 9. HANDLER DEPENDENCIES

### Required Imports
```python
from app.interfaces.desktop.integration import get_desktop_adapter
from app.security.data_validation import (
    sanitize_input,
    validate_email,
    validate_length,
)
```

### Required Instance Variables (Set by Parent)
```python
self.user_manager: UserManager
self.learning_manager: LearningRequestManager
self.data_analyzer: DataAnalysisManager
self.security_manager: SecurityResourcesManager
self.location_tracker: LocationTracker
self.emergency_manager: EmergencyAlertManager
```

### Required UI Components (Set by Parent)
```python
# Learning Path
self.interest_input: QLineEdit
self.skill_level: QComboBox
self.learning_path_display: QTextEdit

# Data Analysis
self.column_selector: QComboBox
self.analysis_type: QComboBox
self.analysis_results: QTextEdit

# Security Resources
self.security_category: QComboBox
self.resources_list: QListWidget

# Location Tracking
self.location_toggle: QPushButton
self.location_display: QLabel

# Emergency Alert
self.alert_button: QPushButton
self.emergency_contacts: QListWidget
```

---

## 10. HANDLER EXECUTION FLOW

### Complete Flow Example (Learning Path)
```
USER ACTION: Clicks "Generate Learning Path" button
        ↓
SIGNAL EMISSION: generate_button.clicked
        ↓
SLOT EXECUTION: self.generate_learning_path()
        ↓
INPUT READING:
├── interest = self.interest_input.text()
└── skill_level = self.skill_level.currentText()
        ↓
VALIDATION:
├── sanitize_input(interest, max_length=200)
└── validate_length(interest, min_len=1, max_len=200)
        ↓
GOVERNANCE ROUTING:
├── adapter = get_desktop_adapter()
├── response = adapter.execute("learning.generate_path", params)
└── If failure → fallback to self.learning_manager.generate_path()
        ↓
RESULT PROCESSING:
├── If success: path = response["result"]["path"]
└── If error: error_msg = response.get("error", "Unknown error")
        ↓
UI UPDATE:
├── self.learning_path_display.setText(path)
└── Or: QMessageBox.warning(self, "Error", error_msg)
        ↓
LOGGING:
├── logger.info("Learning path generated successfully")
└── Or: logger.error(f"Learning path generation failed: {error_msg}")
        ↓
COMPLETION: Handler returns, UI remains responsive
```

---

## 11. HANDLER VS PANEL RESPONSIBILITIES

### Handlers (DashboardHandlers)
- **Purpose:** Business logic, data processing, governance routing
- **Concerns:** Validation, error handling, logging, fallback strategies
- **Not concerned with:** Layout, styling, widget creation

### Panels (Dashboard Panels)
- **Purpose:** UI structure, display, user interaction
- **Concerns:** Layout, styling, widget properties, signals
- **Not concerned with:** Business logic, data validation

### Separation Pattern
```
Panel creates UI:
├── interest_input = QLineEdit()
├── generate_btn = QPushButton("Generate")
└── learning_path_display = QTextEdit()

Panel connects signals:
├── generate_btn.clicked.connect(self.generate_learning_path)

Handler processes logic:
├── validate input from self.interest_input
├── call governance adapter
└── update self.learning_path_display
```

---

## 12. TESTING STRATEGIES

### Unit Tests for Handlers
```python
# test_dashboard_handlers.py
import pytest
from unittest.mock import Mock, patch
from app.gui.dashboard_handlers import DashboardHandlers

class TestDashboardHandlers:
    @pytest.fixture
    def handler(self):
        handler = DashboardHandlers()
        handler.interest_input = Mock()
        handler.skill_level = Mock()
        handler.learning_path_display = Mock()
        handler.user_manager = Mock()
        return handler
    
    def test_generate_learning_path_validation(self, handler):
        """Test input validation in learning path handler."""
        handler.interest_input.text.return_value = ""  # Empty input
        handler.generate_learning_path()
        # Should show warning, not call adapter
        assert not handler.learning_path_display.setText.called
    
    @patch('app.gui.dashboard_handlers.get_desktop_adapter')
    def test_generate_learning_path_success(self, mock_adapter, handler):
        """Test successful learning path generation."""
        handler.interest_input.text.return_value = "Python programming"
        handler.skill_level.currentText.return_value = "Beginner"
        
        mock_adapter.return_value.execute.return_value = {
            "status": "success",
            "result": {"path": "1. Learn basics\n2. Build projects"}
        }
        
        handler.generate_learning_path()
        assert handler.learning_path_display.setText.called
    
    @patch('app.gui.dashboard_handlers.get_desktop_adapter')
    def test_fallback_on_adapter_failure(self, mock_adapter, handler):
        """Test fallback to direct call when governance fails."""
        mock_adapter.side_effect = Exception("Adapter unavailable")
        handler.learning_manager = Mock()
        handler.learning_manager.generate_path.return_value = "Fallback path"
        
        handler.interest_input.text.return_value = "Python"
        handler.skill_level.currentText.return_value = "Beginner"
        
        handler.generate_learning_path()
        assert handler.learning_manager.generate_path.called
```

### Integration Tests
```python
def test_end_to_end_learning_path_generation(qtbot):
    """Test complete flow from button click to display."""
    dashboard = Dashboard()
    qtbot.addWidget(dashboard)
    
    # Simulate user input
    dashboard.interest_input.setText("Machine Learning")
    dashboard.skill_level.setCurrentText("Intermediate")
    
    # Click generate button
    qtbot.mouseClick(dashboard.generate_button, Qt.MouseButton.LeftButton)
    
    # Wait for async operation (if any)
    qtbot.wait(1000)
    
    # Verify output
    assert dashboard.learning_path_display.toPlainText() != ""
```

---

## 13. FUTURE ENHANCEMENTS

### Async Handler Execution
```python
from PyQt6.QtCore import QThread, pyqtSignal

class AsyncHandlerWorker(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, handler_func, *args, **kwargs):
        super().__init__()
        self.handler_func = handler_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        result = self.handler_func(*self.args, **self.kwargs)
        self.finished.emit(result)

# In handler:
def generate_learning_path_async(self):
    worker = AsyncHandlerWorker(self._do_learning_path_generation)
    worker.finished.connect(self._on_learning_path_complete)
    worker.start()
```

### Progress Indicators
```python
def load_data_file(self):
    progress = QProgressDialog("Loading data...", "Cancel", 0, 100, self)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.show()
    
    # ... execute operation ...
    
    progress.setValue(100)
```

---

## SUMMARY

**DashboardHandlers** [[src/app/gui/dashboard_handlers.py]] provides governance-routed event handlers for 6+ dashboard features:
1. **Learning Path Generation** (OpenAI-powered)
2. **Data File Loading** (CSV/XLSX/JSON)
3. **Data Analysis** (Clustering, stats)
4. **Security Resources** (GitHub API)
5. **Location Tracking** (Toggle + history)
6. **Emergency Alerts** (Email notifications)

**Key Design Patterns:**
1. **Governance-First**: Always try adapter.execute() before direct calls
2. **Fallback Strategy**: Direct core system calls if governance unavailable
3. **Input Validation**: Sanitize + validate all user input
4. **Error Feedback**: Always show QMessageBox for errors
5. **Logging**: Comprehensive logging at all levels

**Relationships:**
- **Parent:** Dashboard/Dashboard_main (provides UI components)
- **Governance:** DesktopAdapter → Router → CognitionKernel
- **Core Systems:** 6+ managers (Learning, Data, Security, Location, Emergency, etc.)
- **Security:** data_validation module (sanitize_input, validate_length, validate_email [[src/app/security/data_validation.py]])

**Total Handlers:** 10+ methods covering all dashboard tabs
**Error Handling Layers:** 4 (Validation → Governance → Fallback → Feedback)
**Governance Routes:** 6+ mapped routes to core systems


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/gui/dashboard_handlers.md|Dashboard Handlers]]
- [[relationships/gui/01_DASHBOARD_RELATIONSHIPS.md|01 Dashboard Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/dashboard_handlers.py]] - Implementation file
- [[src/app/interfaces/desktop/integration.py]] - Implementation file


---

## RELATED SYSTEMS

### Core AI System Integration ([[../core-ai/00-INDEX|Core AI Index]])

| Handler Method | Core AI System | Purpose | Documentation |
|----------------|----------------|---------|---------------|
| _on_generate_learning_path | [[../core-ai/04-LearningRequestManager-Relationship-Map\|LearningRequestManager]] | Creates approved learning requests | Section 3 (handler operations) |
| _on_load_data_file | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Stores file metadata in knowledge base | Section 4 (data loading) |
| _on_analyze_data | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Uses AI insights for clustering | Section 5 (analysis) |
| _on_send_alert | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Validates alert doesn't endanger humans | Section 6 (emergency) |
| All handlers | [[../core-ai/06-CommandOverride-Relationship-Map\|CommandOverride]] | Checks if safety protocols active | Governance fallback |

### Agent System Integration ([[../agents/README|Agents Overview]])

| Handler Pattern | Agent System | Flow | Reference |
|-----------------|--------------|------|-----------|
| **Governance Routing** | [[../agents/AGENT_ORCHESTRATION#centralized-kernel-architecture\|CognitionKernel]] | Desktop Adapter → Router → Kernel | Section 3 (pattern) |
| **Input Validation** | [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation\|ValidatorAgent]] | sanitize_input() before processing | Section 2 (validation) |
| **Action Approval** | [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws Layer]] | validate_action() for all mutations | Section 3 (governance) |
| **Task Planning** | [[../agents/PLANNING_HIERARCHIES\|PlannerAgent]] | Multi-step workflow decomposition (future) | Planned integration |

### Governance Pipeline Pattern

```
Handler Event → DashboardErrorHandler.validate_input() → 
Desktop Adapter.execute(route, params) → 
Router.route_to_system() → 
[[../agents/AGENT_ORCHESTRATION#governance-integration|CognitionKernel.process()]] → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|Four Laws Check]] → 
[[../core-ai/02-AIPersona-Relationship-Map|Core System Execution]] → 
Result → Handler → UI Update
```

### Fallback Pattern

If governance unavailable:
```
Handler → Try Desktop Adapter → Exception → 
Fallback to Direct Core System Call → 
Log Warning → Continue Execution
```

See [[../agents/AGENT_ORCHESTRATION#governance-decision-flow|Governance Decision Flow]] for failure handling.

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with Core AI and Agent systems