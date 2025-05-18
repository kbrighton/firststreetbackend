"""
End-to-end tests for complete user journeys.

This module contains tests that simulate a user going through multiple flows
in a single session, ensuring that the application works as a cohesive whole.
"""

import pytest
from datetime import date, timedelta
from app.tests.e2e.helpers import login, logout, submit_form, check_content, check_flash_message


class TestCompleteUserJourney:
    """End-to-end tests for complete user journeys."""

    def test_complete_journey(self, client, sample_user, valid_user_data, valid_order_data):
        """
        Test a complete user journey through the application.
        
        This test simulates a user:
        1. Logging in
        2. Creating a new order
        3. Searching for the order by log number
        4. Editing the order
        5. Viewing due-outs
        6. Logging out
        """
        # Step 1: Log in
        response = login(client, valid_user_data['username'], valid_user_data['password'])
        assert response.status_code == 200
        assert 'Logout' in response.data.decode('utf-8')
        
        # Step 2: Create a new order
        response = client.get('/order')
        assert response.status_code == 200
        
        # Prepare order data
        order_data = valid_order_data.copy()
        order_data['datin'] = order_data['datin'].strftime('%Y-%m-%d')
        order_data['dueout'] = order_data['dueout'].strftime('%Y-%m-%d')
        
        # Submit the new order form
        response = submit_form(client, '/order', order_data)
        assert response.status_code == 200
        assert check_flash_message(response, f"Order {valid_order_data['log']} created successfully")
        
        # Step 3: Search for the order by log number
        response = client.get('/search_log')
        assert response.status_code == 200
        
        form_data = {
            'log': valid_order_data['log']
        }
        
        response = submit_form(client, '/search_log', form_data, method='POST')
        assert response.status_code == 200
        assert valid_order_data['title'] in response.data.decode('utf-8')
        
        # Step 4: Edit the order
        updated_data = order_data.copy()
        updated_data['title'] = 'Updated Journey Order Title'
        
        response = submit_form(client, f'/order/{valid_order_data["log"]}', updated_data)
        assert response.status_code == 200
        assert check_flash_message(response, f"Order {valid_order_data['log']} updated successfully")
        assert 'Updated Journey Order Title' in response.data.decode('utf-8')
        
        # Step 5: View due-outs
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        response = client.get('/dueouts')
        assert response.status_code == 200
        
        form_data = {
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': tomorrow.strftime('%Y-%m-%d')
        }
        
        response = submit_form(client, '/dueouts', form_data)
        assert response.status_code == 200
        assert 'Due Out' in response.data.decode('utf-8')
        
        # Step 6: Log out
        response = logout(client)
        assert response.status_code == 200
        assert 'Sign In' in response.data.decode('utf-8')
        
        # Verify we can't access protected pages after logout
        response = client.get('/', follow_redirects=True)
        assert 'Sign In' in response.data.decode('utf-8')