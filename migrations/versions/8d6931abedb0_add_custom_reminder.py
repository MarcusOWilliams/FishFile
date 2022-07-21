"""add custom reminder

Revision ID: 8d6931abedb0
Revises: a004d83099f5
Create Date: 2022-07-21 16:30:28.590207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d6931abedb0'
down_revision = 'a004d83099f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('custom_reminder', sa.Boolean(), nullable=True))
    op.add_column('settings', sa.Column('pl_custom_reminder', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'pl_custom_reminder')
    op.drop_column('settings', 'custom_reminder')
    # ### end Alembic commands ###
