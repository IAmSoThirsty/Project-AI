"""
Settings and Support - Q/A, Contact, and Feedback system
"""

from .contact_system import ContactSystem
from .feedback_manager import FeedbackManager
from .qa_system import QASystem
from .settings_manager import SettingsManager

__all__ = ['SettingsManager', 'QASystem', 'ContactSystem', 'FeedbackManager']
