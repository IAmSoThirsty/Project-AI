#!/usr/bin/env python3
"""
Robust Dependency Checker with Version Validation
Checks for specific versions and compatibility

Production-ready dependency validation system.
"""

import importlib
import logging
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class VersionConstraint:
    """Version constraint specification."""
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    exact_version: Optional[str] = None
    feature_flag: Optional[str] = None
    required: bool = False


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Parse version string into tuple of integers.
    
    Args:
        version_str: Version string (e.g., "3.11.2")
        
    Returns:
        Tuple of version components (e.g., (3, 11, 2))
    """
    # Remove any non-numeric suffixes (e.g., "1.0.0rc1" -> "1.0.0")
    version_str = re.split(r'[a-zA-Z]', version_str)[0]
    
    # Split and convert to integers
    parts = version_str.split('.')
    return tuple(int(p) for p in parts if p.isdigit())


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    # Pad shorter version with zeros
    max_len = max(len(v1), len(v2))
    v1 = v1 + (0,) * (max_len - len(v1))
    v2 = v2 + (0,) * (max_len - len(v2))
    
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def get_module_version(module_name: str) -> Optional[str]:
    """
    Get version of an installed module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Version string or None if not found
    """
    try:
        module = importlib.import_module(module_name)
        
        # Try different version attributes
        for attr in ['__version__', 'VERSION', 'version']:
            if hasattr(module, attr):
                version = getattr(module, attr)
                # Handle tuple versions
                if isinstance(version, tuple):
                    return '.'.join(str(v) for v in version)
                return str(version)
        
        # Try importlib.metadata (Python 3.8+)
        try:
            from importlib.metadata import version as get_version
            return get_version(module_name)
        except ImportError:
            pass
        
        return None
        
    except ImportError:
        return None


def check_dependency(
    module_name: str,
    constraint: VersionConstraint
) -> Tuple[bool, str, Optional[str]]:
    """
    Check if a dependency meets version constraints.
    
    Args:
        module_name: Name of the module to check
        constraint: Version constraint to validate
        
    Returns:
        Tuple of (is_satisfied, message, installed_version)
    """
    # Check if module is installed
    try:
        importlib.import_module(module_name)
    except ImportError:
        if constraint.required:
            return False, f"Required module '{module_name}' not installed", None
        else:
            return False, f"Optional module '{module_name}' not installed", None
    
    # Get installed version
    installed_version = get_module_version(module_name)
    
    if installed_version is None:
        if constraint.min_version or constraint.max_version or constraint.exact_version:
            return False, f"Could not determine version of '{module_name}'", None
        else:
            return True, f"Module '{module_name}' installed (version unknown)", None
    
    # Check exact version
    if constraint.exact_version:
        if compare_versions(installed_version, constraint.exact_version) == 0:
            return True, f"Module '{module_name}' version matches exactly: {installed_version}", installed_version
        else:
            return False, f"Module '{module_name}' version mismatch: {installed_version} != {constraint.exact_version}", installed_version
    
    # Check minimum version
    if constraint.min_version:
        if compare_versions(installed_version, constraint.min_version) < 0:
            return False, f"Module '{module_name}' version too old: {installed_version} < {constraint.min_version}", installed_version
    
    # Check maximum version
    if constraint.max_version:
        if compare_versions(installed_version, constraint.max_version) > 0:
            return False, f"Module '{module_name}' version too new: {installed_version} > {constraint.max_version}", installed_version
    
    # All checks passed
    return True, f"Module '{module_name}' version OK: {installed_version}", installed_version


def check_python_version(constraint: VersionConstraint) -> Tuple[bool, str]:
    """
    Check Python interpreter version.
    
    Args:
        constraint: Version constraint for Python
        
    Returns:
        Tuple of (is_satisfied, message)
    """
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Check exact version
    if constraint.exact_version:
        if compare_versions(python_version, constraint.exact_version) == 0:
            return True, f"Python version matches exactly: {python_version}"
        else:
            return False, f"Python version mismatch: {python_version} != {constraint.exact_version}"
    
    # Check minimum version
    if constraint.min_version:
        if compare_versions(python_version, constraint.min_version) < 0:
            return False, f"Python version too old: {python_version} < {constraint.min_version}"
    
    # Check maximum version
    if constraint.max_version:
        if compare_versions(python_version, constraint.max_version) > 0:
            return False, f"Python version too new: {python_version} > {constraint.max_version}"
    
    return True, f"Python version OK: {python_version}"


def check_all_dependencies(
    required_deps: Dict[str, VersionConstraint],
    optional_deps: Dict[str, VersionConstraint]
) -> Dict:
    """
    Check all dependencies and return detailed report.
    
    Args:
        required_deps: Dictionary of required dependencies
        optional_deps: Dictionary of optional dependencies
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'python': {},
        'required': {},
        'optional': {},
        'summary': {
            'all_required_met': True,
            'missing_required': [],
            'missing_optional': [],
            'version_mismatches': [],
            'disabled_features': []
        }
    }
    
    # Check Python version
    if 'python' in required_deps:
        is_ok, message = check_python_version(required_deps['python'])
        results['python'] = {
            'satisfied': is_ok,
            'message': message,
            'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        if not is_ok:
            results['summary']['all_required_met'] = False
            results['summary']['version_mismatches'].append('python')
    
    # Check required dependencies
    for module_name, constraint in required_deps.items():
        if module_name == 'python':
            continue
        
        is_ok, message, version = check_dependency(module_name, constraint)
        results['required'][module_name] = {
            'satisfied': is_ok,
            'message': message,
            'installed_version': version,
            'constraint': {
                'min': constraint.min_version,
                'max': constraint.max_version,
                'exact': constraint.exact_version
            }
        }
        
        if not is_ok:
            results['summary']['all_required_met'] = False
            if version is None:
                results['summary']['missing_required'].append(module_name)
            else:
                results['summary']['version_mismatches'].append(module_name)
    
    # Check optional dependencies
    for module_name, constraint in optional_deps.items():
        is_ok, message, version = check_dependency(module_name, constraint)
        results['optional'][module_name] = {
            'satisfied': is_ok,
            'message': message,
            'installed_version': version,
            'feature_flag': constraint.feature_flag,
            'constraint': {
                'min': constraint.min_version,
                'max': constraint.max_version,
                'exact': constraint.exact_version
            }
        }
        
        if not is_ok:
            if version is None:
                results['summary']['missing_optional'].append(module_name)
            else:
                results['summary']['version_mismatches'].append(module_name)
            
            # Track disabled features
            if constraint.feature_flag:
                results['summary']['disabled_features'].append(constraint.feature_flag)
    
    return results


def load_dependencies_from_config(config_dict: Dict) -> Tuple[Dict, Dict]:
    """
    Load dependency constraints from configuration.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Tuple of (required_deps, optional_deps)
    """
    required_deps = {}
    optional_deps = {}
    
    # Parse required dependencies
    for name, config in config_dict.get('dependencies', {}).get('required', {}).items():
        required_deps[name] = VersionConstraint(
            min_version=config.get('min_version'),
            max_version=config.get('max_version'),
            exact_version=config.get('exact_version'),
            required=True
        )
    
    # Parse optional dependencies
    for name, config in config_dict.get('dependencies', {}).get('optional', {}).items():
        optional_deps[name] = VersionConstraint(
            min_version=config.get('min_version'),
            max_version=config.get('max_version'),
            exact_version=config.get('exact_version'),
            feature_flag=config.get('feature'),
            required=False
        )
    
    return required_deps, optional_deps


if __name__ == '__main__':
    # Test dependency checking
    import json
    
    # Example dependencies
    required = {
        'python': VersionConstraint(min_version='3.11.0', max_version='3.12.999', required=True),
        'pydantic': VersionConstraint(min_version='2.0.0', required=True),
    }
    
    optional = {
        'cv2': VersionConstraint(min_version='4.8.0', feature_flag='enable_video', required=False),
        'whisper': VersionConstraint(min_version='1.0.0', feature_flag='enable_transcript', required=False),
    }
    
    results = check_all_dependencies(required, optional)
    
    print("Dependency Check Results:")
    print(json.dumps(results, indent=2))
    
    if not results['summary']['all_required_met']:
        print("\n❌ Required dependencies not met!")
        sys.exit(1)
    else:
        print("\n✅ All required dependencies satisfied")
