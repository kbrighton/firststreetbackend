"""
End-to-end tests for order management flows.

This module contains tests that verify the order management functionality
through the web UI, including creating, editing, and viewing orders.
"""

import pytest
from datetime import date, timedelta
from flask import url_for
from app.tests.e2e.helpers import login, submit_form, check_content, check_flash_message


class TestOrderFlows:
    """End-to-end tests for order management flows."""

    @pytest.fixture(autouse=True)
    def setup(self, client, sample_user, valid_user_data):
        """Set up the test by logging in."""
        login(client, valid_user_data['username'], valid_user_data['password'])
        yield
    
    def test_create_order(self, client, valid_order_data):
        """Test creating a new order."""
        # Navigate to the new order page
        response = client.get('/order')
        assert response.status_code == 200
        assert 'Create New Order' in response.data.decode('utf-8')
        
        # Convert date objects to strings for form submission
        order_data = valid_order_data.copy()
        order_data['datin'] = order_data['datin'].strftime('%Y-%m-%d')
        order_data['dueout'] = order_data['dueout'].strftime('%Y-%m-%d')
        
        # Submit the new order form
        response = submit_form(client, '/order', order_data)
        
        # Verify the order was created successfully
        assert response.status_code == 200
        assert check_flash_message(response, f"Order {valid_order_data['log']} created successfully")
        assert valid_order_data['title'] in response.data.decode('utf-8')
    
    def test_edit_order(self, client, sample_order):
        """Test editing an existing order."""
        # Navigate to the edit order page
        response = client.get(f'/order/{sample_order.log}')
        assert response.status_code == 200
        assert sample_order.title in response.data.decode('utf-8')
        
        # Prepare updated data
        updated_data = {
            'log': sample_order.log,
            'cust': sample_order.cust,
            'title': 'Updated Order Title',
            'datin': sample_order.datin.strftime('%Y-%m-%d'),
            'dueout': sample_order.dueout.strftime('%Y-%m-%d'),
            'logtype': sample_order.logtype,
            'print_n': sample_order.print_n,
            'colorf': sample_order.colorf,
            'subtotal': sample_order.subtotal,
            'total': sample_order.total
        }
        
        # Submit the edit form
        response = submit_form(client, f'/order/{sample_order.log}', updated_data)
        
        # Verify the order was updated successfully
        assert response.status_code == 200
        assert check_flash_message(response, f"Order {sample_order.log} updated successfully")
        assert 'Updated Order Title' in response.data.decode('utf-8')
    
    def test_view_order_not_found(self, client):
        """Test viewing a non-existent order."""
        response = client.get('/order/nonexistent', follow_redirects=True)
        assert check_flash_message(response, "Order with log number nonexistent not found")
    
    def test_view_all_dueouts(self, client, sample_order):
        """Test viewing all due-outs."""
        response = client.get('/dueouts_all')
        assert response.status_code == 200
        # The sample order might not be in the dueouts, so we just check the page structure
        assert 'Due Out' in response.data.decode('utf-8')
    
    def test_view_dueouts_with_date_range(self, client, sample_order):
        """Test viewing due-outs within a date range."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Navigate to the dueouts form
        response = client.get('/dueouts')
        assert response.status_code == 200
        
        # Submit the form with a date range
        form_data = {
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': tomorrow.strftime('%Y-%m-%d')
        }
        
        response = submit_form(client, '/dueouts', form_data)
        
        # Verify the dueouts page is displayed
        assert response.status_code == 200
        assert 'Due Out' in response.data.decode('utf-8')