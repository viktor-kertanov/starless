"""Youtube model, Playlist model created

Revision ID: 2bb10d4f674f
Revises: 0bb424313a3c
Create Date: 2023-08-04 21:01:56.483896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bb10d4f674f'
down_revision = '0bb424313a3c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('playlists',
    sa.Column('track_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('modified', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youtube_trackmatch',
    sa.Column('track_id', sa.UUID(), nullable=False),
    sa.Column('idx_in_search', sa.Integer(), nullable=True),
    sa.Column('yt_video_id', sa.String(length=64), nullable=False),
    sa.Column('yt_metadata', sa.String(), nullable=False),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('yt_category', sa.Integer(), nullable=True),
    sa.Column('match_rate', sa.Float(), nullable=True),
    sa.Column('channel_id', sa.String(length=64), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('modified', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('yt_metadata')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('youtube_trackmatch')
    op.drop_table('playlists')
    # ### end Alembic commands ###