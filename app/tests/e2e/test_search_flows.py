"""
End-to-end tests for search functionality.

This module contains tests that verify the search functionality through the web UI,
including searching for orders by customer, title, and log number.
"""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import event

from app.extensions import db
from app.tests.e2e.helpers import login, submit_form, check_flash_message


class TestSearchFlows:
    """End-to-end tests for search functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, client, sample_user, valid_user_data):
        """Set up the test by logging in."""
        login(client, valid_user_data['username'], valid_user_data['password'])
        yield
    
    def test_search_by_customer(self, client, sample_order, sample_customer):
        """Test searching for orders by customer."""
        # Navigate to the search form
        response = client.get('/search')
        assert response.status_code == 200
        
        # Submit the search form with customer ID
        form_data = {
            'cust': sample_customer.cust_id,
            'title': ''
        }
        
        response = submit_form(client, '/search', form_data, method='POST')
        
        # Verify search results are displayed
        assert response.status_code == 200
        assert sample_order.log in response.data.decode('utf-8')
        assert sample_order.title in response.data.decode('utf-8')
    
    def test_search_by_title(self, client, sample_order):
        """Test searching for orders by title."""
        # Navigate to the search form
        response = client.get('/search')
        assert response.status_code == 200
        
        # Submit the search form with title
        form_data = {
            'cust': '',
            'title': sample_order.title
        }
        
        response = submit_form(client, '/search', form_data, method='POST')
        
        # Verify search results are displayed
        assert response.status_code == 200
        assert sample_order.log in response.data.decode('utf-8')
        assert sample_order.title in response.data.decode('utf-8')
    
    def test_search_by_log(self, client, sample_order):
        """Test searching for orders by log number."""
        # Navigate to the search form
        response = client.get('/search_log')
        assert response.status_code == 200
        
        # Submit the search form with log number
        form_data = {
            'log': sample_order.log
        }
        
        response = submit_form(client, '/search_log', form_data, method='POST')
        
        # Verify we're redirected to the order edit page
        assert response.status_code == 200
        assert sample_order.log in response.data.decode('utf-8')
        assert sample_order.title in response.data.decode('utf-8')
    
    def test_search_no_results(self, client):
        """Test searching with no matching results."""
        # Navigate to the search form
        response = client.get('/search')
        assert response.status_code == 200
        
        # Submit the search form with a valid but non-matching customer and title
        form_data = {
            'cust': '99999',
            'title': 'nonexistent'
        }
        
        response = submit_form(client, '/search', form_data, method='POST')
        
        # Verify we get a flash message about no results
        assert check_flash_message(response, "Could not find any orders that match")

    def test_search_log_not_found(self, client):
        """Test searching for a non-existent log number."""
        response = client.get('/search_log')
        assert response.status_code == 200

        # A well-formed log number (5 alphanumeric characters) that does not exist
        response = submit_form(client, '/search_log', {'log': '99999'}, method='POST')

        assert check_flash_message(response, "Log number does not exist")


class TestOrderSearchPagination:
    """Database-paginated order search coverage."""

    @pytest.fixture(autouse=True)
    def setup(self, client, sample_user):
        """Authenticate the client without depending on the login form."""
        with client.session_transaction() as session:
            session['_user_id'] = str(sample_user.id)
            session['_fresh'] = True
        yield

    def test_order_search_paginates_matching_orders_in_database(
        self, client, sample_customer, order_factory
    ):
        """Search pages should fetch only matching rows for the requested page."""
        matching_orders = [
            order_factory(
                cust=sample_customer.cust_id,
                title='Pagination Target',
                datin=date.today(),
                dueout=date.today() + timedelta(days=7),
            )
            for _ in range(22)
        ]
        wrong_title_order = order_factory(
            cust=sample_customer.cust_id,
            title='Different title',
            datin=date.today(),
            dueout=date.today() + timedelta(days=7),
        )
        wrong_customer_order = order_factory(
            cust='99999',
            title='Pagination Target',
            datin=date.today(),
            dueout=date.today() + timedelta(days=7),
        )
        deleted_order = order_factory(
            cust=sample_customer.cust_id,
            title='Pagination Target',
            datin=date.today(),
            dueout=date.today() + timedelta(days=7),
            deleted_at=datetime.now(),
        )

        expected_orders = sorted(
            matching_orders, key=lambda order: order.id, reverse=True
        )
        statements = []

        def capture_order_queries(
            _connection, _cursor, statement, _parameters, _context, _executemany
        ):
            if (
                'FROM "Orders"' in statement
                and statement.lstrip().upper().startswith('SELECT')
            ):
                statements.append(statement)

        with client.application.app_context():
            event.listen(db.engine, 'before_cursor_execute', capture_order_queries)
            try:
                response = client.get(
                    '/order_search/',
                    query_string={
                        'cust': sample_customer.cust_id,
                        'title': 'Pagination Target',
                        'page': 2,
                    },
                )
            finally:
                event.remove(db.engine, 'before_cursor_execute', capture_order_queries)

        assert response.status_code == 200
        assert any(
            'LIMIT' in statement.upper() and 'OFFSET' in statement.upper()
            for statement in statements
        )
        response_text = response.get_data(as_text=True)
        assert [order.log in response_text for order in expected_orders[:20]] == [False] * 20
        assert all(order.log in response_text for order in expected_orders[20:])
        assert wrong_title_order.log not in response_text
        assert wrong_customer_order.log not in response_text
        assert deleted_order.log not in response_text
        assert 'cust=' + sample_customer.cust_id in response_text
        assert 'title=Pagination+Target' in response_text or 'title=Pagination%20Target' in response_text
        response = client.get(
            '/order_search/',
            query_string={
                'cust': sample_customer.cust_id,
                'title': 'Pagination Target',
                'page': 1,
            },
        )
        response_text = response.get_data(as_text=True)
        assert all(order.log in response_text for order in expected_orders[:20])
        assert all(order.log not in response_text for order in expected_orders[20:])
        assert wrong_title_order.log not in response_text
        assert wrong_customer_order.log not in response_text
        assert deleted_order.log not in response_text

        response = client.get(
            '/order_search/',
            query_string={
                'cust': sample_customer.cust_id,
                'title': 'Pagination Target',
                'page': 3,
            },
        )
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert all(order.log not in response_text for order in matching_orders)

    @pytest.mark.parametrize('page', ['invalid', '0', '-1'])
    def test_order_search_normalizes_invalid_page_values(
        self, client, sample_customer, order_factory, page
    ):
        order = order_factory(
            cust=sample_customer.cust_id,
            title='Page Normalization Target',
            datin=date.today(),
            dueout=date.today() + timedelta(days=7),
        )

        response = client.get(
            '/order_search/',
            query_string={
                'cust': sample_customer.cust_id,
                'title': 'Page Normalization Target',
                'page': page,
            },
        )

        assert response.status_code == 200
        assert order.log in response.get_data(as_text=True)

    def test_order_search_without_matches_redirects_to_search_form(self, client):
        response = client.get('/order_search/', query_string={'cust': 'no-match'})

        assert response.status_code == 302
        assert response.location.endswith('/search')


class TestDueoutListProjection:
    @pytest.fixture(autouse=True)
    def authenticate(self, client, sample_user):
        with client.session_transaction() as session:
            session['_user_id'] = str(sample_user.id)
            session['_fresh'] = True

    def test_dueout_ui_renders_projected_order_content(
        self, client, sample_customer, order_factory
    ):
        due_date = date.today()
        order = order_factory(
            cust=sample_customer.cust_id,
            log='72001',
            title='Dueout UI Projection',
            dueout=due_date,
            datin=due_date,
            logtype='TR',
        )

        response = client.post(
            '/dueouts',
            data={
                'start_date': due_date.isoformat(),
                'end_date': (due_date + timedelta(days=1)).isoformat(),
            },
        )

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert order.log in response_text
        assert order.title in response_text
        assert due_date.isoformat() in response_text
    