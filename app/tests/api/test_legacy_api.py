import pytest
import json
import logging
from datetime import datetime
from flask import url_for

class TestLegacyAPI:
    """Integration tests for Legacy API endpoints."""

    def test_fetch_data(self, client, sample_user, sample_order):
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

    def test_fetch_data_supports_grid_sort_directions_and_multiple_columns(
        self, client, sample_user, sample_customer, order_factory
    ):
        orders = [
            order_factory(cust=sample_customer.cust_id, log='50003', title='Beta'),
            order_factory(cust=sample_customer.cust_id, log='50001', title='Alpha'),
            order_factory(cust=sample_customer.cust_id, log='50002', title='Beta'),
            order_factory(cust=sample_customer.cust_id, log='50004', title='Alpha'),
        ]
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        ascending = client.get('/api/data', query_string={'sort': '+log'})
        assert ascending.status_code == 200
        assert [row['log'] for row in ascending.get_json()['data']] == [
            '50001', '50002', '50003', '50004'
        ]

        unsigned = client.get('/api/data', query_string={'sort': 'log'})
        assert unsigned.status_code == 200
        assert [row['log'] for row in unsigned.get_json()['data']] == [
            '50001', '50002', '50003', '50004'
        ]

        descending = client.get('/api/data', query_string={'sort': '-log'})
        assert descending.status_code == 200
        assert [row['log'] for row in descending.get_json()['data']] == [
            '50004', '50003', '50002', '50001'
        ]

        multiple = client.get(
            '/api/data', query_string={'sort': '+title,-log'}
        )
        assert multiple.status_code == 200
        assert [row['log'] for row in multiple.get_json()['data']] == [
            '50004', '50001', '50003', '50002'
        ]
        assert len(orders) == 4

    def test_fetch_data_uses_stable_id_ties_and_excludes_deleted_orders(
        self, client, sample_user, sample_customer, order_factory
    ):
        orders = [
            order_factory(
                cust=sample_customer.cust_id,
                log=f'6000{index}',
                title='Same title',
            )
            for index in range(1, 4)
        ]
        deleted_order = order_factory(
            cust=sample_customer.cust_id,
            log='60004',
            title='Same title',
            deleted_at=datetime.now(),
        )
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get('/api/data', query_string={'sort': '+title'})

        assert response.status_code == 200
        rows = response.get_json()['data']
        assert [row['log'] for row in rows] == [
            order.log for order in reversed(orders)
        ]
        assert deleted_order.log not in [row['log'] for row in rows]

    @pytest.mark.parametrize('sort_argument', ['deleted_at', 'does_not_exist', '--log'])
    def test_fetch_data_rejects_unsupported_sort_terms(
        self, client, sample_user, sort_argument
    ):
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get('/api/data', query_string={'sort': sort_argument})

        assert response.status_code == 400

    def test_get_orders_rejects_unsupported_sort_terms(self, client, sample_user):
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        response = client.get(
            '/api/orders', query_string={'cust': '12345', 'sort': 'deleted_at'}
        )

        assert response.status_code == 400

    def test_update_order_legacy(self, client, sample_user, sample_order, caplog):
        """Test updating an order with the legacy endpoint."""
        # Login
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )

        # Update the order
        update_data = {
            'id': sample_order.id,
            'title': 'SENSITIVE-ORDER-PAYLOAD',
            'log': sample_order.log  # Include the log to ensure it's not changed
        }

        with caplog.at_level(logging.INFO, logger='app.api.routes'):
            response = client.post('/api/data', json=update_data)
        assert response.status_code == 204
        assert 'SENSITIVE-ORDER-PAYLOAD' not in caplog.text
        assert f'order id={sample_order.id}' in caplog.text

        # Verify the update
        response = client.get(f'/api/orders/{sample_order.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_order.id
        assert data['title'] == 'SENSITIVE-ORDER-PAYLOAD'
        assert data['log'] == sample_order.log

    def test_update_order_legacy_missing_id(self, client, sample_user):
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

    def test_update_order_legacy_nonexistent_id(self, client, sample_user):
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