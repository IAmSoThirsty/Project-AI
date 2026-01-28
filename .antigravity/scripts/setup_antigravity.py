#!/usr/bin/env python3
"""
Setup script for Google Antigravity IDE integration with Project-AI.

This script helps configure Antigravity to work seamlessly with
Project-AI's architecture, including ethical review, security
scanning, and Temporal.io workflows.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class AntigravitySetup:
    """Setup helper for Antigravity IDE integration."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize setup helper.
        
        Args:
            project_root: Path to Project-AI root (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.antigravity_dir = self.project_root / ".antigravity"
        self.config_path = self.antigravity_dir / "config.json"
        
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites are met.
        
        Returns:
            Dictionary of prerequisite checks and their status
        """
        checks = {}
        
        # Check Python version
        checks["python_version"] = sys.version_info >= (3, 11)
        
        # Check if Project-AI root
        checks["is_project_ai"] = (self.project_root / "pyproject.toml").exists()
        
        # Check for key directories
        checks["src_exists"] = (self.project_root / "src").exists()
        checks["tests_exists"] = (self.project_root / "tests").exists()
        checks["temporal_exists"] = (self.project_root / "temporal").exists()
        
        # Check for Antigravity config
        checks["config_exists"] = self.config_path.exists()
        
        # Check for required Python packages
        try:
            import temporalio
            checks["temporal_installed"] = True
        except ImportError:
            checks["temporal_installed"] = False
        
        try:
            import openai
            checks["openai_installed"] = True
        except ImportError:
            checks["openai_installed"] = False
        
        return checks
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """Validate Antigravity configuration.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not self.config_path.exists():
            issues.append("Configuration file not found at .antigravity/config.json")
            return False, issues
        
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ["project", "agents", "integrations", "ai_systems"]
            for section in required_sections:
                if section not in config:
                    issues.append(f"Missing required section: {section}")
            
            # Validate project section
            if "project" in config:
                if config["project"].get("name") != "Project-AI":
                    issues.append("Project name mismatch - should be 'Project-AI'")
            
            # Validate AI systems configuration
            if "ai_systems" in config:
                required_systems = ["four_laws", "triumvirate", "ai_persona"]
                for system in required_systems:
                    if system not in config["ai_systems"]:
                        issues.append(f"Missing AI system configuration: {system}")
            
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in config file: {e}")
            return False, issues
        except Exception as e:
            issues.append(f"Error validating config: {e}")
            return False, issues
        
        return len(issues) == 0, issues
    
    def check_agent_files(self) -> Dict[str, bool]:
        """Check if custom agent files exist.
        
        Returns:
            Dictionary of agent file checks
        """
        agents_dir = self.antigravity_dir / "agents"
        
        return {
            "project_ai_agent": (agents_dir / "project_ai_agent.py").exists(),
            "agents_dir_exists": agents_dir.exists()
        }
    
    def check_workflow_files(self) -> Dict[str, bool]:
        """Check if workflow definition files exist.
        
        Returns:
            Dictionary of workflow file checks
        """
        workflows_dir = self.antigravity_dir / "workflows"
        
        return {
            "feature_development": (workflows_dir / "feature-development.yaml").exists(),
            "security_fix": (workflows_dir / "security-fix.yaml").exists(),
            "workflows_dir_exists": workflows_dir.exists()
        }
    
    def print_status(self):
        """Print setup status and recommendations."""
        print("=" * 60)
        print("Google Antigravity IDE - Project-AI Integration Status")
        print("=" * 60)
        print()
        
        # Prerequisites
        print("📋 Prerequisites:")
        prereqs = self.check_prerequisites()
        for check, status in prereqs.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {check.replace('_', ' ').title()}")
        print()
        
        # Configuration
        print("⚙️  Configuration:")
        is_valid, issues = self.validate_config()
        if is_valid:
            print("  ✅ Configuration valid")
        else:
            print("  ❌ Configuration issues:")
            for issue in issues:
                print(f"     - {issue}")
        print()
        
        # Agent files
        print("🤖 Custom Agents:")
        agents = self.check_agent_files()
        for agent, exists in agents.items():
            icon = "✅" if exists else "❌"
            print(f"  {icon} {agent.replace('_', ' ').title()}")
        print()
        
        # Workflow files
        print("📊 Workflows:")
        workflows = self.check_workflow_files()
        for workflow, exists in workflows.items():
            icon = "✅" if exists else "❌"
            print(f"  {icon} {workflow.replace('_', ' ').title()}")
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        recommendations = self.generate_recommendations(prereqs, is_valid, agents, workflows)
        if recommendations:
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("  ✅ All set! Antigravity integration is ready.")
        print()
        
        print("=" * 60)
    
    def generate_recommendations(self, 
                                prereqs: Dict[str, bool],
                                config_valid: bool,
                                agents: Dict[str, bool],
                                workflows: Dict[str, bool]) -> List[str]:
        """Generate setup recommendations.
        
        Args:
            prereqs: Prerequisite check results
            config_valid: Whether config is valid
            agents: Agent file check results
            workflows: Workflow file check results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not prereqs.get("python_version"):
            recommendations.append("Upgrade to Python 3.11 or later")
        
        if not prereqs.get("is_project_ai"):
            recommendations.append("Run this script from the Project-AI root directory")
        
        if not prereqs.get("temporal_installed"):
            recommendations.append("Install Temporal.io: pip install temporalio")
        
        if not prereqs.get("openai_installed"):
            recommendations.append("Install OpenAI: pip install openai")
        
        if not config_valid:
            recommendations.append("Fix configuration issues in .antigravity/config.json")
        
        if not agents.get("project_ai_agent"):
            recommendations.append("Custom agent file missing - reinstall Antigravity integration")
        
        if not workflows.get("feature_development") or not workflows.get("security_fix"):
            recommendations.append("Workflow definitions missing - reinstall Antigravity integration")
        
        return recommendations


def main():
    """Main setup function."""
    print("\n🚀 Setting up Google Antigravity IDE integration for Project-AI\n")
    
    setup = AntigravitySetup()
    setup.print_status()
    
    # Check if ready
    prereqs = setup.check_prerequisites()
    is_valid, _ = setup.validate_config()
    agents = setup.check_agent_files()
    workflows = setup.check_workflow_files()
    
    all_ready = (
        all(prereqs.values()) and
        is_valid and
        all(agents.values()) and
        all(workflows.values())
    )
    
    if all_ready:
        print("\n✅ Antigravity integration is ready!")
        print("\nNext steps:")
        print("1. Download and install Antigravity IDE from https://antigravity.google.com")
        print("2. Open Project-AI in Antigravity: File > Open Folder")
        print("3. Antigravity will automatically detect the configuration")
        print("4. Start using agent-assisted development!\n")
        return 0
    else:
        print("\n⚠️  Setup incomplete - please address the recommendations above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
