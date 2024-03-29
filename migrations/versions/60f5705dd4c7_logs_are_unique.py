"""Logs are unique

Revision ID: 60f5705dd4c7
Revises: 6f3ad2486e49
Create Date: 2023-05-19 12:44:08.465097

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '60f5705dd4c7'
down_revision = '6f3ad2486e49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['LOG'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Orders', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
