"""update notification to icon

Revision ID: 4778d57220a0
Revises: 78746c9fbb1f
Create Date: 2022-07-08 09:29:05.317524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4778d57220a0'
down_revision = '78746c9fbb1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification_icon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('payload_json', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_icon_name'), 'notification_icon', ['name'], unique=False)
    op.create_index(op.f('ix_notification_icon_time'), 'notification_icon', ['time'], unique=False)
    op.create_index(op.f('ix_notification_icon_timestamp'), 'notification_icon', ['timestamp'], unique=False)
    op.add_column('fish', sa.Column('last_notification_read_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fish', 'last_notification_read_time')
    op.drop_index(op.f('ix_notification_icon_timestamp'), table_name='notification_icon')
    op.drop_index(op.f('ix_notification_icon_time'), table_name='notification_icon')
    op.drop_index(op.f('ix_notification_icon_name'), table_name='notification_icon')
    op.drop_table('notification_icon')
    # ### end Alembic commands ###
