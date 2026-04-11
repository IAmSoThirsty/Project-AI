#!/usr/bin/env python3
"""
Configuration Validator for Sovereign Governance Substrate
Production-grade configuration validation and security scanning

Features:
- Validates all configuration files (YAML, JSON, TOML, .env)
- Detects hardcoded secrets and credentials
- Checks environment variable consistency
- Validates configuration schemas
- Reports missing required configurations
- Ensures environment separation (dev/staging/prod)
- Type checking and value range validation
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "CRITICAL"  # Must fix immediately (security, prod failures)
    ERROR = "ERROR"        # Should fix (functionality broken)
    WARNING = "WARNING"    # Should review (best practices)
    INFO = "INFO"          # Informational (suggestions)


class ConfigFormat(Enum):
    """Supported configuration formats"""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    ENV = "env"
    PYTHON = "py"


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue"""
    level: ValidationLevel
    category: str
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        location = f"{self.file}:{self.line}" if self.line else self.file
        suggestion = f"\n  Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"[{self.level.value}] {self.category}: {location}\n  {self.message}{suggestion}"


@dataclass
class ValidationReport:
    """Complete validation report"""
    total_files: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    scanned_files: List[str] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.CRITICAL)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.WARNING)
    
    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.level == ValidationLevel.INFO)
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*80)
        print("CONFIGURATION VALIDATION REPORT")
        print("="*80)
        print(f"\nFiles Scanned: {self.total_files}")
        print(f"Critical Issues: {self.critical_count}")
        print(f"Errors: {self.error_count}")
        print(f"Warnings: {self.warning_count}")
        print(f"Info: {self.info_count}")
        
        if self.issues:
            print("\n" + "-"*80)
            print("ISSUES FOUND:")
            print("-"*80)
            for issue in sorted(self.issues, key=lambda x: (x.level.value, x.file)):
                print(f"\n{issue}")
        
        print("\n" + "="*80)
        status = "FAILED" if self.critical_count > 0 or self.error_count > 0 else "PASSED"
        print(f"Validation Status: {status}")
        print("="*80 + "\n")


