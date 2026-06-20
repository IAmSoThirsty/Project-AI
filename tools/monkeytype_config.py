"""Optional MonkeyType configuration for tracing Project-AI package code."""

from __future__ import annotations

from collections.abc import Callable
from types import CodeType

from monkeytype.config import DefaultConfig


def project_code(code: CodeType) -> bool:
    return "Project-AI-Beginnings" in code.co_filename


class ProjectConfig(DefaultConfig):
    def code_filter(self) -> Callable[[CodeType], bool]:
        return project_code


CONFIG = ProjectConfig()
