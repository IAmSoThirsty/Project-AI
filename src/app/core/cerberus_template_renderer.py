"""
Cerberus Template Renderer
===========================

Safe template substitution for Cerberus agent code generation.
Uses {{PLACEHOLDER}} format with validation and escaping support.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """
    Safe template substitution engine for Cerberus agents.

    Features:
    - Use {{PLACEHOLDER}} format for variable substitution
    - Validate required variables are present
    - Support variable allowlist per template
    - Handle escaping for different language syntaxes
    - Prevent injection attacks through validation
    """

    # Common required variables for agent templates
    AGENT_TEMPLATE_VARS = {
        "agent_id",
        "human_lang",
        "human_lang_name",
        "programming_lang",
        "programming_lang_name",
        "locked_section",
        "generation",
        "spawn_time",
        "incident_id",
        "runtime_path",
    }

    # Language-specific escaping rules
    ESCAPE_RULES = {
        "python": {"\\": "\\\\", '"': '\\"', "'": "\\'", "\n": "\\n"},
        "javascript": {"\\": "\\\\", '"': '\\"', "'": "\\'", "\n": "\\n", "`": "\\`"},
        "go": {"\\": "\\\\", '"': '\\"', "\n": "\\n"},
        "bash": {"\\": "\\\\", '"': '\\"', "$": "\\$", "`": "\\`"},
        "java": {"\\": "\\\\", '"': '\\"', "\n": "\\n"},
        "rust": {"\\": "\\\\", '"': '\\"', "\n": "\\n"},
        "c": {"\\": "\\\\", '"': '\\"', "\n": "\\n"},
        "cpp": {"\\": "\\\\", '"': '\\"', "\n": "\\n"},
    }

    def __init__(self):
        """Initialize TemplateRenderer."""
        self.template_cache: dict[str, str] = {}

    def render(
        self,
        template_content: str,
        context: dict[str, Any],
        language: str | None = None,
        validate_required: bool = True,
        allowed_vars: set[str] | None = None,
    ) -> str:
        """
        Render a template with safe variable substitution.

        Args:
            template_content: Template string with {{VAR}} placeholders
            context: Dictionary of variables to substitute
            language: Programming language for escaping (optional)
            validate_required: Whether to validate required variables are present
            allowed_vars: Set of allowed variable names (None = allow all)

        Returns:
            Rendered template string

        Raises:
            ValueError: If required variables are missing or validation fails
        """
        # Extract placeholders from template
        placeholders = self._extract_placeholders(template_content)

        # Validate required variables
        if validate_required:
            missing_vars = self._validate_required_vars(placeholders, context)
            if missing_vars:
                raise ValueError(
                    f"Missing required variables: {', '.join(sorted(missing_vars))}"
                )

        # Validate allowed variables
        if allowed_vars is not None:
            invalid_vars = placeholders - allowed_vars
            if invalid_vars:
                raise ValueError(
                    f"Invalid variables in template: {', '.join(sorted(invalid_vars))}"
                )

        # Apply escaping if language specified
        escaped_context = (
            self._escape_context(context, language) if language else context
        )

        # Perform substitution
        rendered = template_content
        for var_name in placeholders:
            if var_name in escaped_context:
                value = str(escaped_context[var_name])
                rendered = rendered.replace("{{" + var_name + "}}", value)

        # Verify no unsubstituted placeholders remain
        remaining = self._extract_placeholders(rendered)
        if remaining:
            logger.warning("Unsubstituted placeholders remain: %s", ', '.join(sorted(remaining)))

        return rendered

    def render_from_file(
        self,
        template_path: str,
        context: dict[str, Any],
        language: str | None = None,
        validate_required: bool = True,
        cache: bool = True,
    ) -> str:
        """
        Render a template from a file.

        Args:
            template_path: Path to template file
            context: Dictionary of variables to substitute
            language: Programming language for escaping (optional)
            validate_required: Whether to validate required variables
            cache: Whether to cache template content

        Returns:
            Rendered template string
        """
        # Load template content
        if cache and template_path in self.template_cache:
            template_content = self.template_cache[template_path]
        else:
            try:
                with open(template_path, encoding="utf-8") as f:
                    template_content = f.read()

                if cache:
                    self.template_cache[template_path] = template_content

            except Exception as e:
                logger.error("Failed to load template %s: %s", template_path, e)
                raise

        # Render template
        return self.render(
            template_content=template_content,
            context=context,
            language=language,
            validate_required=validate_required,
        )

    def _extract_placeholders(self, template: str) -> set[str]:
        """
        Extract all {{PLACEHOLDER}} variables from template.

        Args:
            template: Template string

        Returns:
            Set of placeholder variable names
        """
        # Match {{VAR_NAME}} pattern
        pattern = r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}"
        matches = re.findall(pattern, template)
        return set(matches)

    def _validate_required_vars(
        self, placeholders: set[str], context: dict[str, Any]
    ) -> set[str]:
        """
        Validate that required variables are present in context.

        Args:
            placeholders: Set of placeholder variable names
            context: Context dictionary

        Returns:
            Set of missing required variables
        """
        # For now, all placeholders are considered required
        # This can be extended to check against AGENT_TEMPLATE_VARS
        missing = placeholders - set(context.keys())
        return missing

    def _escape_context(self, context: dict[str, Any], language: str) -> dict[str, Any]:
        """
        Apply language-specific escaping to context values.

        Args:
            context: Context dictionary
            language: Programming language

        Returns:
            Escaped context dictionary
        """
        escape_rules = self.ESCAPE_RULES.get(language, {})

        if not escape_rules:
            return context

        escaped = {}
        for key, value in context.items():
            if isinstance(value, str):
                # Apply escaping rules
                escaped_value = value
                for char, escaped_char in escape_rules.items():
                    escaped_value = escaped_value.replace(char, escaped_char)
                escaped[key] = escaped_value
            else:
                escaped[key] = value

        return escaped

    def validate_template(self, template_content: str) -> dict[str, Any]:
        """
        Validate a template without rendering.

        Args:
            template_content: Template string

        Returns:
            Dictionary with validation results
        """
        placeholders = self._extract_placeholders(template_content)

        # Check for common required variables
        has_agent_id = "agent_id" in placeholders
        has_locked_section = "locked_section" in placeholders
        has_generation = "generation" in placeholders

        return {
            "valid": True,
            "placeholders": sorted(placeholders),
            "placeholder_count": len(placeholders),
            "has_required_vars": has_agent_id and has_locked_section and has_generation,
            "has_agent_id": has_agent_id,
            "has_locked_section": has_locked_section,
            "has_generation": has_generation,
        }

    def get_required_vars(self) -> set[str]:
        """
        Get set of standard required variables for agent templates.

        Returns:
            Set of required variable names
        """
        return self.AGENT_TEMPLATE_VARS.copy()
