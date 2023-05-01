"""Updating Customers

Revision ID: f7045b045ccb
Revises: b0b54b597b1e
Create Date: 2023-04-28 19:27:49.935474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7045b045ccb'
down_revision = 'b0b54b597b1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.alter_column('CUSTID',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Customers_id_seq"\'::regclass)'), autoincrement=True, nullable=False))
        batch_op.alter_column('CUSTID',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###