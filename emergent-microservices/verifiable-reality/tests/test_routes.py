"""Test API routes"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestItemRoutes:
    """Test item CRUD routes"""

    def test_create_item(self, client: TestClient, auth_headers: dict):
        """Test item creation"""
        response = client.post(
            "/api/v1/items",
            json={
                "name": "Test Item",
                "description": "Test Description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert "id" in data

    def test_list_items(self, client: TestClient, auth_headers: dict):
        """Test item listing"""
        response = client.get(
            "/api/v1/items",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_item_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent item"""
        item_id = str(uuid4())
        response = client.get(
            f"/api/v1/items/{item_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_item(self, client: TestClient, auth_headers: dict):
        """Test item update"""
        # Create item first
        create_response = client.post(
            "/api/v1/items",
            json={"name": "Original", "description": "Original desc"},
            headers=auth_headers,
        )
        item_id = create_response.json()["id"]

        # Update item
        response = client.put(
            f"/api/v1/items/{item_id}",
            json={"name": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"

    def test_delete_item(self, client: TestClient, auth_headers: dict):
        """Test item deletion"""
        # Create item first
        create_response = client.post(
            "/api/v1/items",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        item_id = create_response.json()["id"]

        # Delete item
        response = client.delete(
            f"/api/v1/items/{item_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204
