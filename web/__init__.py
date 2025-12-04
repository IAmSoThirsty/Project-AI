"""Project-AI Web package root.

Exposes the Flask app for convenience so tests can import `web.backend.app` or `web.app`.
"""
from .backend import app as app  # re-export for test convenience
