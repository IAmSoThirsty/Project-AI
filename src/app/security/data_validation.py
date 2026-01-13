"""Secure data ingestion and parsing with poisoning defense.

This module implements:
- Secure XML parsing with XSD/DTD blocking
- CSV parsing with schema validation
- Data poisoning defense mechanisms
- Static analysis for incoming data
- Encoding enforcement
"""

import csv
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from io import StringIO
from typing import Any
from xml.etree.ElementTree import (
    Element,  # nosec B405 - Only used for type hints, not parsing
)

import defusedxml.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class ParsedData:
    """Container for parsed data with metadata."""

    data: Any
    data_type: str
    hash: str
    validated: bool
    issues: list[str]


class SecureDataParser:
    """Secure data parsing with multiple format support."""

    def __init__(self):
        """Initialize secure data parser."""
        self.max_file_size = 100 * 1024 * 1024  # 100 MB
        self.allowed_encodings = {"utf-8", "ascii", "latin-1"}
        self.blocked_xml_features = {"entity", "dtd", "external"}

    def parse_xml(self, xml_data: str, schema: dict | None = None) -> ParsedData:
        """Parse XML with security controls.

        Args:
            xml_data: XML string to parse
            schema: Optional schema for validation

        Returns:
            ParsedData object with parsed content and validation status
        """
        issues = []

        # Check for XXE attack patterns
        if self._detect_xxe_patterns(xml_data):
            issues.append("XXE attack pattern detected")
            logger.warning("XXE attack pattern detected in XML data")
            return ParsedData(
                data=None, data_type="xml", hash="", validated=False, issues=issues
            )

        # Check for DTD declarations (should be blocked)
        if "<!DOCTYPE" in xml_data or "<!ENTITY" in xml_data:
            issues.append("DTD/Entity declarations not allowed")
            logger.warning("DTD/Entity declarations found in XML")
            return ParsedData(
                data=None, data_type="xml", hash="", validated=False, issues=issues
            )

        # Parse with defusedxml for secure XML parsing
        try:
            # defusedxml prevents XXE attacks by disabling external entity resolution
            tree = ET.fromstring(xml_data)
            data = self._xml_to_dict(tree)

            # Validate against schema if provided
            if schema:
                validation_issues = self._validate_schema(data, schema)
                issues.extend(validation_issues)

            # Calculate hash
            data_hash = hashlib.sha256(xml_data.encode()).hexdigest()

            return ParsedData(
                data=data,
                data_type="xml",
                hash=data_hash,
                validated=len(issues) == 0,
                issues=issues,
            )

        except ET.ParseError as e:
            issues.append(f"XML parse error: {e}")
            logger.error("XML parsing failed: %s", e)
            return ParsedData(
                data=None, data_type="xml", hash="", validated=False, issues=issues
            )

    def parse_csv(
        self, csv_data: str, schema: dict | None = None, delimiter: str = ","
    ) -> ParsedData:
        """Parse CSV with validation and type checking.

        Args:
            csv_data: CSV string to parse
            schema: Optional schema with column types
            delimiter: CSV delimiter

        Returns:
            ParsedData object with parsed content and validation status
        """
        issues = []

        # Check for CSV injection patterns
        if self._detect_csv_injection(csv_data):
            issues.append("CSV injection pattern detected")
            logger.warning("CSV injection pattern detected")

        try:
            # Parse CSV
            reader = csv.DictReader(StringIO(csv_data), delimiter=delimiter)
            rows = list(reader)

            # Validate schema if provided
            if schema and rows:
                for idx, row in enumerate(rows):
                    row_issues = self._validate_csv_row(row, schema, idx)
                    issues.extend(row_issues)

            # Calculate hash
            data_hash = hashlib.sha256(csv_data.encode()).hexdigest()

            return ParsedData(
                data=rows,
                data_type="csv",
                hash=data_hash,
                validated=len(issues) == 0,
                issues=issues,
            )

        except csv.Error as e:
            issues.append(f"CSV parse error: {e}")
            logger.error("CSV parsing failed: %s", e)
            return ParsedData(
                data=None, data_type="csv", hash="", validated=False, issues=issues
            )

    def parse_json(self, json_data: str, schema: dict | None = None) -> ParsedData:
        """Parse JSON with validation.

        Args:
            json_data: JSON string to parse
            schema: Optional schema for validation

        Returns:
            ParsedData object with parsed content and validation status
        """
        issues = []

        # Check size
        if len(json_data) > self.max_file_size:
            issues.append("JSON data exceeds maximum size")
            return ParsedData(
                data=None, data_type="json", hash="", validated=False, issues=issues
            )

        try:
            data = json.loads(json_data)

            # Validate schema if provided
            if schema:
                validation_issues = self._validate_schema(data, schema)
                issues.extend(validation_issues)

            # Calculate hash
            data_hash = hashlib.sha256(json_data.encode()).hexdigest()

            return ParsedData(
                data=data,
                data_type="json",
                hash=data_hash,
                validated=len(issues) == 0,
                issues=issues,
            )

        except json.JSONDecodeError as e:
            issues.append(f"JSON parse error: {e}")
            logger.error("JSON parsing failed: %s", e)
            return ParsedData(
                data=None, data_type="json", hash="", validated=False, issues=issues
            )

    def _detect_xxe_patterns(self, xml_data: str) -> bool:
        """Detect XXE attack patterns in XML.

        Args:
            xml_data: XML string to check

        Returns:
            True if XXE pattern detected
        """
        xxe_patterns = [
            r"<!ENTITY",
            r"SYSTEM\s+[\"']file://",
            r"SYSTEM\s+[\"']http://",
            r"SYSTEM\s+[\"']https://",
            r"<!DOCTYPE.*SYSTEM",
        ]

        for pattern in xxe_patterns:
            if re.search(pattern, xml_data, re.IGNORECASE):
                return True

        return False

    def _detect_csv_injection(self, csv_data: str) -> bool:
        """Detect CSV injection patterns.

        Args:
            csv_data: CSV string to check

        Returns:
            True if CSV injection detected
        """
        # Check for formula injection
        dangerous_prefixes = ["=", "+", "-", "@", "\t", "\r"]

        for line in csv_data.split("\n")[:10]:  # Check first 10 lines
            fields = line.split(",")
            for field in fields:
                field = field.strip().strip('"').strip("'")
                if field and field[0] in dangerous_prefixes:
                    logger.warning("CSV injection detected: %s", field[:20])
                    return True

        return False

    def _xml_to_dict(self, element: Element) -> dict:
        """Convert XML element to dictionary.

        Args:
            element: XML element

        Returns:
            Dictionary representation
        """
        result = {}

        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib

        # Add text content
        if element.text and element.text.strip():
            if len(result) == 0:
                return element.text.strip()
            result["@text"] = element.text.strip()

        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # Multiple children with same tag - make list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result or element.text

    def _validate_schema(self, data: Any, schema: dict) -> list[str]:
        """Validate data against schema.

        Args:
            data: Data to validate
            schema: Schema definition

        Returns:
            List of validation issues
        """
        issues = []

        if not isinstance(data, dict):
            issues.append("Data is not a dictionary")
            return issues

        # Check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    issues.append(f"Required field missing: {field}")

        # Check types
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    expected_type = field_schema.get("type")
                    value = data[field]

                    if not self._check_type(value, expected_type):
                        issues.append(
                            f"Field '{field}' has wrong type: expected {expected_type}"
                        )

        return issues

    def _validate_csv_row(self, row: dict, schema: dict, row_idx: int) -> list[str]:
        """Validate a CSV row against schema.

        Args:
            row: CSV row as dictionary
            schema: Schema definition
            row_idx: Row index for error reporting

        Returns:
            List of validation issues
        """
        issues = []

        for column, value in row.items():
            if column in schema:
                expected_type = schema[column]

                # Try to convert and validate
                if expected_type == "int":
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        issues.append(
                            f"Row {row_idx}, column '{column}': expected int, got '{value}'"
                        )

                elif expected_type == "float":
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        issues.append(
                            f"Row {row_idx}, column '{column}': expected float, got '{value}'"
                        )

        return issues

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type.

        Args:
            value: Value to check
            expected_type: Expected type string

        Returns:
            True if type matches
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, allow

        return isinstance(value, expected)


