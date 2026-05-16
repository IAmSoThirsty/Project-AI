"""Collaborative workflow GUI panel for Project-AI Leather Book interface."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.agents.collaborative_workflow import CollaborativeWorkflow
    from app.core.cognition_kernel import CognitionKernel

logger = logging.getLogger(__name__)


class WorkflowWorker(QThread):
    """Background thread for running collaborative workflows."""
    
    workflow_complete = pyqtSignal(dict)  # Emits result dictionary
    workflow_error = pyqtSignal(str)  # Emits error message
    
    def __init__(
        self,
        workflow: CollaborativeWorkflow,
        user_request: str,
    ) -> None:
        super().__init__()
        self.workflow = workflow
        self.user_request = user_request
    
    def run(self) -> None:
        """Execute workflow in background thread."""
        try:
            result = self.workflow.execute(self.user_request)
            self.workflow_complete.emit(result)
        except Exception as exc:
            logger.error(f"Workflow execution failed: {exc}")
            self.workflow_error.emit(str(exc))


class CollaborativeWorkflowPanel(QWidget):
    """Panel for running multi-agent collaborative workflows."""
    
    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize collaborative workflow panel.
        
        Args:
            kernel: CognitionKernel instance for routing operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.kernel = kernel
        self.workflow = None
        self.worker = None
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("🤝 Collaborative Workflow")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Multi-agent collaboration: Writer creates content, "
            "Reviewer provides feedback, refinement through iteration."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Request input
        request_label = QLabel("Your Request:")
        layout.addWidget(request_label)
        
        self.request_input = QTextEdit()
        self.request_input.setPlaceholderText(
            "Enter your content request...\n\n"
            "Examples:\n"
            "  • Explain quantum computing to a 10-year-old\n"
            "  • Write a security policy for handling user data\n"
            "  • Analyze the benefits of multi-agent collaboration"
        )
        self.request_input.setMaximumHeight(120)
        layout.addWidget(self.request_input)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.run_button = QPushButton("▶ Run Workflow")
        self.run_button.clicked.connect(self._on_run_workflow)
        controls_layout.addWidget(self.run_button)
        
        self.clear_button = QPushButton("🗑 Clear")
        self.clear_button.clicked.connect(self._on_clear)
        controls_layout.addWidget(self.clear_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #00ff00; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Output display
        output_label = QLabel("Workflow Output:")
        layout.addWidget(output_label)
        
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText("Output will appear here...")
        layout.addWidget(self.output_display)
        
        self.setLayout(layout)
    
    def _on_run_workflow(self) -> None:
        """Handle run workflow button click."""
        user_request = self.request_input.toPlainText().strip()
        
        if not user_request:
            self.status_label.setText("⚠️ Please enter a request")
            self.status_label.setStyleSheet("color: #ff6600;")
            return
        
        # Initialize workflow if needed
        if self.workflow is None:
            try:
                from app.agents.collaborative_workflow import CollaborativeWorkflow
                self.workflow = CollaborativeWorkflow(
                    kernel=self.kernel,
                    max_iterations=2,
                )
            except Exception as exc:
                self.status_label.setText(f"⚠️ Failed to initialize: {exc}")
                self.status_label.setStyleSheet("color: #ff0000;")
                logger.error(f"Workflow initialization failed: {exc}")
                return
        
        # Disable controls during execution
        self.run_button.setEnabled(False)
        self.request_input.setEnabled(False)
        self.status_label.setText("⏳ Running workflow...")
        self.status_label.setStyleSheet("color: #00ffff;")
        self.output_display.clear()
        
        # Start background worker
        self.worker = WorkflowWorker(self.workflow, user_request)
        self.worker.workflow_complete.connect(self._on_workflow_complete)
        self.worker.workflow_error.connect(self._on_workflow_error)
        self.worker.start()
    
    def _on_workflow_complete(self, result: dict) -> None:
        """Handle workflow completion.
        
        Args:
            result: Workflow result dictionary
        """
        # Format output
        output_lines = [
            "="  * 60,
            f"✅ Workflow Complete ({result['iterations']} iteration(s))",
            "=" * 60,
            "",
            "📝 FINAL CONTENT:",
            "",
            result["final_content"],
            "",
            "=" * 60,
            f"Iterations: {result['iterations']}",
            f"Max iterations reached: {result.get('max_iterations_reached', False)}",
            "=" * 60,
        ]
        
        self.output_display.setPlainText("\n".join(output_lines))
        
        # Update status
        self.status_label.setText(
            f"✅ Complete in {result['iterations']} iteration(s)"
        )
        self.status_label.setStyleSheet("color: #00ff00;")
        
        # Re-enable controls
        self.run_button.setEnabled(True)
        self.request_input.setEnabled(True)
        
        logger.info(f"Workflow completed: {result['iterations']} iterations")
    
    def _on_workflow_error(self, error_msg: str) -> None:
        """Handle workflow error.
        
        Args:
            error_msg: Error message
        """
        self.output_display.setPlainText(
            f"❌ Workflow Error:\n\n{error_msg}"
        )
        
        self.status_label.setText("❌ Workflow failed")
        self.status_label.setStyleSheet("color: #ff0000;")
        
        # Re-enable controls
        self.run_button.setEnabled(True)
        self.request_input.setEnabled(True)
    
    def _on_clear(self) -> None:
        """Clear all inputs and outputs."""
        self.request_input.clear()
        self.output_display.clear()
        self.status_label.clear()
