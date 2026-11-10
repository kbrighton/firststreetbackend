import json
import re
from pathlib import Path


def to_openapi_path(rule):
    return re.sub(r'<(?:[^:<>]+:)?([^<>]+)>', r'{\1}', rule)


def test_openapi_lists_every_api_route(client, app):
    response = client.get('/api/openapi.json')

    assert response.status_code == 200
    spec = response.get_json()
    assert spec['openapi'].startswith('3.')

    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/api/'):
            continue
        path = to_openapi_path(rule.rule)
        assert path in spec['paths'], path
        for method in rule.methods - {'HEAD', 'OPTIONS'}:
            assert method.lower() in spec['paths'][path], (path, method)


def test_openapi_documents_contracts_and_csrf(client):
    spec = client.get('/api/openapi.json').get_json()
    schemas = spec['components']['schemas']

    assert {'error', 'message', 'status', 'fields'} <= set(schemas['Error']['properties'])
    assert set(schemas['OrderList']['required']) == {'data', 'total', 'page', 'per_page', 'pages'}
    assert 'role' in schemas['User']['properties']
    assert 'password' not in schemas['User']['properties']
    assert {'log', 'cust', 'title', 'datin', 'logtype'} <= set(schemas['OrderInput']['required'])
    assert {'artno', 'created_by_username', 'updated_by_username'} <= set(
        schemas['OrderDetail']['properties']
    )
    assert 'artno' not in schemas['Order']['properties']

    csrf_scheme = spec['components']['securitySchemes']['csrfToken']
    assert csrf_scheme == {'type': 'apiKey', 'in': 'header', 'name': 'X-CSRFToken'}

    create_order = spec['paths']['/api/orders']['post']
    assert {'csrfToken': [], 'sessionCookie': []} in create_order['security']
    assert create_order['requestBody']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/OrderInput'
    }
    assert create_order['responses']['400']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/Error'
    }

    order_by_id = spec['paths']['/api/orders/{id}']['get']
    assert order_by_id['parameters'] == [
        {'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}
    ]
    assert order_by_id['responses']['200']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/OrderDetail'
    }

    list_orders = spec['paths']['/api/orders']['get']
    assert list_orders['responses']['200']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/OrderList'
    }

    dueouts = spec['paths']['/api/orders/dueouts']['get']
    assert dueouts['parameters'] == [
        {
            'name': 'start_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
        },
        {
            'name': 'end_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
        },
    ]


def test_generated_frontend_openapi_matches_login_and_dueout_contracts(client):
    api_spec = client.get('/api/openapi.json').get_json()
    frontend_spec_path = Path(__file__).resolve().parents[3] / 'frontend' / 'openapi.json'
    frontend_spec = json.loads(frontend_spec_path.read_text(encoding='utf-8'))

    assert frontend_spec['components']['schemas']['LoginRequest'] == (
        api_spec['components']['schemas']['LoginRequest']
    )
    assert frontend_spec['components']['schemas']['CurrentUser'] == (
        api_spec['components']['schemas']['CurrentUser']
    )
    assert set(frontend_spec['components']['schemas']['OrderDetail']['properties']) == set(
        api_spec['components']['schemas']['OrderDetail']['properties']
    )
    assert frontend_spec['components']['schemas']['OrderInput']['properties']['logtype']['enum'] == (
        api_spec['components']['schemas']['OrderInput']['properties']['logtype']['enum']
    )
    for path in ('/api/orders/{id}', '/api/orders/log/{log_id}'):
        assert frontend_spec['paths'][path]['get']['responses']['200']['content']['application/json']['schema'] == (
            api_spec['paths'][path]['get']['responses']['200']['content']['application/json']['schema']
        )
    assert frontend_spec['paths']['/api/orders/dueouts']['get']['parameters'] == (
        api_spec['paths']['/api/orders/dueouts']['get']['parameters']
    )
