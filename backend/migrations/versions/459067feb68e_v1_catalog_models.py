"""V1 catalog models

Revision ID: 459067feb68e
Revises: 348056fea57f
Create Date: 2026-09-12 11:50:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '459067feb68e'
down_revision: Union[str, None] = '348056fea57f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('genres',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_id'), 'genres', ['id'], unique=False)
    op.create_index(op.f('ix_genres_name'), 'genres', ['name'], unique=True)
    op.create_index(op.f('ix_genres_slug'), 'genres', ['slug'], unique=True)

    op.create_table('artists',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=2048), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artists_deleted_at'), 'artists', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_artists_id'), 'artists', ['id'], unique=False)
    op.create_index(op.f('ix_artists_name'), 'artists', ['name'], unique=False)

    op.create_table('albums',
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('artist_id', sa.UUID(), nullable=False),
        sa.Column('cover_url', sa.String(length=2048), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_albums_artist_id'), 'albums', ['artist_id'], unique=False)
    op.create_index(op.f('ix_albums_deleted_at'), 'albums', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_albums_id'), 'albums', ['id'], unique=False)
    op.create_index(op.f('ix_albums_title'), 'albums', ['title'], unique=False)

    op.create_table('songs',
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('artist_id', sa.UUID(), nullable=False),
        sa.Column('album_id', sa.UUID(), nullable=True),
        sa.Column('genre_id', sa.UUID(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('track_number', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('original_filename', sa.String(length=512), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('play_count', sa.BigInteger(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['album_id'], ['albums.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_songs_album_id'), 'songs', ['album_id'], unique=False)
    op.create_index(op.f('ix_songs_artist_id'), 'songs', ['artist_id'], unique=False)
    op.create_index(op.f('ix_songs_deleted_at'), 'songs', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_songs_genre_id'), 'songs', ['genre_id'], unique=False)
    op.create_index(op.f('ix_songs_id'), 'songs', ['id'], unique=False)
    op.create_index(op.f('ix_songs_title'), 'songs', ['title'], unique=False)

    op.create_table('song_audio_variants',
        sa.Column('song_id', sa.UUID(), nullable=False),
        sa.Column('quality', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('bitrate', sa.Integer(), nullable=False),
        sa.Column('codec', sa.String(length=50), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['song_id'], ['songs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_song_audio_variants_id'), 'song_audio_variants', ['id'], unique=False)
    op.create_index(op.f('ix_song_audio_variants_quality'), 'song_audio_variants', ['quality'], unique=False)
    op.create_index(op.f('ix_song_audio_variants_song_id'), 'song_audio_variants', ['song_id'], unique=False)
    op.create_index(op.f('ix_song_audio_variants_status'), 'song_audio_variants', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('song_audio_variants')
    op.drop_table('songs')
    op.drop_table('albums')
    op.drop_table('artists')
    op.drop_table('genres')
