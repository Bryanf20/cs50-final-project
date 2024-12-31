"""Add assigned_to field to TaskProgress

Revision ID: 6ecfb95ae75f
Revises: 26efca9edf88
Create Date: 2024-12-19 07:43:30.774222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ecfb95ae75f'
down_revision = '26efca9edf88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_to', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('uq_taskprogress_assigned_to', 'user', ['assigned_to'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_progress', schema=None) as batch_op:
        batch_op.drop_constraint('uq_taskprogress_assigned_to', type_='foreignkey')
        batch_op.drop_column('assigned_to')

    # ### end Alembic commands ###