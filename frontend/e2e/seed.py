import os
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def require_scratch_sqlite(database_uri):
    if not database_uri.startswith('sqlite:///') or database_uri == 'sqlite:///:memory:':
        raise RuntimeError('E2E seeding requires a scratch SQLite database')

    database_path = Path(database_uri.removeprefix('sqlite:///'))
    scratch_directory = Path(tempfile.gettempdir()).resolve()
    resolved_path = database_path.resolve()
    try:
        resolved_path.relative_to(scratch_directory)
    except ValueError as error:
        raise RuntimeError('E2E seeding is restricted to the system temporary directory') from error
    if resolved_path.name != 'e2e.sqlite' or not resolved_path.parent.name.startswith('firststreet-e2e-'):
        raise RuntimeError('E2E seeding requires the Playwright scratch database path')


if not os.environ.get('DEV_DATABASE_URL'):
    raise RuntimeError('DEV_DATABASE_URL must point to a Playwright scratch database')

from app import create_app
from app.extensions import db
from app.models.order import Order
from app.models.user import User


app = create_app('development')
require_scratch_sqlite(app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()
    users = {}
    for username, role in (('smokeuser', 'user'), ('smokeadmin', 'admin')):
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(
                username=username,
                email=f'{username}@example.com',
                role=role,
                created_at=datetime(2025, 1, 1, 12, 0),
                updated_at=datetime(2025, 1, 1, 12, 0),
            )
            user.set_password('SmokePass123')
            db.session.add(user)
    db.session.commit()

    users['smokeuser'] = User.query.filter_by(username='smokeuser').one()
    if Order.query.filter_by(log='E2001').first() is None:
        start = date(2099, 12, 10)
        end = date(2099, 12, 11)
        for index in range(25):
            if index == 0:
                dueout, logtype, datout = start, 'TR', None
            elif index == 1:
                dueout, logtype, datout = end, 'DP', None
            elif index == 2:
                dueout, logtype, datout = start - timedelta(days=1), 'TR', None
            elif index == 3:
                dueout, logtype, datout = end + timedelta(days=1), 'TR', None
            elif index == 4:
                dueout, logtype, datout = start, 'TR', start
            elif index == 5:
                dueout, logtype, datout = start, 'VG', None
            else:
                dueout, logtype, datout = start + timedelta(days=30 + index), 'TR', None

            db.session.add(Order(
                log=f'E{2001 + index:04d}',
                cust='E2E01',
                title=f'E2E Search {index + 1:02d}',
                datin=date(2025, 1, 1) + timedelta(days=index),
                dueout=dueout,
                datout=datout,
                logtype=logtype,
                created_at=datetime(2025, 1, 1, 12, 0),
                updated_at=datetime(2025, 1, 1, 12, 0),
                artlo=f'A{index + 1:04d}',
                prior=str(index % 9 + 1),
                print_n=100 + index,
                colorf=2,
                rush=index % 2 == 0,
                created_by_id=users['smokeuser'].id,
                updated_by_id=users['smokeuser'].id,
            ))

        db.session.add(Order(
            log='DEL01',
            cust='E2E01',
            title='E2E Search deleted',
            datin=date(2025, 1, 1),
            dueout=start,
            logtype='TR',
            deleted_at=datetime(2025, 1, 1),
            created_by_id=users['smokeuser'].id,
            updated_by_id=users['smokeuser'].id,
        ))
        db.session.commit()
