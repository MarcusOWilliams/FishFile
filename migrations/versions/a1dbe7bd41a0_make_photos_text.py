"""make photos text

Revision ID: a1dbe7bd41a0
Revises: 33baf92cc43f
Create Date: 2022-07-20 16:20:01.802792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1dbe7bd41a0'
down_revision = '33baf92cc43f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fish', sa.Column('photos', sa.Text(), nullable=True))
    op.drop_column('fish', 'num_of_photos')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fish', sa.Column('num_of_photos', sa.INTEGER(), nullable=True))
    op.drop_column('fish', 'photos')
    # ### end Alembic commands ###
