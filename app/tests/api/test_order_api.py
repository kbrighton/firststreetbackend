import pytest
import json
from datetime import date, timedelta
from flask import url_for

class TestOrderAPI:
    """Integration tests for Order API endpoints."""

    def test_get_orders(self, client, sample_order):
        """Test getting all orders."""
        response = client.get('/api/orders')
        assert response.status_code == 401  # Unauthorized without login

        # Login
        login_response = client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )
        assert login_response.status_code == 200

        # Try again after login
        response = client.get('/api/orders')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0
        assert 'log' in data['items'][0]
        assert data['items'][0]['log'] == sample_order.log

    def test_get_order_by_id(self, client, sample_order):
        """Test getting a specific order by ID."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get(f'/api/orders/{sample_order.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_order.id
        assert data['log'] == sample_order.log

    def test_get_order_by_log(self, client, sample_order):
        """Test getting a specific order by log ID."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get(f'/api/orders/log/{sample_order.log}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_order.id
        assert data['log'] == sample_order.log

    def test_create_order(self, client, valid_order_data):
        """Test creating a new order."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Convert date objects to strings for JSON serialization
        order_data = valid_order_data.copy()
        order_data['datin'] = order_data['datin'].isoformat()
        order_data['dueout'] = order_data['dueout'].isoformat()

        response = client.post(
            '/api/orders',
            json=order_data
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['log'] == valid_order_data['log']
        assert data['title'] == valid_order_data['title']

    def test_update_order(self, client, sample_order):
        """Test updating an existing order."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        update_data = {
            'title': 'Updated Order Title'
        }

        response = client.put(
            f'/api/orders/{sample_order.id}',
            json=update_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_order.id
        assert data['title'] == 'Updated Order Title'

    def test_delete_order(self, client, sample_order):
        """Test deleting an order."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.delete(f'/api/orders/{sample_order.id}')
        assert response.status_code == 204

        # Verify the order is deleted
        response = client.get(f'/api/orders/{sample_order.id}')
        assert response.status_code == 404

    def test_get_dueouts(self, client, sample_order):
        """Test getting orders due out within a date range."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        today = date.today()
        tomorrow = today + timedelta(days=1)

        response = client.get(
            f'/api/orders/dueouts?start_date={today.isoformat()}&end_date={tomorrow.isoformat()}'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # The sample order might not be in the dueouts range, so we don't assert on the content