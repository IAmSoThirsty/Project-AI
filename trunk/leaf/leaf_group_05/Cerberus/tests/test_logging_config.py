# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_logging_config.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_logging_config.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Tests for logging configuration."""

import json
import logging
import sys
from io import StringIO

import pytest

from cerberus.config import CerberusSettings
from cerberus.logging_config import (
    JsonFormatter,
    PlainFormatter,
    configure_logging,
    get_logger,
)


class TestJsonFormatter:
    """Tests for JsonFormatter."""

    def test_json_formatter_basic(self) -> None:
        """Test basic JSON formatting."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_function",
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["logger"] == "test.logger"
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["module"] == "test"
        assert data["function"] == "test_function"
        assert data["line"] == 10
        assert "timestamp" in data

    def test_json_formatter_with_exception(self) -> None:
        """Test JSON formatting with exception information."""
        formatter = JsonFormatter()
        
        # Create an exception
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=20,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["message"] == "Error occurred"
        assert "exception" in data
        assert "ValueError" in data["exception"]
        assert "Test error" in data["exception"]

    def test_json_formatter_with_extra_fields(self) -> None:
        """Test JSON formatting with extra fields."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=30,
            msg="Test with extras",
            args=(),
            exc_info=None,
        )
        
        # Add extra fields
        record.extra_fields = {"user_id": "123", "request_id": "abc"}
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["message"] == "Test with extras"
        assert data["user_id"] == "123"
        assert data["request_id"] == "abc"


class TestPlainFormatter:
    """Tests for PlainFormatter."""

    def test_plain_formatter_initialization(self) -> None:
        """Test PlainFormatter initialization."""
        formatter = PlainFormatter()
        assert formatter is not None
        assert isinstance(formatter, logging.Formatter)

    def test_plain_formatter_output(self) -> None:
        """Test PlainFormatter output format."""
        formatter = PlainFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=40,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        
        # Should contain basic logging info
        assert "INFO" in output
        assert "test.logger" in output
        assert "Test message" in output


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_json_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test logging configuration with JSON mode."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Reconfigure settings for this test
        import cerberus.logging_config as logging_module
        monkeypatch.setattr(logging_module, "settings", CerberusSettings(log_json=True, log_level="INFO"))
        
        configure_logging()
        
        # Check that handler is configured
        assert len(root_logger.handlers) > 0
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert isinstance(handler.formatter, JsonFormatter)

    def test_configure_logging_plain_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test logging configuration with plain text mode."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Reconfigure settings for this test
        import cerberus.logging_config as logging_module
        monkeypatch.setattr(logging_module, "settings", CerberusSettings(log_json=False, log_level="DEBUG"))
        
        configure_logging()
        
        # Check that handler is configured
        assert len(root_logger.handlers) > 0
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert isinstance(handler.formatter, PlainFormatter)

    def test_configure_logging_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that log level is properly configured."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Reconfigure settings for this test
        import cerberus.logging_config as logging_module
        monkeypatch.setattr(logging_module, "settings", CerberusSettings(log_level="WARNING"))
        
        configure_logging()
        
        # Check log level
        assert root_logger.level == logging.WARNING


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test.module")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_different_names(self) -> None:
        """Test that get_logger returns different loggers for different names."""
        logger1 = get_logger("module.a")
        logger2 = get_logger("module.b")
        
        assert logger1 != logger2
        assert logger1.name == "module.a"
        assert logger2.name == "module.b"

    def test_get_logger_same_name_returns_same_logger(self) -> None:
        """Test that get_logger returns the same logger for the same name."""
        logger1 = get_logger("same.module")
        logger2 = get_logger("same.module")
        
        assert logger1 is logger2
