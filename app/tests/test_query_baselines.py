"""Repeatable query and latency baselines for representative order workflows."""

import json
from datetime import date, datetime, timedelta
from time import perf_counter
from typing import Any

import pytest
from sqlalchemy import event, insert

from app.extensions import db
from app.models.order import Order


DATASET_SIZE = 500
PAGE_SIZE = 20


def _seed_orders(customer_id):
    today = date.today()
    rows = []
    for index in range(DATASET_SIZE):
        rows.append({
            'log': f'B{index:06d}',
            'cust': customer_id,
            'title': f'Benchmark order {index:06d}',
            'datin': today,
            'dueout': today + timedelta(days=index % 15),
            'logtype': 'TR' if index % 2 == 0 else 'VG',
            'datout': today if index % 5 == 0 else None,
            'deleted_at': datetime.now() if index % 17 == 0 else None,
        })

    db.session.execute(insert(Order), rows)
    db.session.commit()


def _capture_request(client, path):
    statements = []

    def capture_statement(_connection, _cursor, statement, parameters, _context, _executemany):
        statements.append((statement, parameters))

    with client.application.app_context():
        event.listen(db.engine, 'before_cursor_execute', capture_statement)
        started = perf_counter()
        try:
            response = client.get(path)
        finally:
            elapsed_ms = (perf_counter() - started) * 1000
            event.remove(db.engine, 'before_cursor_execute', capture_statement)

    return response, elapsed_ms, statements


def _query_plans(statements, app):
    plans = []

    with app.app_context():
        dialect = db.engine.dialect.name
        explain_prefix = 'EXPLAIN QUERY PLAN' if dialect == 'sqlite' else 'EXPLAIN'
        with db.engine.connect() as connection:
            for statement, parameters in statements:
                if not statement.lstrip().upper().startswith('SELECT'):
                    continue
                if 'ORDERS' not in statement.upper():
                    continue

                rows = connection.exec_driver_sql(
                    f'{explain_prefix} {statement}', parameters
                ).all()
                plans.append({
                    'sql': statement,
                    'plan': [str(row) for row in rows],
                })

    return plans


@pytest.mark.performance
def test_order_workflow_query_baselines(
    client, sample_user, sample_customer
):
    """Print repeatable baselines without imposing machine-specific thresholds."""
    _seed_orders(sample_customer.cust_id)
    with client.session_transaction() as session:
        session['_user_id'] = str(sample_user.id)
        session['_fresh'] = True

    expected_active = sum(index % 17 != 0 for index in range(DATASET_SIZE))
    expected_dueouts = sum(
        index % 2 == 0 and index % 5 != 0 and index % 17 != 0
        for index in range(DATASET_SIZE)
    )
    scenarios = [
        ('/api/data?start=0&length=25', 'legacy_data'),
        (
            f'/order_search/?cust={sample_customer.cust_id}&title=Benchmark&page=1',
            'paginated_search',
        ),
        (
            f'/api/orders/dueouts?start_date={date.today():%Y-%m-%d}'
            f'&end_date={(date.today() + timedelta(days=14)):%Y-%m-%d}',
            'dueouts',
        ),
    ]
    with client.application.app_context():
        report: dict[str, Any] = {
            'dataset_size': DATASET_SIZE,
            'database_engine': db.engine.dialect.name,
            'database_url': client.application.config['SQLALCHEMY_DATABASE_URI'],
            'scenarios': {},
        }

    for path, name in scenarios:
        response, elapsed_ms, statements = _capture_request(client, path)
        assert response.status_code == 200
        expected_query_count = {
            'legacy_data': 3,
            'paginated_search': 3,
            'dueouts': 2,
        }[name]
        assert len(statements) <= expected_query_count

        if name == 'legacy_data':
            payload = response.get_json()
            row_count = len(payload['data'])
            assert row_count == 25
            assert payload['total'] == expected_active
        elif name == 'paginated_search':
            body = response.get_data(as_text=True)
            expected_page_logs = [
                f'B{index:06d}'
                for index in range(DATASET_SIZE - 1, -1, -1)
                if index % 17 != 0
            ][:PAGE_SIZE]
            row_count = sum(log in body for log in expected_page_logs)
            assert row_count == PAGE_SIZE
        else:
            row_count = len(response.get_json())
            assert row_count == expected_dueouts

        report['scenarios'][name] = {
            'latency_ms': round(elapsed_ms, 3),
            'query_count': len(statements),
            'row_count': row_count,
            'query_plans': _query_plans(statements, client.application),
        }

    print(json.dumps(report, indent=2, sort_keys=True))
