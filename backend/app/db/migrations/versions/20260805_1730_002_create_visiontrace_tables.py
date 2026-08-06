"""Create roles, videos, frames, objects, embeddings, search_history, and reports tables with pgvector integration

Revision ID: 002
Revises: 001
Create Date: 2026-08-05 17:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database schema to VisionTrace AI complete architecture.
    """
    bind = op.get_bind()
    
    # 1. Enable pgvector and pg_trgm extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # 2. Create ENUM Types
    video_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='videostatus', create_type=False)
    video_status_enum.create(bind, checkfirst=True)
    
    search_type_enum = postgresql.ENUM('text', 'image', 'hybrid', 'metadata', name='searchtype', create_type=False)
    search_type_enum.create(bind, checkfirst=True)
    
    report_status_enum = postgresql.ENUM('draft', 'generating', 'completed', 'archived', name='reportstatus', create_type=False)
    report_status_enum.create(bind, checkfirst=True)
    
    # 3. Create ROLES Table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Seed default roles
    op.execute("""
        INSERT INTO roles (name, display_name, description, permissions)
        VALUES 
            ('admin', 'Administrator', 'Full system control, user management, and system configuration', '{"system": ["*"], "videos": ["*"], "reports": ["*"], "users": ["*"]}'::jsonb),
            ('investigator', 'Investigator', 'Can upload videos, perform AI searches, and generate investigative reports', '{"videos": ["create", "read", "update", "delete"], "search": ["*"], "reports": ["*"]}'::jsonb),
            ('viewer', 'Viewer', 'Read-only access to assigned surveillance videos and search results', '{"videos": ["read"], "search": ["read"], "reports": ["read"]}'::jsonb)
        ON CONFLICT (name) DO NOTHING;
    """)
    
    # 4. Add role_id foreign key column to USERS table
    op.add_column('users', sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True))
    op.create_index('ix_users_role_id', 'users', ['role_id'], unique=False)
    
    # Link existing users to default roles
    op.execute("""
        UPDATE users SET role_id = roles.id 
        FROM roles WHERE LOWER(users.role::text) = LOWER(roles.name) AND users.role_id IS NULL;
    """)
    
    # 5. Create VIDEOS Table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=False, server_default='video/mp4'),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('total_frames', sa.Integer(), nullable=True),
        sa.Column('status', video_status_enum, nullable=False, server_default='pending', index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_videos_created_at', 'videos', ['created_at'], unique=False)
    
    # 6. Create FRAMES Table
    op.create_table(
        'frames',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('frame_number', sa.Integer(), nullable=False),
        sa.Column('timestamp_seconds', sa.Float(), nullable=False),
        sa.Column('image_path', sa.String(512), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_frames_video_timestamp', 'frames', ['video_id', 'timestamp_seconds'], unique=False)
    op.create_index('ix_frames_video_frame_number', 'frames', ['video_id', 'frame_number'], unique=False)
    
    # 7. Create OBJECTS Table
    op.create_table(
        'objects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('frame_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frames.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('track_id', sa.Integer(), nullable=True, index=True),
        sa.Column('label', sa.String(100), nullable=False, index=True),
        sa.Column('confidence', sa.Float(), nullable=False, index=True),
        sa.Column('bounding_box', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('crop_path', sa.String(512), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_objects_label_confidence', 'objects', ['label', 'confidence'], unique=False)
    op.create_index('ix_objects_video_track', 'objects', ['video_id', 'track_id'], unique=False)
    
    # 8. Create EMBEDDINGS Table (with pgvector column)
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('frame_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frames.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('object_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('objects.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('model_name', sa.String(100), nullable=False, server_default='CLIP-ViT-B/32', index=True),
        sa.Column('dimension', sa.Integer(), nullable=False, server_default='512'),
        sa.Column('embedding', Vector(512), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # HNSW Vector cosine distance index
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_embeddings_vector_hnsw 
        ON embeddings USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    
    # 9. Create SEARCH_HISTORY Table
    op.create_table(
        'search_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('query_text', sa.Text(), nullable=True),
        sa.Column('query_image_path', sa.String(512), nullable=True),
        sa.Column('search_type', search_type_enum, nullable=False, server_default='text', index=True),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('result_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('execution_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_search_history_user_created', 'search_history', ['user_id', 'created_at'], unique=False)
    
    # 10. Create REPORTS Table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.String(50), nullable=False, server_default='investigation', index=True),
        sa.Column('status', report_status_enum, nullable=False, server_default='draft', index=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('file_path', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # 11. Triggers for updated_at
    tables = ['roles', 'videos', 'frames', 'objects', 'embeddings', 'search_history', 'reports']
    for table in tables:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """
    Downgrade database schema (drop tables in reverse dependency order).
    """
    tables = ['reports', 'search_history', 'embeddings', 'objects', 'frames', 'videos', 'roles']
    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")
    
    op.drop_index('ix_embeddings_vector_hnsw', table_name='embeddings', if_exists=True)
    op.drop_table('reports')
    op.drop_table('search_history')
    op.drop_table('embeddings')
    op.drop_table('objects')
    op.drop_table('frames')
    op.drop_table('videos')
    
    op.drop_index('ix_users_role_id', table_name='users', if_exists=True)
    op.drop_column('users', 'role_id')
    op.drop_table('roles')
    
    bind = op.get_bind()
    report_status_enum = postgresql.ENUM('draft', 'generating', 'completed', 'archived', name='reportstatus')
    report_status_enum.drop(bind, checkfirst=True)
    
    search_type_enum = postgresql.ENUM('text', 'image', 'hybrid', 'metadata', name='searchtype')
    search_type_enum.drop(bind, checkfirst=True)
    
    video_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='videostatus')
    video_status_enum.drop(bind, checkfirst=True)