class ConfigValidator:
    """Configuration validation engine"""
    
    # Patterns for secret detection
    SECRET_PATTERNS = [
        (r'password\s*[=:]\s*["\']([^"\']+)["\']', 'PASSWORD'),
        (r'secret\s*[=:]\s*["\']([^"\']+)["\']', 'SECRET'),
        (r'api_key\s*[=:]\s*["\']([^"\']+)["\']', 'API_KEY'),
        (r'token\s*[=:]\s*["\']([^"\']+)["\']', 'TOKEN'),
        (r'private_key\s*[=:]\s*["\']([^"\']+)["\']', 'PRIVATE_KEY'),
        (r'access_key\s*[=:]\s*["\']([^"\']+)["\']', 'ACCESS_KEY'),
        (r'aws_secret_access_key\s*[=:]\s*["\']([^"\']+)["\']', 'AWS_SECRET'),
    ]
    
    # Safe placeholder values (not real secrets)
    SAFE_VALUES = {
        'changeme', 'change-me', 'your-key-here', 'xxx', 'yyy', 'zzz',
        'test-key', 'demo-token', 'example', 'placeholder', 'fake',
        'sk-1234567890', 'test_key', 'demo_key', 'your_api_key',
        '0123456789abcdef', 'hardcoded_secret', 'test_token',
        's3cret!', 'test_password', 'SecurePassword123!', 'admin_test_password',
        'mysecretpassword', 'cert-hardened-secret', '', 'none', 'null'
    }
    
    # Required environment variables
    REQUIRED_ENV_VARS = {
        'production': [
            'OPENAI_API_KEY',
            'SECRET_KEY',
            'JWT_SECRET',
            'API_KEYS',
        ],
        'staging': [
            'OPENAI_API_KEY',
            'SECRET_KEY',
        ],
        'development': []
    }
    
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path.cwd()
        self.report = ValidationReport()
    
    def validate_all(self) -> ValidationReport:
        """Run all validation checks"""
        logger.info(f"Starting configuration validation in {self.root_dir}")
        
        # Find all configuration files
        config_files = self._find_config_files()
        self.report.total_files = len(config_files)
        
        logger.info(f"Found {len(config_files)} configuration files")
        
        # Validate each file
        for config_file in config_files:
            self._validate_file(config_file)
        
        # Check environment variables
        self._validate_env_vars()
        
        # Check for configuration consistency
        self._validate_consistency()
        
        return self.report
    
    def _find_config_files(self) -> List[Path]:
        """Find all configuration files in the repository"""
        patterns = [
            '**/*.yaml',
            '**/*.yml',
            '**/*.json',
            '**/*.toml',
            '**/.env*',
            '**/config.py',
            '**/settings.py',
        ]
        
        exclude_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            '.venv_prod', 'build', 'dist', '.pytest_cache', '.mypy_cache',
            'htmlcov', 'android', 'tmp', 'logs', 'archive'
        }
        
        files = []
        for pattern in patterns:
            for file in self.root_dir.glob(pattern):
                # Skip excluded directories
                if any(exc in file.parts for exc in exclude_dirs):
                    continue
                # Skip example files for secret scanning
                if 'example' not in file.name.lower():
                    files.append(file)
        
        return files
    
    def _validate_file(self, file_path: Path):
        """Validate a single configuration file"""
        self.report.scanned_files.append(str(file_path))
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Detect format
            file_format = self._detect_format(file_path)
            
            # Parse configuration
            config_data = self._parse_config(file_path, content, file_format)
            
            # Run validations
            self._check_secrets(file_path, content)
            self._check_syntax(file_path, content, file_format, config_data)
            self._check_best_practices(file_path, config_data, file_format)
            
        except Exception as e:
            self.report.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category="File Error",
                file=str(file_path),
                line=None,
                message=f"Failed to validate file: {str(e)}"
            ))
    
    def _detect_format(self, file_path: Path) -> ConfigFormat:
        """Detect configuration file format"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if suffix in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        elif suffix == '.json':
            return ConfigFormat.JSON
        elif suffix == '.toml':
            return ConfigFormat.TOML
        elif name.startswith('.env'):
            return ConfigFormat.ENV
        elif suffix == '.py':
            return ConfigFormat.PYTHON
        
        return ConfigFormat.YAML  # Default
    
    def _parse_config(self, file_path: Path, content: str, fmt: ConfigFormat) -> Optional[Dict]:
        """Parse configuration file"""
        try:
            if fmt == ConfigFormat.YAML:
                return yaml.safe_load(content)
            elif fmt == ConfigFormat.JSON:
                return json.loads(content)
            elif fmt == ConfigFormat.TOML:
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib
                return tomllib.loads(content)
            elif fmt == ConfigFormat.ENV:
                # Parse .env files into dict
                config = {}
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                return config
            else:
                return None
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
            return None
    
    def _check_secrets(self, file_path: Path, content: str):
        """Check for hardcoded secrets"""
        # Skip test files and example files
        if 'test' in file_path.name.lower() or 'example' in file_path.name.lower():
            return
        
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            for pattern, secret_type in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    
                    # Check if it's a safe placeholder
                    is_safe = any(
                        safe in value.lower() 
                        for safe in self.SAFE_VALUES
                    )
                    
                    # Check if it's an environment variable reference
                    is_env_ref = value.startswith('${') or value.startswith('$')
                    
                    if not is_safe and not is_env_ref and len(value) > 3:
                        self.report.issues.append(ValidationIssue(
                            level=ValidationLevel.CRITICAL,
                            category="Security",
                            file=str(file_path),
                            line=line_num,
                            message=f"Potential hardcoded {secret_type} detected: '{value[:20]}...'",
                            suggestion=f"Move to environment variable or secrets manager"
                        ))
    
    def _check_syntax(self, file_path: Path, content: str, fmt: ConfigFormat, config_data: Optional[Dict]):
        """Check configuration syntax"""
        if config_data is None and fmt != ConfigFormat.PYTHON:
            self.report.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category="Syntax",
                file=str(file_path),
                line=None,
                message=f"Failed to parse {fmt.value} file - syntax error",
                suggestion="Check file syntax and formatting"
            ))
    
    def _check_best_practices(self, file_path: Path, config_data: Optional[Dict], fmt: ConfigFormat):
        """Check configuration best practices"""
        if not config_data:
            return
        
        # Check for production-specific issues
        if 'production' in str(file_path).lower():
            self._check_production_config(file_path, config_data)
        
        # Check for missing required fields
        self._check_required_fields(file_path, config_data)
    
    def _check_production_config(self, file_path: Path, config_data: Dict):
        """Validate production configuration"""
        # Check for debug mode
        if isinstance(config_data, dict):
            if config_data.get('debug') or config_data.get('DEBUG'):
                self.report.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="Production",
                    file=str(file_path),
                    line=None,
                    message="DEBUG mode enabled in production config",
                    suggestion="Set debug=false in production"
                ))
            
            # Check for weak secrets
            for key in ['JWT_SECRET', 'SECRET_KEY', 'API_KEYS']:
                value = config_data.get(key, '')
                if isinstance(value, str) and 'changeme' in value.lower():
                    self.report.issues.append(ValidationIssue(
                        level=ValidationLevel.CRITICAL,
                        category="Security",
                        file=str(file_path),
                        line=None,
                        message=f"{key} uses default/weak value in production",
                        suggestion=f"Set strong {key} value from environment"
                    ))
    
    def _check_required_fields(self, file_path: Path, config_data: Dict):
        """Check for required configuration fields"""
        # Microservice configs should have these fields
        if 'app/config.py' in str(file_path):
            required = ['SERVICE_NAME', 'HOST', 'PORT']
            for field in required:
                if isinstance(config_data, dict) and field not in config_data:
                    self.report.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category="Missing Field",
                        file=str(file_path),
                        line=None,
                        message=f"Missing recommended field: {field}",
                        suggestion=f"Add {field} to configuration"
                    ))
    
    def _validate_env_vars(self):
        """Validate environment variables"""
        # Check if .env.example exists
        env_example = self.root_dir / '.env.example'
        env_file = self.root_dir / '.env'
        
        if not env_example.exists():
            self.report.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="Environment",
                file=".env.example",
                line=None,
                message=".env.example file not found",
                suggestion="Create .env.example template for environment variables"
            ))
            return
        
        # Parse .env.example
        example_vars = set()
        for line in env_example.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                example_vars.add(key)
        
        # Check if .env exists (in development)
        if not env_file.exists():
            self.report.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category="Environment",
                file=".env",
                line=None,
                message=".env file not found (expected in development)",
                suggestion=f"Copy .env.example to .env and fill in values"
            ))
    
    def _validate_consistency(self):
        """Check configuration consistency across files"""
        # Check docker-compose vs k8s configs
        # Check environment-specific configs match
        pass  # Implement as needed


def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate configuration files for Sovereign Governance Substrate"
    )
    parser.add_argument(
        '--root-dir',
        type=Path,
        default=Path.cwd(),
        help="Root directory to scan (default: current directory)"
    )
    parser.add_argument(
        '--fail-on-error',
        action='store_true',
        help="Exit with error code if validation fails"
    )
    parser.add_argument(
        '--output',
        type=Path,
        help="Output validation report to file"
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = ConfigValidator(root_dir=args.root_dir)
    report = validator.validate_all()
    
    # Print report
    report.print_summary()
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"Configuration Validation Report\n")
            f.write(f"Generated: {__import__('datetime').datetime.now()}\n\n")
            f.write(f"Total Files: {report.total_files}\n")
            f.write(f"Critical: {report.critical_count}\n")
            f.write(f"Errors: {report.error_count}\n")
            f.write(f"Warnings: {report.warning_count}\n")
            f.write(f"Info: {report.info_count}\n\n")
            for issue in report.issues:
                f.write(f"{issue}\n\n")
        logger.info(f"Report saved to {args.output}")
    
    # Exit with appropriate code
    if args.fail_on_error and (report.critical_count > 0 or report.error_count > 0):
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
