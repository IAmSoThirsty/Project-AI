#!/usr/bin/env python3
"""
AGENT-079: Batch Cross-Link Generator
Adds comprehensive bidirectional cross-links to all integration, API, web, and CLI documentation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Cross-link definitions: (file_path, section_additions)
CROSSLINKS: Dict[str, Dict[str, List[str]]] = {
    # ============================================================
    # INTEGRATIONS LAYER
    # ============================================================
    
    "relationships/integrations/02-github-integration.md": {
        "Integration Layer (Same Category)": [
            "**[01-openai-integration.md](01-openai-integration.md)**: Primary AI provider",
            "**[11-security-resources-api.md](11-security-resources-api.md)**: GitHub repos for security data",
            "**[05-external-apis.md](05-external-apis.md)**: External API patterns",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: GitHub API integration endpoints",
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance validates GitHub operations",
            "**[../../source-docs/api/12-API-CLIENT-EXAMPLES.md](../../source-docs/api/12-API-CLIENT-EXAMPLES.md)**: Client integration patterns",
        ],
        "Web Layer (User Interface)": [
            "**[../web/04_api_routes_controllers.md](../web/04_api_routes_controllers.md)**: API routes for GitHub integration",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Security practices for external APIs",
        ],
    },
    
    "relationships/integrations/03-huggingface-integration.md": {
        "Integration Layer (Same Category)": [
            "**[01-openai-integration.md](01-openai-integration.md)**: Primary provider (HF is fallback)",
            "**[06-service-adapters.md](06-service-adapters.md)**: Model adapter for provider abstraction",
            "**[10-image-generator.md](10-image-generator.md)**: Stable Diffusion 2.1 consumer",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: Image generation endpoints with HF fallback",
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance for AI operations",
        ],
        "Web Layer (User Interface)": [
            "**[../web/02_react_frontend_architecture.md](../web/02_react_frontend_architecture.md)**: React UI consumes image generation",
            "**[../web/04_api_routes_controllers.md](../web/04_api_routes_controllers.md)**: API routes for image generation",
        ],
    },
    
    "relationships/integrations/04-database-connectors.md": {
        "Integration Layer (Same Category)": [
            "**[05-external-apis.md](05-external-apis.md)**: External data sources",
            "**[06-service-adapters.md](06-service-adapters.md)**: Database adapter pattern",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/01-API-OVERVIEW.md](../../source-docs/api/01-API-OVERVIEW.md)**: API persistence architecture",
            "**[../../source-docs/api/03-SAVE-POINTS-API.md](../../source-docs/api/03-SAVE-POINTS-API.md)**: State save/restore using DB connectors",
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Commit phase uses DB connectors",
        ],
        "Web Layer (User Interface)": [
            "**[../web/06_state_management.md](../web/06_state_management.md)**: Web state persistence backend",
            "**[../web/09_request_flow_state_propagation.md](../web/09_request_flow_state_propagation.md)**: State persistence in request flow",
            "**[../../source-docs/web/07_STATE_MANAGEMENT.md](../../source-docs/web/07_STATE_MANAGEMENT.md)**: Zustand + JSON/SQLite persistence",
        ],
    },
    
    "relationships/integrations/06-service-adapters.md": {
        "Integration Layer (Same Category)": [
            "**[01-openai-integration.md](01-openai-integration.md)**: OpenAI adapter implementation",
            "**[03-huggingface-integration.md](03-huggingface-integration.md)**: HuggingFace adapter implementation",
            "**[04-database-connectors.md](04-database-connectors.md)**: Database adapter pattern",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Adapters enable governance testing",
            "**[../../source-docs/api/12-API-CLIENT-EXAMPLES.md](../../source-docs/api/12-API-CLIENT-EXAMPLES.md)**: Mock adapter usage examples",
        ],
        "Web Layer (User Interface)": [
            "**[../web/07_component_hierarchy.md](../web/07_component_hierarchy.md)**: Component testing with mock adapters",
            "**[../../source-docs/web/09_TESTING_GUIDE.md](../../source-docs/web/09_TESTING_GUIDE.md)**: Testing with service adapters",
        ],
    },
    
    "relationships/integrations/08-intelligence-engine.md": {
        "Integration Layer (Same Category)": [
            "**[01-openai-integration.md](01-openai-integration.md)**: Primary AI provider for intelligence",
            "**[09-learning-paths.md](09-learning-paths.md)**: Learning path intelligence subsystem",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: Intelligence engine exposed via API",
            "**[../../source-docs/api/07-RUNTIME-ROUTER.md](../../source-docs/api/07-RUNTIME-ROUTER.md)**: Router coordinates intelligence requests",
        ],
        "Web Layer (User Interface)": [
            "**[../web/04_api_routes_controllers.md](../web/04_api_routes_controllers.md)**: API routes for AI chat/intelligence",
            "**[../web/09_request_flow_state_propagation.md](../web/09_request_flow_state_propagation.md)**: Intelligence request flow",
        ],
    },
    
    "relationships/integrations/10-image-generator.md": {
        "Integration Layer (Same Category)": [
            "**[01-openai-integration.md](01-openai-integration.md)**: DALL-E 3 provider",
            "**[03-huggingface-integration.md](03-huggingface-integration.md)**: Stable Diffusion fallback",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: Image generation API endpoints",
        ],
        "Web Layer (User Interface)": [
            "**[../web/02_react_frontend_architecture.md](../web/02_react_frontend_architecture.md)**: React image generation UI",
            "**[../web/04_api_routes_controllers.md](../web/04_api_routes_controllers.md)**: Image generation routes",
            "**[../../source-docs/web/06_COMPONENT_LIBRARY.md](../../source-docs/web/06_COMPONENT_LIBRARY.md)**: Image generation components",
        ],
    },
    
    "relationships/integrations/12-email-integration.md": {
        "Integration Layer (Same Category)": [
            "**[13-sms-integration.md](13-sms-integration.md)**: SMS notification alternative",
        ],
        "API Layer (External Interface)": [
            "**[../../source-docs/api/09-SECURITY-AUTH.md](../../source-docs/api/09-SECURITY-AUTH.md)**: Email alerts for authentication events",
            "**[../../source-docs/api/10-SECURITY-MIDDLEWARE.md](../../source-docs/api/10-SECURITY-MIDDLEWARE.md)**: Security middleware triggers email",
        ],
        "Web Layer (User Interface)": [
            "**[../web/03_authentication_system.md](../web/03_authentication_system.md)**: Login alerts via email integration",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Security notification practices",
        ],
    },
    
    # ============================================================
    # API LAYER
    # ============================================================
    
    "source-docs/api/02-FASTAPI-MAIN-ROUTES.md": {
        "Integration Layer (Providers)": [
            "**[../../relationships/integrations/01-openai-integration.md](../../relationships/integrations/01-openai-integration.md)**: OpenAI provider integration",
            "**[../../relationships/integrations/03-huggingface-integration.md](../../relationships/integrations/03-huggingface-integration.md)**: HuggingFace fallback provider",
            "**[../../relationships/integrations/08-intelligence-engine.md](../../relationships/integrations/08-intelligence-engine.md)**: Intelligence engine domain logic",
            "**[../../relationships/integrations/10-image-generator.md](../../relationships/integrations/10-image-generator.md)**: Image generation integration",
        ],
        "API Layer (Parallel Systems)": [
            "**[06-FLASK-WEB-BACKEND.md](06-FLASK-WEB-BACKEND.md)**: Flask web API (parallel path)",
            "**[07-RUNTIME-ROUTER.md](07-RUNTIME-ROUTER.md)**: Router coordinates both API paths",
            "**[08-GOVERNANCE-PIPELINE.md](08-GOVERNANCE-PIPELINE.md)**: Shared governance enforcement",
            "**[09-SECURITY-AUTH.md](09-SECURITY-AUTH.md)**: JWT authentication implementation",
        ],
        "Web Layer (Consumers)": [
            "**[../../relationships/web/01_flask_api_architecture.md](../../relationships/web/01_flask_api_architecture.md)**: Flask architecture (alternative path)",
            "**[../../relationships/web/04_api_routes_controllers.md](../../relationships/web/04_api_routes_controllers.md)**: API route patterns",
        ],
        "CLI Layer (Automation)": [
            "**[../../relationships/cli-automation/01_cli-interface.md](../../relationships/cli-automation/01_cli-interface.md)**: CLI can invoke FastAPI endpoints",
        ],
    },
    
    "source-docs/api/06-FLASK-WEB-BACKEND.md": {
        "Integration Layer (Providers)": [
            "**[../../relationships/integrations/01-openai-integration.md](../../relationships/integrations/01-openai-integration.md)**: OpenAI consumed via orchestrator",
        ],
        "API Layer (Parallel Systems)": [
            "**[01-API-OVERVIEW.md](01-API-OVERVIEW.md)**: Multi-path API architecture",
            "**[02-FASTAPI-MAIN-ROUTES.md](02-FASTAPI-MAIN-ROUTES.md)**: FastAPI (parallel governance path)",
            "**[07-RUNTIME-ROUTER.md](07-RUNTIME-ROUTER.md)**: Router coordinates Flask requests",
            "**[08-GOVERNANCE-PIPELINE.md](08-GOVERNANCE-PIPELINE.md)**: Governance pipeline enforcement",
        ],
        "Web Layer (Implementation)": [
            "**[../../relationships/web/01_flask_api_architecture.md](../../relationships/web/01_flask_api_architecture.md)**: Flask architecture relationships",
            "**[../../relationships/web/02_react_frontend_architecture.md](../../relationships/web/02_react_frontend_architecture.md)**: React frontend consumer",
            "**[../../source-docs/web/01_FLASK_BACKEND_API.md](../../source-docs/web/01_FLASK_BACKEND_API.md)**: Detailed Flask implementation docs",
        ],
        "CLI Layer (Deployment)": [
            "**[../../relationships/cli-automation/03_scripts.md](../../relationships/cli-automation/03_scripts.md)**: Deployment scripts for Flask",
        ],
    },
    
    "source-docs/api/07-RUNTIME-ROUTER.md": {
        "API Layer (Coordinated Systems)": [
            "**[02-FASTAPI-MAIN-ROUTES.md](02-FASTAPI-MAIN-ROUTES.md)**: FastAPI routes through router",
            "**[06-FLASK-WEB-BACKEND.md](06-FLASK-WEB-BACKEND.md)**: Flask routes through router",
            "**[08-GOVERNANCE-PIPELINE.md](08-GOVERNANCE-PIPELINE.md)**: Router enforces governance",
        ],
        "Web Layer (Request Sources)": [
            "**[../../relationships/web/01_flask_api_architecture.md](../../relationships/web/01_flask_api_architecture.md)**: Flask routing patterns",
            "**[../../relationships/web/09_request_flow_state_propagation.md](../../relationships/web/09_request_flow_state_propagation.md)**: Request flow through router",
        ],
        "CLI Layer (Command Routing)": [
            "**[../../relationships/cli-automation/02_command-handlers.md](../../relationships/cli-automation/02_command-handlers.md)**: CLI command routing layer",
        ],
    },
    
    "source-docs/api/08-GOVERNANCE-PIPELINE.md": {
        "Integration Layer (Governed Systems)": [
            "**[../../relationships/integrations/01-openai-integration.md](../../relationships/integrations/01-openai-integration.md)**: OpenAI operations validated",
            "**[../../relationships/integrations/06-service-adapters.md](../../relationships/integrations/06-service-adapters.md)**: Adapters enable governance testing",
        ],
        "API Layer (Enforcement Points)": [
            "**[02-FASTAPI-MAIN-ROUTES.md](02-FASTAPI-MAIN-ROUTES.md)**: FastAPI enforces governance",
            "**[06-FLASK-WEB-BACKEND.md](06-FLASK-WEB-BACKEND.md)**: Flask enforces governance",
            "**[07-RUNTIME-ROUTER.md](07-RUNTIME-ROUTER.md)**: Router coordinates governance",
            "**[09-SECURITY-AUTH.md](09-SECURITY-AUTH.md)**: Gate phase validates JWT",
            "**[11-INPUT-VALIDATION.md](11-INPUT-VALIDATION.md)**: Validation phase sanitizes input",
        ],
        "Web Layer (Governed Operations)": [
            "**[../../relationships/web/05_middleware_security.md](../../relationships/web/05_middleware_security.md)**: Middleware security enforcement",
            "**[../../relationships/web/09_request_flow_state_propagation.md](../../relationships/web/09_request_flow_state_propagation.md)**: Governance in request flow",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Security practices aligned with governance",
        ],
        "CLI Layer (Quality Gates)": [
            "**[../../relationships/cli-automation/09_pre-commit-hooks.md](../../relationships/cli-automation/09_pre-commit-hooks.md)**: Pre-commit governance principles",
        ],
    },
    
    "source-docs/api/09-SECURITY-AUTH.md": {
        "Integration Layer (Notification)": [
            "**[../../relationships/integrations/12-email-integration.md](../../relationships/integrations/12-email-integration.md)**: Email alerts for auth events",
        ],
        "API Layer (Security Stack)": [
            "**[08-GOVERNANCE-PIPELINE.md](08-GOVERNANCE-PIPELINE.md)**: Gate phase validates auth",
            "**[10-SECURITY-MIDDLEWARE.md](10-SECURITY-MIDDLEWARE.md)**: CORS and rate limiting",
            "**[11-INPUT-VALIDATION.md](11-INPUT-VALIDATION.md)**: Input sanitization",
        ],
        "Web Layer (Auth Implementation)": [
            "**[../../relationships/web/03_authentication_system.md](../../relationships/web/03_authentication_system.md)**: Web auth system implementation",
            "**[../../relationships/web/05_middleware_security.md](../../relationships/web/05_middleware_security.md)**: Security middleware patterns",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Comprehensive security guide",
        ],
    },
    
    "source-docs/api/12-API-CLIENT-EXAMPLES.md": {
        "Integration Layer (Patterns)": [
            "**[../../relationships/integrations/05-external-apis.md](../../relationships/integrations/05-external-apis.md)**: External API integration patterns",
            "**[../../relationships/integrations/06-service-adapters.md](../../relationships/integrations/06-service-adapters.md)**: Mock adapter examples",
        ],
        "API Layer (Endpoints)": [
            "**[02-FASTAPI-MAIN-ROUTES.md](02-FASTAPI-MAIN-ROUTES.md)**: FastAPI endpoints referenced",
            "**[06-FLASK-WEB-BACKEND.md](06-FLASK-WEB-BACKEND.md)**: Flask endpoints referenced",
        ],
        "Web Layer (Client Integration)": [
            "**[../../relationships/web/04_api_routes_controllers.md](../../relationships/web/04_api_routes_controllers.md)**: API route integration",
            "**[../../source-docs/web/05_API_CLIENT_INTEGRATION.md](../../source-docs/web/05_API_CLIENT_INTEGRATION.md)**: Axios client implementation",
        ],
    },
    
    # ============================================================
    # WEB RELATIONSHIP LAYER
    # ============================================================
    
    "relationships/web/01_flask_api_architecture.md": {
        "Integration Layer (Services)": [
            "**[../integrations/01-openai-integration.md](../integrations/01-openai-integration.md)**: OpenAI service integration",
            "**[../integrations/04-database-connectors.md](../integrations/04-database-connectors.md)**: Database persistence layer",
        ],
        "API Layer (Implementation)": [
            "**[../../source-docs/api/06-FLASK-WEB-BACKEND.md](../../source-docs/api/06-FLASK-WEB-BACKEND.md)**: Flask API implementation docs",
            "**[../../source-docs/api/07-RUNTIME-ROUTER.md](../../source-docs/api/07-RUNTIME-ROUTER.md)**: Runtime router coordination",
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance enforcement",
        ],
        "Web Layer (Architecture)": [
            "**[02_react_frontend_architecture.md](02_react_frontend_architecture.md)**: React frontend consumer",
            "**[04_api_routes_controllers.md](04_api_routes_controllers.md)**: API routes and controllers",
            "**[05_middleware_security.md](05_middleware_security.md)**: Security middleware",
            "**[09_request_flow_state_propagation.md](09_request_flow_state_propagation.md)**: Complete request flow",
        ],
        "CLI Layer (Deployment)": [
            "**[../cli-automation/03_scripts.md](../cli-automation/03_scripts.md)**: Flask deployment scripts",
        ],
    },
    
    "relationships/web/02_react_frontend_architecture.md": {
        "Integration Layer (Services)": [
            "**[../integrations/01-openai-integration.md](../integrations/01-openai-integration.md)**: AI chat/image consumer",
            "**[../integrations/10-image-generator.md](../integrations/10-image-generator.md)**: Image generation UI",
        ],
        "API Layer (Backend)": [
            "**[../../source-docs/api/06-FLASK-WEB-BACKEND.md](../../source-docs/api/06-FLASK-WEB-BACKEND.md)**: Flask backend endpoints",
        ],
        "Web Layer (Frontend)": [
            "**[01_flask_api_architecture.md](01_flask_api_architecture.md)**: Backend architecture",
            "**[06_state_management.md](06_state_management.md)**: Zustand state management",
            "**[07_component_hierarchy.md](07_component_hierarchy.md)**: Component tree structure",
            "**[../../source-docs/web/02_REACT_FRONTEND.md](../../source-docs/web/02_REACT_FRONTEND.md)**: Detailed React implementation",
        ],
        "CLI Layer (Build)": [
            "**[../cli-automation/04_automation-workflows.md](../cli-automation/04_automation-workflows.md)**: React build automation",
        ],
    },
    
    "relationships/web/03_authentication_system.md": {
        "Integration Layer (Services)": [
            "**[../integrations/12-email-integration.md](../integrations/12-email-integration.md)**: Login email alerts",
        ],
        "API Layer (Security)": [
            "**[../../source-docs/api/09-SECURITY-AUTH.md](../../source-docs/api/09-SECURITY-AUTH.md)**: JWT auth implementation",
            "**[../../source-docs/api/10-SECURITY-MIDDLEWARE.md](../../source-docs/api/10-SECURITY-MIDDLEWARE.md)**: Security middleware",
        ],
        "Web Layer (Auth Flow)": [
            "**[05_middleware_security.md](05_middleware_security.md)**: Security enforcement",
            "**[09_request_flow_state_propagation.md](09_request_flow_state_propagation.md)**: Auth request flow",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Security best practices",
        ],
    },
    
    "relationships/web/05_middleware_security.md": {
        "API Layer (Security)": [
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance enforcement",
            "**[../../source-docs/api/09-SECURITY-AUTH.md](../../source-docs/api/09-SECURITY-AUTH.md)**: Auth implementation",
            "**[../../source-docs/api/10-SECURITY-MIDDLEWARE.md](../../source-docs/api/10-SECURITY-MIDDLEWARE.md)**: CORS and rate limiting",
        ],
        "Web Layer (Security)": [
            "**[03_authentication_system.md](03_authentication_system.md)**: Authentication system",
            "**[09_request_flow_state_propagation.md](09_request_flow_state_propagation.md)**: Security in request flow",
            "**[../../source-docs/web/04_SECURITY_PRACTICES.md](../../source-docs/web/04_SECURITY_PRACTICES.md)**: Security practices",
        ],
        "CLI Layer (Quality)": [
            "**[../cli-automation/06_linting.md](../cli-automation/06_linting.md)**: Security linting",
        ],
    },
    
    "relationships/web/08_deployment_integration.md": {
        "Web Layer (Deployment)": [
            "**[../../source-docs/web/03_DEPLOYMENT_GUIDE.md](../../source-docs/web/03_DEPLOYMENT_GUIDE.md)**: Detailed deployment guide",
        ],
        "CLI Layer (CI/CD)": [
            "**[../cli-automation/03_scripts.md](../cli-automation/03_scripts.md)**: Deployment scripts",
            "**[../cli-automation/04_automation-workflows.md](../cli-automation/04_automation-workflows.md)**: GitHub Actions CI/CD",
        ],
    },
    
    # ============================================================
    # CLI AUTOMATION LAYER
    # ============================================================
    
    "relationships/cli-automation/01_cli-interface.md": {
        "API Layer (Targets)": [
            "**[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: CLI can invoke FastAPI",
        ],
        "CLI Layer (Execution)": [
            "**[02_command-handlers.md](02_command-handlers.md)**: Command routing and execution",
            "**[03_scripts.md](03_scripts.md)**: Execution scripts",
        ],
    },
    
    "relationships/cli-automation/02_command-handlers.md": {
        "API Layer (Routing)": [
            "**[../../source-docs/api/07-RUNTIME-ROUTER.md](../../source-docs/api/07-RUNTIME-ROUTER.md)**: Router handles CLI commands",
        ],
        "CLI Layer (Commands)": [
            "**[01_cli-interface.md](01_cli-interface.md)**: CLI entry points",
            "**[03_scripts.md](03_scripts.md)**: Handler scripts",
        ],
    },
    
    "relationships/cli-automation/03_scripts.md": {
        "Web Layer (Deployment)": [
            "**[../web/01_flask_api_architecture.md](../web/01_flask_api_architecture.md)**: Flask deployment scripts",
            "**[../web/08_deployment_integration.md](../web/08_deployment_integration.md)**: Web deployment automation",
        ],
        "CLI Layer (Automation)": [
            "**[04_automation-workflows.md](04_automation-workflows.md)**: Scripts invoked by workflows",
        ],
    },
    
    "relationships/cli-automation/04_automation-workflows.md": {
        "Web Layer (Build/Deploy)": [
            "**[../web/02_react_frontend_architecture.md](../web/02_react_frontend_architecture.md)**: React build automation",
            "**[../web/08_deployment_integration.md](../web/08_deployment_integration.md)**: Deployment workflows",
        ],
        "CLI Layer (CI/CD)": [
            "**[03_scripts.md](03_scripts.md)**: Workflow invokes scripts",
            "**[06_linting.md](06_linting.md)**: Linting in workflows",
            "**[09_pre-commit-hooks.md](09_pre-commit-hooks.md)**: Pre-commit automation",
        ],
    },
    
    "relationships/cli-automation/06_linting.md": {
        "Web Layer (Quality)": [
            "**[../web/05_middleware_security.md](../web/05_middleware_security.md)**: Security code quality",
        ],
        "CLI Layer (Enforcement)": [
            "**[04_automation-workflows.md](04_automation-workflows.md)**: Linting in CI/CD",
            "**[09_pre-commit-hooks.md](09_pre-commit-hooks.md)**: Pre-commit linting",
        ],
    },
    
    "relationships/cli-automation/09_pre-commit-hooks.md": {
        "API Layer (Quality)": [
            "**[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance principles in hooks",
        ],
        "CLI Layer (Validation)": [
            "**[04_automation-workflows.md](04_automation-workflows.md)**: Hooks + workflows",
            "**[06_linting.md](06_linting.md)**: Linters run in hooks",
        ],
    },
}


def find_related_section(content: str) -> Tuple[int, int, str]:
    """Find the Related Systems/Documentation section and return (start_line, end_line, section_heading)."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if re.match(r'^##\s+(Related\s+(Systems?|Documentation))', line, re.IGNORECASE):
            # Find the next ## heading or end of file
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('##'):
                    end = j
                    break
            return (i, end, line.strip())
    
    return (-1, -1, "")


