"""add transgenes as seperate table

Revision ID: b097367ca68d
Revises: cacded29a323
Create Date: 2022-08-05 12:52:54.458376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b097367ca68d'
down_revision = 'cacded29a323'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transgene',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fish_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('unidentified', sa.Boolean(), nullable=True),
    sa.Column('identified', sa.Boolean(), nullable=True),
    sa.Column('homozygous', sa.Boolean(), nullable=True),
    sa.Column('heterozygous', sa.Boolean(), nullable=True),
    sa.Column('hemizygous', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['fish_id'], ['fish.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transgene')
    # ### end Alembic commands ###