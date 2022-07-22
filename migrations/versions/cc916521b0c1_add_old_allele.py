"""add old_allele

Revision ID: cc916521b0c1
Revises: 0979a17f743f
Create Date: 2022-07-22 17:25:49.667626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc916521b0c1'
down_revision = '0979a17f743f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fish', sa.Column('old_allele', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fish', 'old_allele')
    # ### end Alembic commands ###
