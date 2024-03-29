"""Corrected Type

Revision ID: 7e5c5c581f29
Revises: 6f331797d1c0
Create Date: 2023-04-14 11:11:03.325429

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7e5c5c581f29'
down_revision = '6f331797d1c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.alter_column('RUSH',
               existing_type=sa.INTEGER(),
               type_=sa.Boolean(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.alter_column('RUSH',
               existing_type=sa.Boolean(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
