"""
End-to-end tests for search functionality.

This module contains tests that verify the search functionality through the web UI,
including searching for orders by customer, title, and log number.
"""

import pytest
from flask import url_for
from app.tests.e2e.helpers import login, submit_form, check_content, check_flash_message


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
        
        # Submit the search form with non-existent customer and title
        form_data = {
            'cust': 'nonexistent',
            'title': 'nonexistent'
        }
        
        response = submit_form(client, '/search', form_data, method='POST')
        
        # Verify we get a flash message about no results
        assert check_flash_message(response, "Could not find any orders that match")
    
    def test_search_log_not_found(self, client):
        """Test searching for a non-existent log number."""
        # Navigate to the search form
        response = client.get('/search_log')
        assert response.status_code == 200
        
        # Submit the search form with non-existent log number
        form_data = {
            'log': 'nonexistent'
        }
        
        response = submit_form(client, '/search_log', form_data, method='POST')
        
        # Verify we get a flash message about log not found
        assert check_flash_message(response, "Log number does not exist")