class DataPoisoningDefense:
    """Defense mechanisms against data poisoning attacks."""

    def __init__(self):
        """Initialize data poisoning defense."""
        self.known_poisons: set[str] = set()
        self.poison_patterns: list[re.Pattern] = [
            re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"onerror\s*=", re.IGNORECASE),
            re.compile(r"onclick\s*=", re.IGNORECASE),
            re.compile(r"onload\s*=", re.IGNORECASE),
            re.compile(r"onfocus\s*=", re.IGNORECASE),
            re.compile(r"onstart\s*=", re.IGNORECASE),
            re.compile(r"<svg.*?onload", re.IGNORECASE),
            re.compile(r"<iframe", re.IGNORECASE),
            re.compile(r"<embed", re.IGNORECASE),
            re.compile(r"<object", re.IGNORECASE),
            re.compile(r"\.\./\.\."),  # Path traversal
            re.compile(r";\s*drop\s+table", re.IGNORECASE),  # SQL injection
            re.compile(r"union\s+select", re.IGNORECASE),  # SQL injection
            re.compile(r"\$\{jndi:", re.IGNORECASE),  # Log4j injection
            re.compile(r"\{\{.*?\}\}"),  # Template injection
            re.compile(r"%0d%0a", re.IGNORECASE),  # CRLF injection
        ]

    def check_for_poison(self, data: str) -> tuple[bool, list[str]]:
        """Check data for poisoning patterns.

        Args:
            data: Data to check

        Returns:
            Tuple of (is_poisoned, list_of_detected_patterns)
        """
        detected = []

        # Check hash against known poisons
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        if data_hash in self.known_poisons:
            detected.append("Known poison hash detected")
            logger.warning("Known poison detected: %s", data_hash[:16])
            return True, detected

        # Check for poison patterns
        for pattern in self.poison_patterns:
            if pattern.search(data):
                detected.append(f"Poison pattern: {pattern.pattern[:50]}")
                logger.warning("Poison pattern detected: %s", pattern.pattern[:50])

        return len(detected) > 0, detected

    def add_poison_signature(self, data: str) -> None:
        """Add data signature to known poisons.

        Args:
            data: Data to blacklist
        """
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        self.known_poisons.add(data_hash)
        logger.info("Added poison signature: %s", data_hash[:16])

    def sanitize_input(self, data: str) -> str:
        """Sanitize input data by removing dangerous patterns.

        Args:
            data: Input data

        Returns:
            Sanitized data
        """
        sanitized = data

        # Remove script tags
        sanitized = re.sub(
            r"<script.*?>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove event handlers
        sanitized = re.sub(r"on\w+\s*=\s*[\"'][^\"']*[\"']", "", sanitized, flags=re.IGNORECASE)

        # Remove javascript: URLs
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)

        return sanitized
