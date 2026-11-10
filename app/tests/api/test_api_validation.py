from datetime import date, timedelta

import pytest
from werkzeug.datastructures import MultiDict

from app.auth.forms import LoginForm
from app.main.forms import DisplayDueouts, OrderForm, SearchForm, SearchLog, UserForm
from app.models import User


def login(client, username='testuser', password='password123'):
    response = client.post(
        '/api/auth/login',
        json={'username': username, 'password': password},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(('field', 'value'), [
    ('username', 'ab'),
    ('username', 'a@b'),
    ('username', 'x' * 65),
    ('password', 'short'),
    ('password', ''),
])
def test_login_field_errors_match_login_form(client, app, field, value):
    payload = {'username': 'validname', 'password': 'validpass123'}
    payload[field] = value
    with app.test_request_context('/login'):
        form = LoginForm(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = {field: form.errors[field]}

    response = client.post('/api/auth/login', json=payload)

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


@pytest.fixture
def admin_user(db_session):
    user = User(
        username='validationadmin',
        email='validationadmin@example.com',
        role='admin',
    )
    user.set_password('adminpass123')
    db_session.add(user)
    db_session.commit()
    return user


def test_invalid_order_fields_match_order_form_errors(client, app, sample_user):
    payload = {
        'log': '123',
        'cust': 'abc!',
        'title': '',
        'datin': '',
        'logtype': 'INVALID',
    }
    with app.test_request_context('/api/orders'):
        form = OrderForm(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.post('/api/orders', json=payload)

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Validation Error'
    assert response.get_json()['fields'] == expected_errors


@pytest.mark.parametrize(('field', 'value'), [
    ('log', 'abc!d'),
    ('cust', 'abc!d'),
    ('title', 'x' * 101),
    ('artout', 'not-a-date'),
    ('dueout', 'not-a-date'),
    ('print_n', 'not-an-integer'),
    ('print_n', 0),
    ('artlo', 'x' * 21),
    ('artlo', 'invalid!'),
    ('prior', 11),
    ('logtype', 'INVALID'),
    ('colorf', -1),
    ('ref_artlo', 'abc'),
    ('ref_artlo', 'abc!e'),
    ('howship', 0),
    ('artno', 'abc'),
    ('artno', 'abc!'),
    ('datout', 'not-a-date'),
])
def test_order_field_errors_match_order_form_validators(
    client, app, sample_user, field, value
):
    payload = {
        'log': '12345',
        'cust': '54321',
        'title': 'Valid order title',
        'datin': date.today().isoformat(),
        'logtype': 'TR',
    }
    payload[field] = value
    with app.test_request_context('/api/orders'):
        form = OrderForm(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.post('/api/orders', json=payload)

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


def test_order_update_validates_only_submitted_fields(client, sample_user, sample_order):
    login(client)

    valid_response = client.put(
        f'/api/orders/{sample_order.id}',
        json={'title': 'Updated with partial payload'},
    )
    assert valid_response.status_code == 200

    invalid_response = client.put(
        f'/api/orders/{sample_order.id}',
        json={'print_n': 0},
    )
    assert invalid_response.status_code == 400
    assert invalid_response.get_json()['fields'] == {
        'print_n': ['Quantity must be a positive number'],
    }


def test_order_api_accepts_digital_graphics_option_from_order_form(
    client, sample_user, valid_order_data
):
    login(client)
    payload = valid_order_data.copy()
    payload.update({
        'log': 'DG001',
        'logtype': 'DG',
        'datin': payload['datin'].isoformat(),
    })
    if payload.get('dueout'):
        payload['dueout'] = payload['dueout'].isoformat()

    response = client.post('/api/orders', json=payload)

    assert response.status_code == 201
    assert response.get_json()['logtype'] == 'DG'


def test_order_search_requires_at_least_one_search_field(client, sample_user):
    login(client)

    response = client.get('/api/orders')

    assert response.status_code == 400
    assert response.get_json()['fields'] == {
        'cust': ['At least one search field is required'],
    }


def test_order_search_returns_paginated_envelope(client, sample_user, sample_order):
    login(client)

    response = client.get(
        '/api/orders',
        query_string={
            'cust': sample_order.cust,
            'page': 1,
            'per_page': 1,
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload) == {'data', 'total', 'page', 'per_page', 'pages'}
    assert payload['total'] == 1
    assert payload['page'] == 1
    assert payload['per_page'] == 1
    assert payload['pages'] == 1
    assert payload['data'][0]['log'] == sample_order.log


def test_order_search_preserves_allowlisted_sorting(
    client, sample_user, sample_customer, order_factory
):
    order_factory(cust=sample_customer.cust_id, log='73002', title='Sort target')
    order_factory(cust=sample_customer.cust_id, log='73001', title='Sort target')
    login(client)

    response = client.get(
        '/api/orders',
        query_string={
            'cust': sample_customer.cust_id,
            'title': 'Sort target',
            'sort': '+log',
        },
    )

    assert response.status_code == 200
    assert [row['log'] for row in response.get_json()['data']] == ['73001', '73002']


def test_invalid_log_matches_search_log_form_errors(client, app, sample_user):
    with app.test_request_context('/search_log'):
        form = SearchLog(formdata=MultiDict({'log': 'abc'}))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.get('/api/orders/log/abc')

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


@pytest.mark.parametrize('log', ['abc', 'ab!de'])
def test_log_validation_matches_search_log_form(client, app, sample_user, log):
    with app.test_request_context('/search_log'):
        form = SearchLog(formdata=MultiDict({'log': log}))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.get(f'/api/orders/log/{log}')

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


def test_dueout_date_range_validation_matches_form(client, app, sample_user):
    start = date.today() + timedelta(days=2)
    end = date.today()
    payload = {
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
    }
    with app.test_request_context('/dueouts'):
        form = DisplayDueouts(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.get('/api/orders/dueouts', query_string=payload)

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


def test_dueout_dates_are_optional_but_must_be_provided_as_a_pair(client, sample_user):
    login(client)

    all_dueouts = client.get('/api/orders/dueouts')
    assert all_dueouts.status_code == 200
    assert isinstance(all_dueouts.get_json(), list)

    one_date = client.get(
        '/api/orders/dueouts',
        query_string={'start_date': date.today().isoformat()},
    )
    assert one_date.status_code == 400
    assert one_date.get_json()['fields'] == {'end_date': ['End date is required']}

    other_date = client.get(
        '/api/orders/dueouts',
        query_string={'end_date': date.today().isoformat()},
    )
    assert other_date.status_code == 400
    assert other_date.get_json()['fields'] == {'start_date': ['Start date is required']}


def test_invalid_user_fields_match_user_form_errors(client, app, admin_user):
    payload = {
        'username': 'a@',
        'email': 'valid@example.com',
        'password': 'short',
        'role': 'user',
    }
    with app.test_request_context('/api/users'):
        form = UserForm(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = form.errors

    login(client, 'validationadmin', 'adminpass123')
    response = client.post('/api/users', json=payload)

    assert response.status_code == 400
    assert response.get_json()['fields'] == {
        field: errors for field, errors in expected_errors.items()
        if field in {'username', 'password'}
    }


@pytest.mark.parametrize(('field', 'value'), [
    ('username', 'ab'),
    ('username', 'a@b'),
    ('username', 'x' * 65),
    ('email', 'a' * 110 + '@example.com'),
    ('password', 'short'),
])
def test_user_field_errors_match_user_form_validators(
    client, app, admin_user, field, value
):
    payload = {
        'username': 'validname',
        'email': 'valid@example.com',
        'password': 'validpass123',
        'role': 'user',
    }
    payload[field] = value
    with app.test_request_context('/api/users'):
        form = UserForm(formdata=MultiDict(payload))
        assert not form.validate()
        expected_errors = {
            name: errors for name, errors in form.errors.items()
            if name in {'username', 'email', 'password'}
        }

    login(client, 'validationadmin', 'adminpass123')
    response = client.post('/api/users', json=payload)

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


@pytest.mark.parametrize(('field', 'value'), [
    ('cust', '123456'),
    ('cust', 'ab!de'),
    ('title', 'x' * 101),
])
def test_search_field_errors_match_search_form_validators(
    client, app, sample_user, field, value
):
    params = {'cust': '12345', 'title': ''}
    params[field] = value
    with app.test_request_context('/search'):
        form = SearchForm(formdata=MultiDict(params))
        assert not form.validate()
        expected_errors = form.errors

    login(client)
    response = client.get('/api/orders', query_string=params)

    assert response.status_code == 400
    assert response.get_json()['fields'] == expected_errors


def test_search_whitespace_matches_optional_form_behavior(client, app, sample_user):
    params = {'cust': '   ', 'title': ''}
    with app.test_request_context('/search'):
        form = SearchForm(formdata=MultiDict(params))
        assert form.validate()

    login(client)
    response = client.get('/api/orders', query_string=params)

    assert response.status_code == 200


def test_user_role_validation_and_serialization(client, admin_user):
    login(client, 'validationadmin', 'adminpass123')

    invalid_response = client.post(
        '/api/users',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'superadmin',
        },
    )
    assert invalid_response.status_code == 400
    assert invalid_response.get_json()['fields'] == {
        'role': ['Role must be one of: user, admin'],
    }

    valid_response = client.post(
        '/api/users',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'admin',
        },
    )
    assert valid_response.status_code == 201
    user_data = valid_response.get_json()
    assert user_data['role'] == 'admin'
    assert 'password' not in user_data
    assert 'password_hash' not in user_data


def test_user_creation_requires_password(client, admin_user):
    login(client, 'validationadmin', 'adminpass123')

    response = client.post(
        '/api/users',
        json={'username': 'newuser', 'email': 'newuser@example.com'},
    )

    assert response.status_code == 400
    assert response.get_json()['fields'] == {
        'password': ['This field is required.'],
    }


def test_regular_user_cannot_set_role(client, sample_user):
    login(client)

    response = client.put(
        f'/api/users/{sample_user.id}',
        json={'role': 'admin'},
    )

    assert response.status_code == 403
    assert response.get_json()['error'] == 'Forbidden'
