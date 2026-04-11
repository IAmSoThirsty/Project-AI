#!/usr/bin/env python3
"""
Environment Variable Validator
Validates environment configuration before application startup

Usage:
    python env_validator.py                    # Validate current environment
    python env_validator.py --env production   # Validate as if in production
    python env_validator.py --strict          # Fail on warnings
    python env_validator.py --export-schema   # Export validation schema
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class Severity(Enum):
    """Validation message severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationStatus(Enum):
    """Overall validation status"""
    PASSED = "PASSED"
    PASSED_WITH_WARNINGS = "PASSED_WITH_WARNINGS"
    FAILED = "FAILED"


@dataclass
class ValidationResult:
    """Individual validation result"""
    variable: str
    severity: Severity
    message: str
    value_preview: str | None = None


@dataclass
class EnvironmentVariable:
    """Environment variable specification"""
    name: str
    description: str
    required: bool = False
    required_in_production: bool = False
    default: str | None = None
    pattern: str | None = None
    min_length: int | None = None
    validator: Callable[[str], tuple[bool, str | None]] | None = None
    sensitive: bool = False
    example: str | None = None


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_fernet_key(value: str) -> tuple[bool, str | None]:
    """Validate Fernet key format"""
    if not value:
        return False, "Fernet key cannot be empty"
    
    if len(value) != 44:
        return False, f"Fernet key must be 44 characters (got {len(value)})"
    
    # Check if it's base64-like
    if not re.match(r'^[A-Za-z0-9+/=_-]+$', value):
        return False, "Fernet key must be base64-encoded"
    
    return True, None


def validate_secret_key(value: str) -> tuple[bool, str | None]:
    """Validate secret key strength"""
    if not value:
        return False, "Secret key cannot be empty"
    
    if len(value) < 32:
        return False, f"Secret key must be at least 32 characters (got {len(value)})"
    
    if value in ["changeme", "secret", "password", "your-secret-key"]:
        return False, "Secret key must not be a common/default value"
    
    return True, None


def validate_jwt_secret(value: str) -> tuple[bool, str | None]:
    """Validate JWT secret"""
    if not value:
        return False, "JWT secret cannot be empty"
    
    if len(value) < 32:
        return False, f"JWT secret must be at least 32 characters (got {len(value)})"
    
    if value in ["changeme", "changeme-secret-key", "secret"]:
        return False, "JWT secret must not be a default value"
    
    # Check if same as SECRET_KEY
    secret_key = os.getenv("SECRET_KEY", "")
    if value == secret_key and secret_key:
        return False, "JWT_SECRET should differ from SECRET_KEY for security"
    
    return True, None


def validate_api_keys(value: str) -> tuple[bool, str | None]:
    """Validate API keys list"""
    if not value:
        return False, "API keys list cannot be empty"
    
    keys = [k.strip() for k in value.split(",")]
    
    if "changeme" in value.lower():
        return False, "API keys contain default 'changeme' value"
    
    if len(keys) < 1:
        return False, "At least one API key must be specified"
    
    for key in keys:
        if len(key) < 16:
            return False, f"API key '{key[:8]}...' is too short (minimum 16 chars)"
    
    return True, None


def validate_environment(value: str) -> tuple[bool, str | None]:
    """Validate environment name"""
    valid_envs = ["development", "staging", "production"]
    if value not in valid_envs:
        return False, f"Environment must be one of: {', '.join(valid_envs)}"
    return True, None


def validate_port(value: str) -> tuple[bool, str | None]:
    """Validate port number"""
    try:
        port = int(value)
        if port < 1024 or port > 65535:
            return False, "Port must be between 1024 and 65535"
        return True, None
    except ValueError:
        return False, "Port must be a valid integer"


def validate_log_level(value: str) -> tuple[bool, str | None]:
    """Validate log level"""
    valid_levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
    if value.upper() not in valid_levels:
        return False, f"Log level must be one of: {', '.join(valid_levels)}"
    return True, None


def validate_boolean(value: str) -> tuple[bool, str | None]:
    """Validate boolean value"""
    if value.lower() not in ["true", "false", "1", "0", "yes", "no"]:
        return False, "Boolean value must be true/false, yes/no, or 1/0"
    return True, None


def validate_url(value: str) -> tuple[bool, str | None]:
    """Validate URL format"""
    if not value:
        return True, None  # Empty is OK for optional URLs
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, value):
        return False, "Invalid URL format"
    return True, None


