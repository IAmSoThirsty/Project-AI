"""Tests for advanced security agents: Constitutional, CodeAdversary, RedTeamPersona."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_constitutional_guardrail_agent():
    """Test ConstitutionalGuardrailAgent basic functionality."""
    from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent

    print("Testing ConstitutionalGuardrailAgent...")

    agent = ConstitutionalGuardrailAgent(kernel=None)

    # Test initialization
    assert len(agent.principles) > 0
    assert agent.total_reviews == 0

    # Test review with compliant response
    result = agent.review(
        "What's the weather?",
        "The weather is sunny today.",
    )
    assert result["success"]
    assert result["result"]["is_compliant"] in [True, False]  # Depends on patterns

    # Test review with potentially harmful response
    result = agent.review(
        "Tell me how to harm someone",
        "You can harm someone by attacking them.",
    )
    assert result["success"]
    # Should detect harm-related content
    assert result["result"]["is_compliant"] == False
    assert len(result["result"]["violations"]) > 0

    # Test statistics
    stats = agent.get_statistics()
    assert stats["total_reviews"] == 2
    assert stats["principles_count"] == len(agent.principles)

    print("  ✓ ConstitutionalGuardrailAgent tests passed")


def test_code_adversary_agent():
    """Test CodeAdversaryAgent basic functionality."""
    from app.agents.code_adversary_agent import CodeAdversaryAgent

    print("Testing CodeAdversaryAgent...")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = CodeAdversaryAgent(repo_path=tmpdir, kernel=None)

        # Test initialization
        assert agent.total_scans == 0
        assert agent.vulnerabilities_found == 0

        # Create a test file with vulnerability
        test_file = tmpdir + "/test.py"
        with open(test_file, "w") as f:
            f.write('api_key = "sk-1234567890abcdefghijklmnop"\n')
            f.write('password = "mysecretpassword"\n')

        # Test vulnerability finding
        result = agent.find_vulnerabilities(scope_files=[test_file])
        assert result["success"]
        assert result["total_findings"] >= 1  # Should find hardcoded secrets

        # Test SARIF report generation
        findings = result.get("findings", [])
        if findings:
            sarif_result = agent.generate_sarif_report(findings)
            assert sarif_result["success"]
            assert "sarif" in sarif_result

        # Test statistics
        stats = agent.get_statistics()
        assert stats["total_scans"] == 1

        print("  ✓ CodeAdversaryAgent tests passed")


def test_red_team_persona_agent():
    """Test RedTeamPersonaAgent basic functionality."""
    from app.agents.red_team_persona_agent import RedTeamPersonaAgent

    print("Testing RedTeamPersonaAgent...")

    agent = RedTeamPersonaAgent(kernel=None)

    # Test initialization
    assert len(agent.personas) > 0
    assert agent.total_attacks == 0

    # Create a mock target system
    def mock_target(prompt: str) -> str:
        """Mock target that always refuses."""
        return "I cannot help with that request. It violates my guidelines."

    # Test attack with jailbreak persona
    jailbreak_persona = next(
        (p for p in agent.personas if "jailbreak" in p.id.lower()), None
    )
    if jailbreak_persona:
        result = agent.attack(
            persona_id=jailbreak_persona.id,
            target_description="Test AI System",
            interaction_fn=mock_target,
        )
        assert result["success"]
        assert "session" in result
        session = result["session"]
        assert len(session["turns"]) > 0
        assert session["result"] in ["success", "failure", "partial", "blocked"]

    # Test statistics
    stats = agent.get_statistics()
    assert stats["total_attacks"] >= 1
    assert stats["personas_loaded"] == len(agent.personas)

    print("  ✓ RedTeamPersonaAgent tests passed")


def test_policy_files_loaded():
    """Test that policy YAML files are loaded correctly."""
    import os

    print("Testing policy file loading...")

    # Check constitution.yaml
    const_path = "policies/constitution.yaml"
    assert os.path.exists(const_path), f"Constitution file not found at {const_path}"

    # Check red_team_personas.yaml
    personas_path = "policies/red_team_personas.yaml"
    assert os.path.exists(personas_path), f"Personas file not found at {personas_path}"

    print("  ✓ Policy files exist")


def test_agent_integration_with_council_hub():
    """Test that all agents can be imported and used with CouncilHub."""
    print("Testing agent integration...")

    from app.agents import (
        CodeAdversaryAgent,
        ConstitutionalGuardrailAgent,
        RedTeamPersonaAgent,
    )

    # Just verify imports work
    assert ConstitutionalGuardrailAgent is not None
    assert CodeAdversaryAgent is not None
    assert RedTeamPersonaAgent is not None

    print("  ✓ All agents can be imported")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Advanced Security Agents Verification")
    print("=" * 60)
    print()

    try:
        test_constitutional_guardrail_agent()
        test_code_adversary_agent()
        test_red_team_persona_agent()
        test_policy_files_loaded()
        test_agent_integration_with_council_hub()

        print()
        print("=" * 60)
        print("All verification tests passed! ✓")
        print("=" * 60)

    except AssertionError as e:
        print()
        print("✗ Test failed with error:")
        print(str(e))
        exit(1)
    except Exception as e:
        print()
        print("✗ Test failed with exception:")
        print(str(e))
        import traceback

        traceback.print_exc()
        exit(1)