def enhance_related_section(filepath: Path, crosslinks: Dict[str, List[str]]) -> bool:
    """Add comprehensive cross-links to a file's Related Systems section."""
    
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return False
    
    content = filepath.read_text(encoding='utf-8')
    start, end, section_heading = find_related_section(content)
    
    if start == -1:
        print(f"⚠️  No Related section found in: {filepath.name}")
        return False
    
    lines = content.split('\n')
    
    # Build new Related section
    new_section = [section_heading, ""]
    
    for category, links in crosslinks.items():
        new_section.append(f"### {category}")
        new_section.extend(links)
        new_section.append("")
    
    # Replace old section
    new_lines = lines[:start] + new_section + lines[end:]
    new_content = '\n'.join(new_lines)
    
    filepath.write_text(new_content, encoding='utf-8')
    return True


def main():
    """Process all files with cross-link enhancements."""
    base_path = Path(__file__).parent
    
    stats = {
        'processed': 0,
        'enhanced': 0,
        'failed': 0,
        'total_links': 0,
    }
    
    print("=" * 70)
    print("AGENT-079: Batch Cross-Link Generator")
    print("=" * 70)
    print()
    
    for rel_path, crosslinks in CROSSLINKS.items():
        filepath = base_path / rel_path
        print(f"📝 Processing: {rel_path}")
        
        stats['processed'] += 1
        
        if enhance_related_section(filepath, crosslinks):
            link_count = sum(len(links) for links in crosslinks.values())
            stats['enhanced'] += 1
            stats['total_links'] += link_count
            print(f"   ✅ Enhanced with {link_count} cross-links")
        else:
            stats['failed'] += 1
            print(f"   ❌ Failed to enhance")
        
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files Processed:  {stats['processed']}")
    print(f"Files Enhanced:   {stats['enhanced']}")
    print(f"Files Failed:     {stats['failed']}")
    print(f"Total Links Added: {stats['total_links']}")
    print()
    print("✅ Batch cross-linking complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
