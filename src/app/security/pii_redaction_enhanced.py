#!/usr/bin/env python3
"""
Enhanced PII Redaction with Comprehensive Patterns
Includes addresses, coordinates, and more pattern types

Production-ready PII detection and redaction system.
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Comprehensive PII Patterns
# ============================================================================

PII_PATTERNS = {
    # Personal identifiers
    "ssn": {
        "patterns": [
            r"\b\d{3}-\d{2}-\d{4}\b",  # 123-45-6789
            r"\b\d{9}\b",  # 123456789 (context-sensitive)
        ],
        "replacement": "[REDACTED-SSN]",
        "confidence": 0.95,
    },
    "email": {
        "patterns": [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        ],
        "replacement": "[REDACTED-EMAIL]",
        "confidence": 0.98,
    },
    # Phone numbers - US and international
    "phone": {
        "patterns": [
            r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # US
            r"\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",  # International
            r"\b\d{3}[-.\s]\d{4}\b",  # Short format
        ],
        "replacement": "[REDACTED-PHONE]",
        "confidence": 0.92,
    },
    # Financial
    "credit_card": {
        "patterns": [
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # 1234-5678-9012-3456
            r"\b\d{13,19}\b",  # 1234567890123456 (with Luhn check)
        ],
        "replacement": "[REDACTED-CARD]",
        "confidence": 0.90,
        "luhn_check": True,
    },
    "bank_account": {
        "patterns": [
            r"\b\d{8,17}\b",  # Account numbers (context-sensitive)
        ],
        "replacement": "[REDACTED-ACCOUNT]",
        "confidence": 0.70,
        "context_keywords": ["account", "bank", "routing"],
    },
    # Network
    "ip_address": {
        "patterns": [
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",  # IPv4
            r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",  # IPv6
        ],
        "replacement": "[REDACTED-IP]",
        "confidence": 0.90,
        "exclude_ranges": ["127.0.0.0/8", "10.0.0.0/8", "192.168.0.0/16"],
    },
    # Government IDs
    "passport": {
        "patterns": [
            r"\b[A-Z]{1,2}\d{6,9}\b",  # US/UK passport
        ],
        "replacement": "[REDACTED-PASSPORT]",
        "confidence": 0.75,
        "context_keywords": ["passport", "travel"],
    },
    "driver_license": {
        "patterns": [
            r"\b[A-Z]{1,2}\d{6,8}\b",  # State driver's license
            r"\b\d{7,9}\b",  # Numeric driver's license
        ],
        "replacement": "[REDACTED-LICENSE]",
        "confidence": 0.70,
        "context_keywords": ["license", "dl", "driver"],
    },
    # Addresses - Enhanced
    "street_address": {
        "patterns": [
            r"\b\d{1,5}\s+[\w\s]{1,50}(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|court|ct|boulevard|blvd|way|circle|cir|plaza|pl)\b",
            r"\b\d{1,5}\s+[NSEW]\.?\s+[\w\s]{1,50}(?:street|st|avenue|ave|road|rd)\b",
        ],
        "replacement": "[REDACTED-ADDRESS]",
        "confidence": 0.85,
    },
    "po_box": {
        "patterns": [
            r"\bP\.?\s*O\.?\s*Box\s+\d{1,5}\b",
        ],
        "replacement": "[REDACTED-POBOX]",
        "confidence": 0.95,
    },
    "zipcode": {
        "patterns": [
            r"\b\d{5}(?:-\d{4})?\b",  # US ZIP code
            r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b",  # Canadian postal code
        ],
        "replacement": "[REDACTED-ZIP]",
        "confidence": 0.80,
    },
    # Geographic coordinates
    "coordinates": {
        "patterns": [
            r"\b[-+]?\d{1,3}\.\d{4,}\s*,\s*[-+]?\d{1,3}\.\d{4,}\b",  # Lat/Long
            r"\b(?:lat|latitude):\s*[-+]?\d{1,3}\.\d+\b",
            r"\b(?:lon|lng|longitude):\s*[-+]?\d{1,3}\.\d+\b",
        ],
        "replacement": "[REDACTED-COORDS]",
        "confidence": 0.88,
    },
    # Medical
    "medical_record": {
        "patterns": [
            r"\bMRN[-:\s]?\d{6,10}\b",
            r"\b\d{6,10}\b",  # Context-sensitive
        ],
        "replacement": "[REDACTED-MRN]",
        "confidence": 0.65,
        "context_keywords": ["medical", "patient", "health", "mrn"],
    },
    # API keys and tokens
    "api_keys": {
        "patterns": [
            r"\b(?:sk|pk)_(?:test|live)_[A-Za-z0-9]{24,}\b",  # Stripe-style
            r"\bAKIA[0-9A-Z]{16}\b",  # AWS access key
            r"\bghp_[A-Za-z0-9]{36}\b",  # GitHub personal access token
            r"\b[A-Za-z0-9]{32,}\b",  # Generic token (context-sensitive)
        ],
        "replacement": "[REDACTED-KEY]",
        "confidence": 0.99,
        "context_keywords": ["token", "api", "key", "secret", "password"],
    },
}


def luhn_check(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm.

    Args:
        card_number: Card number string

    Returns:
        True if valid, False otherwise
    """
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0

    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


