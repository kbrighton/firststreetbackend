import pytest
import json
from flask import url_for

class TestCustomerAPI:
    """Integration tests for Customer API endpoints."""

    def test_get_customers(self, client, sample_customer):
        """Test getting all customers."""
        response = client.get('/api/customers')
        assert response.status_code == 401  # Unauthorized without login

        # Login
        login_response = client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )
        assert login_response.status_code == 200

        # Try again after login
        response = client.get('/api/customers')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'cust_id' in data[0]
        assert data[0]['cust_id'] == sample_customer.cust_id

    def test_get_customer_by_id(self, client, sample_customer):
        """Test getting a specific customer by ID."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get(f'/api/customers/{sample_customer.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_customer.id
        assert data['cust_id'] == sample_customer.cust_id
        assert data['customer'] == sample_customer.customer

    def test_get_customer_by_cust_id(self, client, sample_customer):
        """Test getting a specific customer by customer ID."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get(f'/api/customers/cust_id/{sample_customer.cust_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_customer.id
        assert data['cust_id'] == sample_customer.cust_id
        assert data['customer'] == sample_customer.customer

    def test_create_customer(self, client, valid_customer_data):
        """Test creating a new customer."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Create a new customer with a different cust_id to avoid conflicts
        customer_data = valid_customer_data.copy()
        customer_data['cust_id'] = '54321'  # Different from sample_customer

        response = client.post(
            '/api/customers',
            json=customer_data
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['cust_id'] == customer_data['cust_id']
        assert data['customer'] == customer_data['customer']
        assert data['customer_email'] == customer_data['customer_email']

    def test_update_customer(self, client, sample_customer):
        """Test updating an existing customer."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        update_data = {
            'customer': 'Updated Customer Name',
            'customer_email': 'updated@example.com'
        }

        response = client.put(
            f'/api/customers/{sample_customer.id}',
            json=update_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_customer.id
        assert data['customer'] == update_data['customer']
        assert data['customer_email'] == update_data['customer_email']

    def test_delete_customer(self, client, sample_customer):
        """Test deleting a customer."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.delete(f'/api/customers/{sample_customer.id}')
        assert response.status_code == 204

        # Verify the customer is deleted
        response = client.get(f'/api/customers/{sample_customer.id}')
        assert response.status_code == 404

    def test_search_customers(self, client, sample_customer):
        """Test searching for customers."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Search by customer name
        response = client.get(f'/api/customers/search?q={sample_customer.customer}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]['cust_id'] == sample_customer.cust_id
        assert data[0]['customer'] == sample_customer.customer

        # Search by customer ID
        response = client.get(f'/api/customers/search?q={sample_customer.cust_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]['cust_id'] == sample_customer.cust_id