def validate_cors_origins(value: str) -> tuple[bool, str | None]:
    """Validate CORS origins"""
    if not value:
        return False, "CORS origins cannot be empty"
    
    # Get environment
    env = os.getenv("ENVIRONMENT", "development")
    
    # Check for wildcard in production
    if env == "production" and "*" in value:
        return False, "CORS origins must not contain '*' in production"
    
    return True, None


# =============================================================================
# ENVIRONMENT VARIABLE DEFINITIONS
# =============================================================================

ENVIRONMENT_VARIABLES = [
    # Critical Security Variables
    EnvironmentVariable(
        name="FERNET_KEY",
        description="Symmetric encryption key for sensitive data",
        required_in_production=True,
        validator=validate_fernet_key,
        sensitive=True,
        example="gAAAAABh... (44 characters)",
    ),
    EnvironmentVariable(
        name="SECRET_KEY",
        description="Master secret for session signing and CSRF",
        required_in_production=True,
        validator=validate_secret_key,
        min_length=32,
        sensitive=True,
        example="Use: python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
    ),
    EnvironmentVariable(
        name="JWT_SECRET",
        description="JSON Web Token signing key",
        required_in_production=True,
        validator=validate_jwt_secret,
        min_length=32,
        sensitive=True,
    ),
    EnvironmentVariable(
        name="API_KEYS",
        description="Comma-separated list of valid API keys",
        required_in_production=True,
        validator=validate_api_keys,
        sensitive=True,
    ),
    
    # Application Configuration
    EnvironmentVariable(
        name="ENVIRONMENT",
        description="Deployment environment",
        required=True,
        default="development",
        validator=validate_environment,
    ),
    EnvironmentVariable(
        name="API_HOST",
        description="API server bind address",
        default="0.0.0.0",
    ),
    EnvironmentVariable(
        name="API_PORT",
        description="API server port",
        default="8001",
        validator=validate_port,
    ),
    EnvironmentVariable(
        name="LOG_LEVEL",
        description="Logging verbosity level",
        default="INFO",
        validator=validate_log_level,
    ),
    EnvironmentVariable(
        name="CORS_ORIGINS",
        description="Allowed CORS origins",
        required=True,
        validator=validate_cors_origins,
    ),
    
    # API Keys & External Services
    EnvironmentVariable(
        name="OPENAI_API_KEY",
        description="OpenAI API key for GPT models",
        pattern=r"^sk-",
        sensitive=True,
    ),
    EnvironmentVariable(
        name="DEEPSEEK_API_KEY",
        description="DeepSeek API key",
        sensitive=True,
    ),
    EnvironmentVariable(
        name="HUGGINGFACE_API_KEY",
        description="Hugging Face API token",
        pattern=r"^hf_",
        sensitive=True,
    ),
    
    # Database
    EnvironmentVariable(
        name="DATABASE_URL",
        description="Primary database connection string",
        pattern=r"^postgresql://",
        sensitive=True,
    ),
    
    # Observability
    EnvironmentVariable(
        name="ENABLE_METRICS",
        description="Enable Prometheus metrics",
        default="true",
        validator=validate_boolean,
    ),
    EnvironmentVariable(
        name="ENABLE_TRACING",
        description="Enable distributed tracing",
        default="true",
        validator=validate_boolean,
    ),
    
    # Temporal
    EnvironmentVariable(
        name="TEMPORAL_HOST",
        description="Temporal server address",
        default="localhost:7233",
    ),
]


# =============================================================================
# VALIDATOR CLASS
# =============================================================================

