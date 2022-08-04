"""remove old stock

Revision ID: 1c3bb52048ba
Revises: 21bbc4d41c3d
Create Date: 2022-07-31 11:42:41.809700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c3bb52048ba'
down_revision = '21bbc4d41c3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fish', 'old_stock')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fish', sa.Column('old_stock', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    # ### end Alembic commands ###