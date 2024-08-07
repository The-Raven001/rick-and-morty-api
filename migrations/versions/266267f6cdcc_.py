"""empty message

Revision ID: 266267f6cdcc
Revises: 66ef0a6f0d63
Create Date: 2024-07-19 22:22:21.755796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '266267f6cdcc'
down_revision = '66ef0a6f0d63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=180),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=180),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###
