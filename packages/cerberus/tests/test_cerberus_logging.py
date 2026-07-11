"""Tests for cerberus.logging_config.

Honest scope: verifies formatter output shape and configure_logging
idempotence against the root logger (state is saved and restored around
each test). Log rotation/file handling is out of scope (stream-only).
"""

import json
import logging
from collections.abc import Iterator

import pytest
from cerberus.config import CerberusSettings
from cerberus.logging_config import (
    JsonFormatter,
    PlainFormatter,
    configure_logging,
    get_logger,
)


@pytest.fixture
def restore_root_logger() -> Iterator[None]:
    root = logging.getLogger()
    saved_handlers = list(root.handlers)
    saved_level = root.level
    try:
        yield
    finally:
        root.handlers.clear()
        root.handlers.extend(saved_handlers)
        root.setLevel(saved_level)


def _make_record(msg: str = "hello") -> logging.LogRecord:
    return logging.LogRecord(
        name="cerberus.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


class TestJsonFormatter:
    def test_format_produces_json_with_utc_timestamp(self) -> None:
        payload = json.loads(JsonFormatter().format(_make_record()))
        assert payload["message"] == "hello"
        assert payload["level"] == "INFO"
        assert payload["logger"] == "cerberus.test"
        assert payload["timestamp"].endswith("+00:00")

    def test_extra_fields_merged(self) -> None:
        record = _make_record()
        record.extra_fields = {"guardian_id": "g-1", "spawned": 3}
        payload = json.loads(JsonFormatter().format(record))
        assert payload["guardian_id"] == "g-1"
        assert payload["spawned"] == 3

    def test_exception_info_included(self) -> None:
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            import sys

            record = _make_record("failed")
            record.exc_info = sys.exc_info()
        payload = json.loads(JsonFormatter().format(record))
        assert "RuntimeError: boom" in payload["exception"]


class TestConfigureLogging:
    @pytest.mark.usefixtures("restore_root_logger")
    def test_configure_json_mode(self) -> None:
        configure_logging(CerberusSettings(log_json=True, log_level="WARNING"))
        root = logging.getLogger()
        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)

    @pytest.mark.usefixtures("restore_root_logger")
    def test_configure_plain_mode(self) -> None:
        configure_logging(CerberusSettings(log_json=False))
        root = logging.getLogger()
        assert isinstance(root.handlers[0].formatter, PlainFormatter)

    @pytest.mark.usefixtures("restore_root_logger")
    def test_configure_is_idempotent(self) -> None:
        settings = CerberusSettings()
        configure_logging(settings)
        configure_logging(settings)
        assert len(logging.getLogger().handlers) == 1


class TestGetLogger:
    def test_returns_named_logger(self) -> None:
        assert get_logger("cerberus.x").name == "cerberus.x"
