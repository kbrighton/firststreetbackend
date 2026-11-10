import re

import pytest


@pytest.fixture
def csrf_app(app):
    app.config['WTF_CSRF_ENABLED'] = True
    yield app
    app.config['WTF_CSRF_ENABLED'] = False


@pytest.fixture
def csrf_client(csrf_app):
    return csrf_app.test_client()


def get_token(client):
    response = client.get('/api/auth/csrf')
    assert response.status_code == 200
    return response.get_json()['csrf_token']


def login(client, token):
    response = client.post(
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'password123'},
        headers={'X-CSRFToken': token},
    )
    assert response.status_code == 200


def test_api_write_without_token_returns_json_csrf_error(csrf_client, sample_user):
    response = csrf_client.post(
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'password123'},
    )

    assert response.status_code == 400
    assert response.is_json
    payload = response.get_json()
    assert payload['error'] == 'CSRF Error'
    assert payload['status'] == 400
    assert payload['message']


def test_api_write_with_invalid_token_is_rejected(csrf_client, sample_user):
    get_token(csrf_client)

    response = csrf_client.post(
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'password123'},
        headers={'X-CSRFToken': 'not-a-valid-token'},
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'CSRF Error'


def test_token_is_accepted_for_post_put_and_delete(csrf_client, sample_user, sample_order):
    token = get_token(csrf_client)
    login(csrf_client, token)
    token = get_token(csrf_client)

    put_response = csrf_client.put(
        f'/api/orders/{sample_order.id}',
        json={'title': 'Updated with token'},
        headers={'X-CSRFToken': token},
    )
    assert put_response.status_code == 200

    delete_response = csrf_client.delete(
        f'/api/orders/{sample_order.id}',
        headers={'X-CSRFToken': token},
    )
    assert delete_response.status_code == 204

    logout_response = csrf_client.post(
        '/api/auth/logout',
        headers={'X-CSRFToken': token},
    )
    assert logout_response.status_code == 200


def test_grid_page_token_allows_grid_update(csrf_client, sample_user, sample_order):
    login(csrf_client, get_token(csrf_client))

    page = csrf_client.get('/newsearch')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)
    assert match
    assert "'X-CSRFToken'" in html

    response = csrf_client.post(
        '/api/data',
        json={'id': sample_order.id, 'title': 'Grid edit'},
        headers={'X-CSRFToken': match.group(1)},
    )
    assert response.status_code == 204

    rejected = csrf_client.post(
        '/api/data',
        json={'id': sample_order.id, 'title': 'No token'},
    )
    assert rejected.status_code == 400


def test_login_form_renders_csrf_field_when_enabled(csrf_client):
    response = csrf_client.get('/auth/login')

    assert response.status_code == 200
    assert 'name="csrf_token"' in response.get_data(as_text=True)
