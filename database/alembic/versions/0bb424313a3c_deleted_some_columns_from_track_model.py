"""Deleted some columns from track model

Revision ID: 0bb424313a3c
Revises: af2ce723522a
Create Date: 2023-07-31 20:11:49.151025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bb424313a3c'
down_revision = 'af2ce723522a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracks', 'in_favourite')
    op.drop_column('tracks', 'total_charts')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracks', sa.Column('total_charts', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('tracks', sa.Column('in_favourite', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
