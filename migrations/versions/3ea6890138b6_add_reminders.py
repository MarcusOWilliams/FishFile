"""add reminders

Revision ID: 3ea6890138b6
Revises: 
Create Date: 2022-07-12 10:31:03.696249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ea6890138b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('project_license', sa.String(length=120), nullable=True),
    sa.Column('role', sa.String(length=32), nullable=True),
    sa.Column('code', sa.String(length=32), nullable=True),
    sa.Column('last_notification_read_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_code'), 'user', ['code'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=False)
    op.create_index(op.f('ix_user_project_license'), 'user', ['project_license'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table('fish',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fish_id', sa.String(length=32), nullable=True),
    sa.Column('tank_id', sa.String(length=32), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=True),
    sa.Column('stock', sa.String(length=32), nullable=True),
    sa.Column('source', sa.String(length=32), nullable=True),
    sa.Column('protocol', sa.Integer(), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('date_of_arrival', sa.Date(), nullable=True),
    sa.Column('allele', sa.String(length=64), nullable=True),
    sa.Column('mutant_gene', sa.String(length=64), nullable=True),
    sa.Column('transgenes', sa.String(length=64), nullable=True),
    sa.Column('cross_type', sa.String(length=64), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('father_id', sa.Integer(), nullable=True),
    sa.Column('mother_id', sa.Integer(), nullable=True),
    sa.Column('project_license_holder_id', sa.Integer(), nullable=True),
    sa.Column('user_code_id', sa.Integer(), nullable=True),
    sa.Column('males', sa.Integer(), nullable=True),
    sa.Column('females', sa.Integer(), nullable=True),
    sa.Column('unsexed', sa.Integer(), nullable=True),
    sa.Column('carriers', sa.Integer(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['father_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['mother_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['project_license_holder_id'], ['user.project_license'], ),
    sa.ForeignKeyConstraint(['user_code_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fish_allele'), 'fish', ['allele'], unique=False)
    op.create_index(op.f('ix_fish_birthday'), 'fish', ['birthday'], unique=False)
    op.create_index(op.f('ix_fish_cross_type'), 'fish', ['cross_type'], unique=False)
    op.create_index(op.f('ix_fish_date_of_arrival'), 'fish', ['date_of_arrival'], unique=False)
    op.create_index(op.f('ix_fish_fish_id'), 'fish', ['fish_id'], unique=False)
    op.create_index(op.f('ix_fish_mutant_gene'), 'fish', ['mutant_gene'], unique=False)
    op.create_index(op.f('ix_fish_protocol'), 'fish', ['protocol'], unique=False)
    op.create_index(op.f('ix_fish_status'), 'fish', ['status'], unique=False)
    op.create_index(op.f('ix_fish_stock'), 'fish', ['stock'], unique=False)
    op.create_index(op.f('ix_fish_tank_id'), 'fish', ['tank_id'], unique=False)
    op.create_index(op.f('ix_fish_transgenes'), 'fish', ['transgenes'], unique=False)
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('emails', sa.Boolean(), nullable=True),
    sa.Column('add_notifications', sa.Boolean(), nullable=True),
    sa.Column('change_notifications', sa.Boolean(), nullable=True),
    sa.Column('turnover_notifications', sa.Boolean(), nullable=True),
    sa.Column('age_notifications', sa.Boolean(), nullable=True),
    sa.Column('pl_add_notifications', sa.Boolean(), nullable=True),
    sa.Column('pl_turnover_notifications', sa.Boolean(), nullable=True),
    sa.Column('pl_age_notifications', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('fish_id', sa.Integer(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.Column('contents', sa.String(length=64), nullable=True),
    sa.Column('change_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fish_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reminder',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('fish_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('message', sa.String(length=64), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['fish_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('change',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('fish_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=True),
    sa.Column('contents', sa.String(length=64), nullable=True),
    sa.Column('field', sa.String(length=64), nullable=True),
    sa.Column('old', sa.String(length=64), nullable=True),
    sa.Column('new', sa.String(length=64), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('notification_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fish_id'], ['fish.id'], ),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('change')
    op.drop_table('reminder')
    op.drop_table('notification')
    op.drop_table('settings')
    op.drop_index(op.f('ix_fish_transgenes'), table_name='fish')
    op.drop_index(op.f('ix_fish_tank_id'), table_name='fish')
    op.drop_index(op.f('ix_fish_stock'), table_name='fish')
    op.drop_index(op.f('ix_fish_status'), table_name='fish')
    op.drop_index(op.f('ix_fish_protocol'), table_name='fish')
    op.drop_index(op.f('ix_fish_mutant_gene'), table_name='fish')
    op.drop_index(op.f('ix_fish_fish_id'), table_name='fish')
    op.drop_index(op.f('ix_fish_date_of_arrival'), table_name='fish')
    op.drop_index(op.f('ix_fish_cross_type'), table_name='fish')
    op.drop_index(op.f('ix_fish_birthday'), table_name='fish')
    op.drop_index(op.f('ix_fish_allele'), table_name='fish')
    op.drop_table('fish')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_project_license'), table_name='user')
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_code'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###