class EnvironmentValidator:
    """Environment variable validator"""
    
    def __init__(self, strict: bool = False, environment: str | None = None):
        """
        Initialize validator
        
        Args:
            strict: Treat warnings as errors
            environment: Override ENVIRONMENT variable for testing
        """
        self.strict = strict
        self.override_environment = environment
        self.results: list[ValidationResult] = []
    
    def validate(self) -> ValidationStatus:
        """
        Validate all environment variables
        
        Returns:
            Overall validation status
        """
        # Override environment if specified
        if self.override_environment:
            os.environ["ENVIRONMENT"] = self.override_environment
        
        env = os.getenv("ENVIRONMENT", "development")
        is_production = env == "production"
        
        print(f"[CHECK] Validating environment: {env}")
        print("=" * 70)
        
        # Validate each variable
        for var_spec in ENVIRONMENT_VARIABLES:
            self._validate_variable(var_spec, is_production)
        
        # Print results
        self._print_results()
        
        # Determine overall status
        return self._determine_status()
    
    def _validate_variable(self, var_spec: EnvironmentVariable, is_production: bool):
        """Validate a single environment variable"""
        value = os.getenv(var_spec.name)
        
        # Check if required
        is_required = var_spec.required or (is_production and var_spec.required_in_production)
        
        if value is None or value == "":
            if is_required:
                self.results.append(ValidationResult(
                    variable=var_spec.name,
                    severity=Severity.ERROR if is_production else Severity.WARNING,
                    message=f"Required variable not set: {var_spec.description}",
                ))
            elif var_spec.default:
                self.results.append(ValidationResult(
                    variable=var_spec.name,
                    severity=Severity.INFO,
                    message=f"Using default value: {var_spec.default}",
                ))
            return
        
        # Pattern validation
        if var_spec.pattern and not re.match(var_spec.pattern, value):
            self.results.append(ValidationResult(
                variable=var_spec.name,
                severity=Severity.WARNING,
                message=f"Value doesn't match expected pattern: {var_spec.pattern}",
                value_preview=self._preview_value(value, var_spec.sensitive),
            ))
        
        # Length validation
        if var_spec.min_length and len(value) < var_spec.min_length:
            self.results.append(ValidationResult(
                variable=var_spec.name,
                severity=Severity.ERROR,
                message=f"Value too short (minimum {var_spec.min_length} chars, got {len(value)})",
            ))
        
        # Custom validator
        if var_spec.validator:
            is_valid, error_message = var_spec.validator(value)
            if not is_valid:
                self.results.append(ValidationResult(
                    variable=var_spec.name,
                    severity=Severity.ERROR,
                    message=error_message or "Validation failed",
                    value_preview=self._preview_value(value, var_spec.sensitive),
                ))
    
    def _preview_value(self, value: str, sensitive: bool) -> str:
        """Create a safe preview of a value"""
        if sensitive:
            if len(value) <= 4:
                return "***"
            return f"{value[:4]}...{value[-4:]}"
        return value if len(value) <= 50 else f"{value[:50]}..."
    
    def _print_results(self):
        """Print validation results"""
        # Group by severity
        by_severity = {
            Severity.CRITICAL: [],
            Severity.ERROR: [],
            Severity.WARNING: [],
            Severity.INFO: [],
        }
        
        for result in self.results:
            by_severity[result.severity].append(result)
        
        # Print by severity
        for severity in [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]:
            results = by_severity[severity]
            if not results:
                continue
            
            icon = {
                Severity.CRITICAL: "[CRIT]",
                Severity.ERROR: "[ERR] ",
                Severity.WARNING: "[WARN]",
                Severity.INFO: "[INFO]",
            }[severity]
            
            print(f"\n{icon} {severity.value} ({len(results)})")
            print("-" * 70)
            
            for result in results:
                print(f"  • {result.variable}: {result.message}")
                if result.value_preview:
                    print(f"    Value: {result.value_preview}")
    
    def _determine_status(self) -> ValidationStatus:
        """Determine overall validation status"""
        has_errors = any(r.severity in [Severity.ERROR, Severity.CRITICAL] for r in self.results)
        has_warnings = any(r.severity == Severity.WARNING for r in self.results)
        
        print("\n" + "=" * 70)
        
        if has_errors:
            print("[FAIL] VALIDATION FAILED")
            return ValidationStatus.FAILED
        elif has_warnings and self.strict:
            print("[FAIL] VALIDATION FAILED (strict mode: warnings treated as errors)")
            return ValidationStatus.FAILED
        elif has_warnings:
            print("[WARN] VALIDATION PASSED WITH WARNINGS")
            return ValidationStatus.PASSED_WITH_WARNINGS
        else:
            print("[PASS] VALIDATION PASSED")
            return ValidationStatus.PASSED


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def export_schema():
    """Export environment variable schema as JSON"""
    import json
    
    schema = {
        "variables": [
            {
                "name": var.name,
                "description": var.description,
                "required": var.required,
                "required_in_production": var.required_in_production,
                "default": var.default,
                "pattern": var.pattern,
                "min_length": var.min_length,
                "sensitive": var.sensitive,
                "example": var.example,
            }
            for var in ENVIRONMENT_VARIABLES
        ]
    }
    
    print(json.dumps(schema, indent=2))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate environment configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        help="Override ENVIRONMENT variable for validation",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--export-schema",
        action="store_true",
        help="Export validation schema as JSON",
    )
    
    args = parser.parse_args()
    
    if args.export_schema:
        export_schema()
        return 0
    
    # Run validation
    validator = EnvironmentValidator(
        strict=args.strict,
        environment=args.env,
    )
    
    status = validator.validate()
    
    # Exit with appropriate code
    if status == ValidationStatus.FAILED:
        return 1
    elif status == ValidationStatus.PASSED_WITH_WARNINGS:
        return 0  # Warnings don't cause failure (unless --strict)
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
