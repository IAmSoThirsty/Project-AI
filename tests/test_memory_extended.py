#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Extended test suite for MemoryExpansionSystem with 20+ tests.

Covers:
- Knowledge add/get for categories and keys
- Conversation logging IDs and timestamps
- Statistics reporting
- Persistence and corrupted file handling
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

import pytest

from app.core.ai_systems import MemoryExpansionSystem