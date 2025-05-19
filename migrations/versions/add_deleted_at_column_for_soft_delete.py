"""Add deleted_at column for soft delete functionality

Revision ID: add_deleted_at_column
Revises: 44dc8fb4ef7f
Create Date: 2025-05-17 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_deleted_at_column'
down_revision = '44dc8fb4ef7f'
branch_labels = None
depends_on = None


def upgrade():
    # Add deleted_at column to Customers table
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # Add deleted_at column to Orders table
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # Add deleted_at column to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove deleted_at column from Customers table
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')

    # Remove deleted_at column from Orders table
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')

    # Remove deleted_at column from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')