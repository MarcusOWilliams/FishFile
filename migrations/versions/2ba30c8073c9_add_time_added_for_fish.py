"""add time added for fish

Revision ID: 2ba30c8073c9
Revises: 08c795a58c65
Create Date: 2022-07-12 18:14:15.902323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ba30c8073c9'
down_revision = '08c795a58c65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fish', sa.Column('added', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fish', 'added')
    # ### end Alembic commands ###
