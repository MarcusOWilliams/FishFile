"""add changes

Revision ID: b0d4b4f52fc7
Revises: 4b49434d2fd1
Create Date: 2022-06-18 14:49:43.072319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0d4b4f52fc7'
down_revision = '4b49434d2fd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('change',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('fish_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=True),
    sa.Column('contents', sa.String(length=64), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['fish_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('change')
    # ### end Alembic commands ###
