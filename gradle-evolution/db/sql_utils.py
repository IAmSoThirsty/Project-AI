"""
SQL identifier sanitization utilities.

This module provides utilities for safely handling SQL identifiers (table names,
column names) which cannot be parameterized using standard SQL placeholders.
"""

import re
from typing import List


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize a SQL identifier (table or column name).
    
    Validates that the identifier contains only safe characters to prevent
    SQL injection when identifiers must be used in f-strings (since they
    cannot be parameterized with ? placeholders in SQLite).
    
    Args:
        identifier: Table or column name to sanitize
        
    Returns:
        The validated identifier
        
    Raises:
        ValueError: If identifier contains unsafe characters
    """
    # Allow alphanumeric, underscore, and dollar sign (valid SQL identifiers)
    # Disallow spaces, quotes, semicolons, and other SQL syntax characters
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(
            f"Invalid SQL identifier: {identifier}. "
            "Identifiers must start with a letter or underscore and contain "
            "only alphanumeric characters and underscores."
        )
    
    return identifier


def quote_identifier(identifier: str) -> str:
    """
    Quote a SQL identifier for safe use in queries.
    
    Uses double quotes per SQL standard. This should be used after sanitization.
    
    Args:
        identifier: Table or column name to quote
        
    Returns:
        Quoted identifier
    """
    # First sanitize, then quote
    safe_id = sanitize_identifier(identifier)
    return f'"{safe_id}"'


def sanitize_identifier_list(identifiers: List[str]) -> List[str]:
    """
    Sanitize a list of SQL identifiers.
    
    Args:
        identifiers: List of table or column names
        
    Returns:
        List of validated identifiers
        
    Raises:
        ValueError: If any identifier contains unsafe characters
    """
    return [sanitize_identifier(id) for id in identifiers]


def build_set_clause(columns: List[str]) -> str:
    """
    Build a safe SET clause for UPDATE statements.
    
    Args:
        columns: Column names to include in SET clause
        
    Returns:
        SET clause string with sanitized column names
        
    Raises:
        ValueError: If any column name is invalid
    """
    sanitized = sanitize_identifier_list(columns)
    return ", ".join(f"{col} = ?" for col in sanitized)
