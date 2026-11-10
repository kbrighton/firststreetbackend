import pytest
import json
from datetime import date, datetime, timedelta
from flask import url_for

from app.repositories.order_repository import ORDER_LIST_FIELDS
from app.schemas.order_schema import OrderSchema

class TestOrderAPI:
    """Integration tests for Order API endpoints."""

    @pytest.fixture(autouse=True)
    def create_test_user(self, sample_user):
        """Ensure authenticated API tests have a user available to log in."""

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
        response = client.get('/api/orders', query_string={'cust': sample_order.cust})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert set(data) == {'data', 'total', 'page', 'per_page', 'pages'}
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
        assert 'log' in data['data'][0]
        assert data['data'][0]['log'] == sample_order.log

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

    def test_order_detail_includes_edit_and_admin_metadata_without_changing_list(self, client, db_session, sample_order, sample_user):
        sample_order.artno = 'ART42'
        sample_order.created_by = sample_user
        sample_order.updated_by = sample_user
        db_session.commit()
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'},
        )

        detail_response = client.get(f'/api/orders/log/{sample_order.log}')
        assert detail_response.status_code == 200
        detail = detail_response.get_json()
        assert detail['artno'] == 'ART42'
        assert detail['created_by_username'] == sample_user.username
        assert detail['updated_by_username'] == sample_user.username
        assert 'T' in detail['created_at']
        assert 'T' in detail['updated_at']

        list_response = client.get('/api/orders', query_string={'cust': sample_order.cust})
        assert list_response.status_code == 200
        listed = list_response.get_json()['data'][0]
        assert 'artno' not in listed
        assert 'created_by_username' not in listed

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

    def test_get_all_dueouts_without_date_range(
        self, client, sample_user, sample_customer, order_factory
    ):
        due_order = order_factory(
            cust=sample_customer.cust_id,
            log='71008',
            dueout=date.today(),
            logtype='TR',
        )
        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'},
        )

        response = client.get('/api/orders/dueouts')

        assert response.status_code == 200
        assert due_order.log in {row['log'] for row in response.get_json()}

    def test_dueouts_include_range_boundaries_and_exclude_shipped_deleted_and_other_types(
        self, client, sample_user, sample_customer, order_factory
    ):
        start = date.today()
        end = start + timedelta(days=1)
        due_at_start = order_factory(
            cust=sample_customer.cust_id,
            log='71001',
            dueout=start,
            logtype='TR',
        )
        due_at_end = order_factory(
            cust=sample_customer.cust_id,
            log='71002',
            dueout=end,
            logtype='DP',
        )
        order_factory(
            cust=sample_customer.cust_id,
            log='71003',
            dueout=start - timedelta(days=1),
            logtype='TR',
        )
        order_factory(
            cust=sample_customer.cust_id,
            log='71004',
            dueout=end + timedelta(days=1),
            logtype='TR',
        )
        shipped = order_factory(
            cust=sample_customer.cust_id,
            log='71005',
            dueout=start,
            logtype='TR',
            datout=start,
        )
        deleted = order_factory(
            cust=sample_customer.cust_id,
            log='71006',
            dueout=start,
            logtype='TR',
            deleted_at=datetime.now(),
        )
        other_type = order_factory(
            cust=sample_customer.cust_id,
            log='71007',
            dueout=start,
            logtype='VG',
        )

        client.post(
            '/api/auth/login',
            json={'username': 'testuser', 'password': 'password123'}
        )
        response = client.get(
            '/api/orders/dueouts',
            query_string={
                'start_date': start.isoformat(),
                'end_date': end.isoformat(),
            },
        )

        assert response.status_code == 200
        rows = response.get_json()
        rows_by_log = {row['log']: row for row in rows}
        assert set(rows_by_log) == {due_at_start.log, due_at_end.log}
        assert set(rows_by_log[due_at_start.log]) == set(OrderSchema.Meta.fields)
        assert rows_by_log[due_at_start.log]['dueout'] == start.isoformat()
        assert rows_by_log[due_at_end.log]['dueout'] == end.isoformat()
        assert all(
            order.log not in rows_by_log
            for order in (shipped, deleted, other_type)
        )

    def test_order_list_projection_matches_serialized_schema(self):
        assert set(ORDER_LIST_FIELDS) == set(OrderSchema.Meta.fields)