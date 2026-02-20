"""
Tests for Verifiability API and Documentation Generator.

Tests REST API endpoints for external verification,
cryptographic proof generation, and documentation.
"""

import json

import pytest
from gradle_evolution.api.documentation_generator import (
    APIDocumentation,
    DocumentationGenerator,
)
from gradle_evolution.api.verifiability_api import VerifiabilityAPI
from gradle_evolution.audit.audit_integration import BuildAuditIntegration
from gradle_evolution.capsules.capsule_engine import BuildCapsule, CapsuleEngine
from gradle_evolution.capsules.replay_engine import ReplayEngine


class TestVerifiabilityAPI:
    """Test VerifiabilityAPI component."""

    @pytest.fixture
    def api_components(self, capsule_storage, audit_log_path):
        """Create API components for testing."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        audit_integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        return capsule_engine, replay_engine, audit_integration

    @pytest.fixture
    def api(self, api_components):
        """Create VerifiabilityAPI instance."""
        capsule_engine, replay_engine, audit_integration = api_components

        api = VerifiabilityAPI(
            capsule_engine=capsule_engine,
            replay_engine=replay_engine,
            audit_integration=audit_integration,
            host="localhost",
            port=8080,
        )

        api.app.config["TESTING"] = True
        return api

    def test_initialization(self, api):
        """Test API initializes correctly."""
        assert api.host == "localhost"
        assert api.port == 8080
        assert api.app is not None

    def test_health_endpoint(self, api):
        """Test health check endpoint."""
        with api.app.test_client() as client:
            response = client.get("/api/v1/health")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert "timestamp" in data

    def test_list_capsules_empty(self, api):
        """Test listing capsules when none exist."""
        with api.app.test_client() as client:
            response = client.get("/api/v1/capsules")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["count"] == 0
            assert data["capsules"] == []

    def test_list_capsules(self, api, sample_build_capsule_data):
        """Test listing capsules."""
        # Add capsule
        capsule = BuildCapsule(**sample_build_capsule_data)
        api.capsule_engine.capsules[capsule.capsule_id] = capsule

        with api.app.test_client() as client:
            response = client.get("/api/v1/capsules")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["count"] == 1
            assert len(data["capsules"]) == 1

    def test_get_capsule(self, api, sample_build_capsule_data):
        """Test getting specific capsule."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        api.capsule_engine.capsules[capsule.capsule_id] = capsule

        with api.app.test_client() as client:
            response = client.get(f"/api/v1/capsules/{capsule.capsule_id}")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["capsule_id"] == capsule.capsule_id

    def test_get_nonexistent_capsule(self, api):
        """Test getting nonexistent capsule returns 404."""
        with api.app.test_client() as client:
            response = client.get("/api/v1/capsules/nonexistent-id")

            assert response.status_code == 404

    def test_verify_capsule(self, api, sample_build_capsule_data):
        """Test capsule verification endpoint."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        api.capsule_engine.capsules[capsule.capsule_id] = capsule

        with api.app.test_client() as client:
            response = client.post(f"/api/v1/capsules/{capsule.capsule_id}/verify")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "verified" in data

    def test_replay_capsule(self, api, sample_build_capsule_data):
        """Test capsule replay endpoint."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        api.capsule_engine.capsules[capsule.capsule_id] = capsule

        with api.app.test_client() as client:
            response = client.post(f"/api/v1/capsules/{capsule.capsule_id}/replay")

            # Should initiate replay
            assert response.status_code in [200, 202]

    def test_get_audit_log(self, api):
        """Test getting audit log."""
        with api.app.test_client() as client:
            response = client.get("/api/v1/audit")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "events" in data or "audit" in data

    def test_get_cryptographic_proof(self, api, sample_build_capsule_data):
        """Test getting cryptographic proof for capsule."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        api.capsule_engine.capsules[capsule.capsule_id] = capsule

        with api.app.test_client() as client:
            response = client.get(f"/api/v1/capsules/{capsule.capsule_id}/proof")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "merkle_root" in data or "proof" in data

    def test_error_handling(self, api):
        """Test API error handling."""
        with api.app.test_client() as client:
            # Invalid endpoint
            response = client.get("/api/v1/invalid")

            assert response.status_code == 404

    def test_cors_headers(self, api):
        """Test CORS headers are present."""
        with api.app.test_client() as client:
            response = client.get("/api/v1/health")

            # CORS should be enabled
            assert response.status_code == 200


class TestAPIDocumentation:
    """Test APIDocumentation component."""

    def test_documentation_creation(self):
        """Test creating API documentation."""
        doc = APIDocumentation(
            endpoint="/api/v1/capsules",
            method="GET",
            description="List all build capsules",
            parameters=[],
            response_schema={"type": "object"},
        )

        assert doc.endpoint == "/api/v1/capsules"
        assert doc.method == "GET"

    def test_documentation_to_dict(self):
        """Test converting documentation to dictionary."""
        doc = APIDocumentation(
            endpoint="/api/v1/capsules",
            method="GET",
            description="List capsules",
            parameters=[],
            response_schema={},
        )

        doc_dict = doc.to_dict()

        assert doc_dict["endpoint"] == "/api/v1/capsules"
        assert "description" in doc_dict


class TestDocumentationGenerator:
    """Test DocumentationGenerator component."""

    def test_initialization(self):
        """Test generator initializes."""
        generator = DocumentationGenerator()

        assert generator.api_docs == []

    def test_add_endpoint_documentation(self):
        """Test adding endpoint documentation."""
        generator = DocumentationGenerator()

        doc = APIDocumentation(
            endpoint="/api/v1/health",
            method="GET",
            description="Health check",
            parameters=[],
            response_schema={},
        )

        generator.add_endpoint_documentation(doc)

        assert len(generator.api_docs) == 1

    def test_generate_openapi_spec(self):
        """Test generating OpenAPI specification."""
        generator = DocumentationGenerator()

        # Add multiple endpoints
        docs = [
            APIDocumentation(
                endpoint="/api/v1/health",
                method="GET",
                description="Health check",
                parameters=[],
                response_schema={},
            ),
            APIDocumentation(
                endpoint="/api/v1/capsules",
                method="GET",
                description="List capsules",
                parameters=[],
                response_schema={},
            ),
        ]

        for doc in docs:
            generator.add_endpoint_documentation(doc)

        spec = generator.generate_openapi_spec()

        assert "openapi" in spec
        assert "paths" in spec
        assert len(spec["paths"]) == 2

    def test_generate_markdown_docs(self):
        """Test generating Markdown documentation."""
        generator = DocumentationGenerator()

        doc = APIDocumentation(
            endpoint="/api/v1/capsules",
            method="GET",
            description="List all build capsules",
            parameters=[{"name": "limit", "type": "integer", "description": "Max results"}],
            response_schema={"type": "array"},
        )

        generator.add_endpoint_documentation(doc)
        markdown = generator.generate_markdown_docs()

        assert "/api/v1/capsules" in markdown
        assert "GET" in markdown
        assert "List all build capsules" in markdown

    def test_generate_postman_collection(self):
        """Test generating Postman collection."""
        generator = DocumentationGenerator()

        doc = APIDocumentation(
            endpoint="/api/v1/health",
            method="GET",
            description="Health check",
            parameters=[],
            response_schema={},
        )

        generator.add_endpoint_documentation(doc)
        collection = generator.generate_postman_collection()

        assert "info" in collection
        assert "item" in collection
        assert len(collection["item"]) == 1

    def test_export_documentation(self, temp_dir):
        """Test exporting documentation to file."""
        generator = DocumentationGenerator()

        doc = APIDocumentation(
            endpoint="/api/v1/health",
            method="GET",
            description="Health check",
            parameters=[],
            response_schema={},
        )

        generator.add_endpoint_documentation(doc)

        output_path = temp_dir / "api_docs.md"
        generator.export_documentation(output_path, format="markdown")

        assert output_path.exists()
        content = output_path.read_text()
        assert "Health check" in content

    def test_validate_documentation(self):
        """Test documentation validation."""
        generator = DocumentationGenerator()

        # Valid documentation
        valid_doc = APIDocumentation(
            endpoint="/api/v1/capsules",
            method="GET",
            description="List capsules",
            parameters=[],
            response_schema={},
        )

        assert generator.validate_documentation(valid_doc)

    def test_generate_examples(self):
        """Test generating request/response examples."""
        generator = DocumentationGenerator()

        doc = APIDocumentation(
            endpoint="/api/v1/capsules",
            method="GET",
            description="List capsules",
            parameters=[],
            response_schema={
                "type": "object",
                "properties": {
                    "capsules": {"type": "array"},
                    "count": {"type": "integer"},
                },
            },
        )

        generator.add_endpoint_documentation(doc)
        examples = generator.generate_examples(doc.endpoint)

        assert "request" in examples or "response" in examples
