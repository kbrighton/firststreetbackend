"""Identity Field

Revision ID: 6f3ad2486e49
Revises: 7e5e81bdc2e3
Create Date: 2023-05-19 12:11:34.609376

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6f3ad2486e49'
down_revision = '7e5e81bdc2e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.drop_column('id')

    # ### end Alembic commands ###
