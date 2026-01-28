"""
Project AI Utilities Module.

Provides helper functions, logging, and validation utilities.
"""
from .helpers import (
    hash_data,
    get_timestamp,
    format_timestamp,
    truncate_hash,
    safe_get
)
from .logger import setup_logger, default_logger
from .validators import (
    validate_actor,
    validate_action,
    validate_target,
    validate_verdict,
    validate_intent,
    sanitize_string,
    ValidationError
)

__all__ = [
    # Helpers
    'hash_data',
    'get_timestamp',
    'format_timestamp',
    'truncate_hash',
    'safe_get',
    
    # Logger
    'setup_logger',
    'default_logger',
    
    # Validators
    'validate_actor',
    'validate_action',
    'validate_target',
    'validate_verdict',
    'validate_intent',
    'sanitize_string',
    'ValidationError',
]

__version__ = '1.0.0'
