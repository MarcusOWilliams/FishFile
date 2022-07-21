"""add personal License

Revision ID: 7b3af6b607c8
Revises: bb1262520ba1
Create Date: 2022-07-21 12:59:57.284668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3af6b607c8'
down_revision = 'bb1262520ba1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('personal_license', sa.String(length=120), nullable=True))
    op.drop_index('ix_user_project_license', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_project_license', 'user', ['project_license'], unique=False)
    op.drop_column('user', 'personal_license')
    # ### end Alembic commands ###