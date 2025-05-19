import pytest
import json
from flask import url_for

class TestLegacyAPI:
    """Integration tests for Legacy API endpoints."""

    def test_fetch_data(self, client, sample_order):
        """Test fetching orders data with the legacy endpoint."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Test without parameters
        response = client.get('/api/data')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'total' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
        assert data['data'][0]['log'] == sample_order.log

        # Test with search parameter
        response = client.get(f'/api/data?search={sample_order.log}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) > 0
        assert data['data'][0]['log'] == sample_order.log

        # Test with sort parameter
        response = client.get('/api/data?sort=log')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) > 0

        # Test with pagination
        response = client.get('/api/data?start=0&length=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) <= 10  # Should be at most 10 items

    def test_update_order_legacy(self, client, sample_order):
        """Test updating an order with the legacy endpoint."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Update the order
        update_data = {
            'id': sample_order.id,
            'title': 'Updated via Legacy API',
            'log': sample_order.log  # Include the log to ensure it's not changed
        }

        response = client.post(
            '/api/data',
            json=update_data
        )
        assert response.status_code == 204

        # Verify the update
        response = client.get(f'/api/orders/{sample_order.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_order.id
        assert data['title'] == 'Updated via Legacy API'
        assert data['log'] == sample_order.log

    def test_update_order_legacy_missing_id(self, client):
        """Test updating an order with the legacy endpoint without providing an ID."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Try to update without ID
        update_data = {
            'title': 'This should fail'
        }

        response = client.post(
            '/api/data',
            json=update_data
        )
        assert response.status_code == 400  # Bad request

    def test_update_order_legacy_nonexistent_id(self, client):
        """Test updating a non-existent order with the legacy endpoint."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Try to update with non-existent ID
        update_data = {
            'id': 9999,  # Assuming this ID doesn't exist
            'title': 'This should fail'
        }

        response = client.post(
            '/api/data',
            json=update_data
        )
        assert response.status_code == 404  # Not found