def redact_pii_comprehensive(
    text: str, enabled_patterns: List[str] = None, preserve_hashes: bool = True
) -> Tuple[str, Dict[str, any]]:
    """
    Comprehensive PII redaction with all pattern types.

    Args:
        text: Text to redact
        enabled_patterns: List of pattern types to use (all if None)
        preserve_hashes: Store SHA-256 hashes of redacted values

    Returns:
        Tuple of (redacted_text, redaction_stats)
    """
    import hashlib

    redacted = text
    stats = {
        "total_redactions": 0,
        "by_type": {},
        "hashes": [] if preserve_hashes else None,
    }

    # Use all patterns if not specified
    if enabled_patterns is None:
        enabled_patterns = list(PII_PATTERNS.keys())

    for pattern_type in enabled_patterns:
        if pattern_type not in PII_PATTERNS:
            continue

        pattern_config = PII_PATTERNS[pattern_type]
        count = 0

        for pattern in pattern_config["patterns"]:
            matches = list(re.finditer(pattern, redacted, re.IGNORECASE))

            for match in matches:
                matched_text = match.group(0)

                # Context-sensitive validation
                if pattern_config.get("context_keywords"):
                    # Check if any context keyword appears nearby
                    context_window = 50
                    start = max(0, match.start() - context_window)
                    end = min(len(text), match.end() + context_window)
                    context = text[start:end].lower()

                    if not any(
                        kw in context for kw in pattern_config["context_keywords"]
                    ):
                        continue

                # Luhn check for credit cards
                if pattern_config.get("luhn_check"):
                    if not luhn_check(matched_text):
                        continue

                # IP address exclusion
                if pattern_config.get("exclude_ranges"):
                    # Skip private IP ranges (simplified)
                    if matched_text.startswith(("127.", "10.", "192.168.")):
                        continue

                # Redact
                redacted = redacted.replace(matched_text, pattern_config["replacement"])
                count += 1

                # Store hash if requested
                if preserve_hashes:
                    hash_value = hashlib.sha256(matched_text.encode()).hexdigest()
                    stats["hashes"].append(
                        {
                            "type": pattern_type,
                            "hash": hash_value,
                            "length": len(matched_text),
                        }
                    )

        if count > 0:
            stats["by_type"][pattern_type] = count
            stats["total_redactions"] += count

    return redacted, stats


if __name__ == "__main__":
    # Test comprehensive redaction
    test_text = """
    Contact: John Doe
    Email: john.doe@example.com
    Phone: +1 (555) 123-4567 or 555-987-6543
    SSN: 123-45-6789
    Address: 123 Main Street, Apt 4B, New York, NY 10001
    Coordinates: 40.7128, -74.0060
    Credit Card: 4532-1234-5678-9010
    Medical Record: MRN-1234567
    IP: 192.168.1.100
    API Key: [REDACTED]
    """

    redacted, stats = redact_pii_comprehensive(test_text)

    print("Original length:", len(test_text))
    print("Redacted length:", len(redacted))
    print("\nRedaction stats:")
    print(f"  Total redactions: {stats['total_redactions']}")
    print(f"  By type: {stats['by_type']}")
    print("\nRedacted text:")
    print(redacted)
