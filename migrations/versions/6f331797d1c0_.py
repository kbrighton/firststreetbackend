"""empty message

Revision ID: 6f331797d1c0
Revises: a8844ec5c76f
Create Date: 2023-04-14 11:05:18.149549

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6f331797d1c0'
down_revision = 'a8844ec5c76f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Customers',
    sa.Column('CUSTID', sa.String(length=255), nullable=True),
    sa.Column('Customer ID', sa.String(length=255), nullable=True),
    sa.Column('Customer', sa.String(length=255), nullable=True),
    sa.Column('Address Line 1', sa.String(length=255), nullable=True),
    sa.Column('Address Line 2', sa.String(length=255), nullable=True),
    sa.Column('City', sa.String(length=255), nullable=True),
    sa.Column('State', sa.String(length=255), nullable=True),
    sa.Column('Zip', sa.String(length=255), nullable=True),
    sa.Column('Bill To Contact', sa.String(length=255), nullable=True),
    sa.Column('Telephone 1', sa.String(length=255), nullable=True),
    sa.Column('Telephone 2', sa.String(length=255), nullable=True),
    sa.Column('Fax Number', sa.String(length=255), nullable=True),
    sa.Column('Tax ID', sa.String(length=255), nullable=True),
    sa.Column('Resale No', sa.String(length=255), nullable=True),
    sa.Column('Cust Since', sa.DateTime(timezone=True), nullable=True),
    sa.Column('Ship to 1 Address Line 1', sa.String(length=255), nullable=True),
    sa.Column('Ship to 1 Address Line 2', sa.String(length=255), nullable=True),
    sa.Column('Ship to 1 City ', sa.String(length=255), nullable=True),
    sa.Column('Ship to 1 State ', sa.String(length=255), nullable=True),
    sa.Column('Ship to 1 Zip ', sa.String(length=255), nullable=True),
    sa.Column('Customer E-mail', sa.String(length=255), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Orders',
    sa.Column('LOG', sa.String(length=7), nullable=True),
    sa.Column('CUST', sa.String(length=5), nullable=True),
    sa.Column('CUST_P_0', sa.String(length=8), nullable=True),
    sa.Column('PRIOR', sa.String(length=1), nullable=True),
    sa.Column('SHIPOUT', sa.String(length=5), nullable=True),
    sa.Column('HOWSHIP', sa.String(length=5), nullable=True),
    sa.Column('WEIGHT', sa.Float(precision=53), nullable=True),
    sa.Column('ARTLO', sa.String(length=5), nullable=True),
    sa.Column('DATIN', sa.Date(), nullable=True),
    sa.Column('ARTOUT', sa.DateTime(timezone=True), nullable=True),
    sa.Column('DUEOUT', sa.DateTime(timezone=True), nullable=True),
    sa.Column('LOGTYPE', sa.String(length=5), nullable=True),
    sa.Column('DATOUT', sa.DateTime(timezone=True), nullable=True),
    sa.Column('COLORF', sa.Float(precision=53), nullable=True),
    sa.Column('INKTYP', sa.Float(precision=53), nullable=True),
    sa.Column('COLORI', sa.Float(precision=53), nullable=True),
    sa.Column('PRINT_N', sa.Float(precision=53), nullable=True),
    sa.Column('RUSH_N', sa.Float(precision=53), nullable=True),
    sa.Column('COLORC_N', sa.Float(precision=53), nullable=True),
    sa.Column('GANG_N', sa.Float(precision=53), nullable=True),
    sa.Column('ARTC_N', sa.Float(precision=53), nullable=True),
    sa.Column('APPL_N', sa.Float(precision=53), nullable=True),
    sa.Column('ADHES_N', sa.Float(precision=53), nullable=True),
    sa.Column('LET_NU_N', sa.Float(precision=53), nullable=True),
    sa.Column('GARMNT_N', sa.Float(precision=53), nullable=True),
    sa.Column('PRINT_C', sa.Float(precision=53), nullable=True),
    sa.Column('RUSH_C', sa.Float(precision=53), nullable=True),
    sa.Column('COLORC_C', sa.Float(precision=53), nullable=True),
    sa.Column('GANG_C', sa.Float(precision=53), nullable=True),
    sa.Column('ARTC_C', sa.Float(precision=53), nullable=True),
    sa.Column('APPL_C', sa.Float(precision=53), nullable=True),
    sa.Column('ADHES_C', sa.Float(precision=53), nullable=True),
    sa.Column('LET_NU_C', sa.Float(precision=53), nullable=True),
    sa.Column('GARMNT_C', sa.Float(precision=53), nullable=True),
    sa.Column('PRINT_T', sa.Float(precision=53), nullable=True),
    sa.Column('RUSH_T', sa.Float(precision=53), nullable=True),
    sa.Column('COLORC_T', sa.Float(precision=53), nullable=True),
    sa.Column('GANG_T', sa.Float(precision=53), nullable=True),
    sa.Column('ARTC_T', sa.Float(precision=53), nullable=True),
    sa.Column('APPL_T', sa.Float(precision=53), nullable=True),
    sa.Column('ADHES_T', sa.Float(precision=53), nullable=True),
    sa.Column('LET_NU_T', sa.Float(precision=53), nullable=True),
    sa.Column('GARMNT_T', sa.Float(precision=53), nullable=True),
    sa.Column('SUBTOTAL', sa.Float(precision=53), nullable=True),
    sa.Column('SALES_TAX', sa.Float(precision=53), nullable=True),
    sa.Column('SHIP_FRGHT', sa.Float(precision=53), nullable=True),
    sa.Column('TOTAL', sa.Float(precision=53), nullable=True),
    sa.Column('ART_1', sa.String(length=5), nullable=True),
    sa.Column('ART_2', sa.String(length=5), nullable=True),
    sa.Column('ART_3', sa.String(length=5), nullable=True),
    sa.Column('ART_4', sa.String(length=5), nullable=True),
    sa.Column('ART_5', sa.String(length=5), nullable=True),
    sa.Column('ART_6', sa.String(length=5), nullable=True),
    sa.Column('ART_7', sa.String(length=5), nullable=True),
    sa.Column('ART_8', sa.String(length=5), nullable=True),
    sa.Column('ART_9', sa.String(length=5), nullable=True),
    sa.Column('PRINT_1', sa.String(length=5), nullable=True),
    sa.Column('PRINT_2', sa.String(length=5), nullable=True),
    sa.Column('PRINT_3', sa.String(length=5), nullable=True),
    sa.Column('PRINT_4', sa.String(length=5), nullable=True),
    sa.Column('PRINT_5', sa.String(length=5), nullable=True),
    sa.Column('PRINT_6', sa.String(length=5), nullable=True),
    sa.Column('PRINT_7', sa.String(length=5), nullable=True),
    sa.Column('PRINT_8', sa.String(length=5), nullable=True),
    sa.Column('PRINT_9', sa.String(length=5), nullable=True),
    sa.Column('A1', sa.Float(precision=53), nullable=True),
    sa.Column('A2', sa.Float(precision=53), nullable=True),
    sa.Column('A3', sa.Float(precision=53), nullable=True),
    sa.Column('A4', sa.Float(precision=53), nullable=True),
    sa.Column('A5', sa.Float(precision=53), nullable=True),
    sa.Column('A6', sa.Float(precision=53), nullable=True),
    sa.Column('A7', sa.Float(precision=53), nullable=True),
    sa.Column('A8', sa.Float(precision=53), nullable=True),
    sa.Column('A9', sa.Float(precision=53), nullable=True),
    sa.Column('P1', sa.Float(precision=53), nullable=True),
    sa.Column('P2', sa.Float(precision=53), nullable=True),
    sa.Column('P3', sa.Float(precision=53), nullable=True),
    sa.Column('P4', sa.Float(precision=53), nullable=True),
    sa.Column('P5', sa.Float(precision=53), nullable=True),
    sa.Column('P6', sa.Float(precision=53), nullable=True),
    sa.Column('P7', sa.Float(precision=53), nullable=True),
    sa.Column('P8', sa.Float(precision=53), nullable=True),
    sa.Column('P9', sa.Float(precision=53), nullable=True),
    sa.Column('TITLE', sa.String(length=48), nullable=True),
    sa.Column('LET_STYLE', sa.String(length=5), nullable=True),
    sa.Column('REF_ARTLO', sa.String(length=5), nullable=True),
    sa.Column('ARTPAG', sa.String(length=3), nullable=True),
    sa.Column('ARTNO', sa.String(length=5), nullable=True),
    sa.Column('ARTENCL', sa.String(length=1), nullable=True),
    sa.Column('RET_ART', sa.String(length=1), nullable=True),
    sa.Column('REORDER', sa.String(length=1), nullable=True),
    sa.Column('CUST_INFO', sa.String(length=95), nullable=True),
    sa.Column('LOCATE', sa.String(length=15), nullable=True),
    sa.Column('SET_1', sa.String(length=5), nullable=True),
    sa.Column('SET_2', sa.String(length=5), nullable=True),
    sa.Column('SET_3', sa.String(length=5), nullable=True),
    sa.Column('SET_4', sa.String(length=5), nullable=True),
    sa.Column('PCK_1', sa.String(length=5), nullable=True),
    sa.Column('PCK_2', sa.String(length=5), nullable=True),
    sa.Column('PCK_3', sa.String(length=5), nullable=True),
    sa.Column('PCK_4', sa.String(length=5), nullable=True),
    sa.Column('S1', sa.Float(precision=53), nullable=True),
    sa.Column('S2', sa.Float(precision=53), nullable=True),
    sa.Column('S3', sa.Float(precision=53), nullable=True),
    sa.Column('S4', sa.Float(precision=53), nullable=True),
    sa.Column('U1', sa.Float(precision=53), nullable=True),
    sa.Column('U2', sa.Float(precision=53), nullable=True),
    sa.Column('U3', sa.Float(precision=53), nullable=True),
    sa.Column('U4', sa.Float(precision=53), nullable=True),
    sa.Column('ARTD_1', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_2', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_3', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_4', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_5', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_6', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_7', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_8', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTD_9', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_1', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_2', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_3', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_4', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_5', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_6', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_7', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_8', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ARTO_9', sa.DateTime(timezone=True), nullable=True),
    sa.Column('LUPD', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ORIGPR', sa.String(length=1), nullable=True),
    sa.Column('RUSH', sa.Integer(), nullable=True),
    sa.Column('LATE', sa.Float(precision=53), nullable=True),
    sa.Column('TIMEOUT', sa.String(length=8), nullable=True),
    sa.Column('TIMEIN', sa.String(length=8), nullable=True),
    sa.Column('OUT', sa.Float(precision=53), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Orders')
    op.drop_table('Customers')
    # ### end Alembic commands ###
