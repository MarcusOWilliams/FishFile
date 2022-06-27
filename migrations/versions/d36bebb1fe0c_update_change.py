"""update Change

Revision ID: d36bebb1fe0c
Revises: 38a04bd6af27
Create Date: 2022-06-27 10:00:14.918033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd36bebb1fe0c'
down_revision = '38a04bd6af27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('change', sa.Column('old', sa.String(length=64), nullable=True))
    op.add_column('change', sa.Column('new', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('change', 'new')
    op.drop_column('change', 'old')
    # ### end Alembic commands ###
