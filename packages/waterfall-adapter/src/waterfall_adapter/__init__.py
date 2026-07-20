"""Governed, narrow integration boundary for Thirstys Waterfall."""

from .adapter import (
    ALLOWED_OPERATIONS,
    AdapterResult,
    UnsupportedOperation,
    WaterfallAdapter,
    WaterfallTransport,
)

__all__ = [
    "ALLOWED_OPERATIONS",
    "AdapterResult",
    "UnsupportedOperation",
    "WaterfallAdapter",
    "WaterfallTransport",
]

__version__ = "0.0.3"
