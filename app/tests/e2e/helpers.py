"""
Helper functions for end-to-end tests.

This module provides utility functions for common operations in end-to-end tests,
such as logging in and out, submitting forms, and checking for specific content
in responses.
"""

from typing import Dict, Any, Optional
from flask.testing import FlaskClient
from bs4 import BeautifulSoup


def login(client: FlaskClient, username: str, password: str, remember: bool = False) -> None:
    """
    Log in a user through the web UI.

    Args:
        client: The Flask test client.
        username: The username to log in with.
        password: The password to log in with.
        remember: Whether to check the "Remember Me" option.

    Returns:
        None
    """
    response = client.get('/auth/login')
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Extract CSRF token from the form
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    return client.post(
        '/auth/login',
        data={
            'username': username,
            'password': password,
            'remember_me': remember,
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )


def logout(client: FlaskClient) -> None:
    """
    Log out a user through the web UI.

    Args:
        client: The Flask test client.

    Returns:
        None
    """
    return client.get('/auth/logout', follow_redirects=True)


def get_csrf_token(response_data: bytes) -> str:
    """
    Extract CSRF token from an HTML response.

    Args:
        response_data: The HTML response data.

    Returns:
        The CSRF token.
    """
    soup = BeautifulSoup(response_data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    if csrf_token:
        return csrf_token['value']
    return ''


def submit_form(client: FlaskClient, url: str, form_data: Dict[str, Any], 
                method: str = 'POST', follow_redirects: bool = True) -> Any:
    """
    Submit a form with CSRF token.

    Args:
        client: The Flask test client.
        url: The URL to submit the form to.
        form_data: The form data to submit.
        method: The HTTP method to use (GET or POST).
        follow_redirects: Whether to follow redirects.

    Returns:
        The response from the form submission.
    """
    # Get the form page to extract the CSRF token
    response = client.get(url)
    csrf_token = get_csrf_token(response.data)
    
    # Add CSRF token to form data
    form_data['csrf_token'] = csrf_token
    
    # Submit the form
    if method.upper() == 'POST':
        return client.post(url, data=form_data, follow_redirects=follow_redirects)
    else:
        return client.get(url, query_string=form_data, follow_redirects=follow_redirects)


def check_content(response: Any, expected_content: str) -> bool:
    """
    Check if a response contains expected content.

    Args:
        response: The response to check.
        expected_content: The content to look for.

    Returns:
        True if the content is found, False otherwise.
    """
    return expected_content in response.data.decode('utf-8')


def check_flash_message(response: Any, message: str) -> bool:
    """
    Check if a flash message is present in the response.

    Args:
        response: The response to check.
        message: The flash message to look for.

    Returns:
        True if the flash message is found, False otherwise.
    """
    soup = BeautifulSoup(response.data, 'html.parser')
    flash_messages = soup.find_all(class_='flash-message')
    
    for flash in flash_messages:
        if message in flash.text:
            return True
    
    return False