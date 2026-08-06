-- =============================================================================
-- VisionTrace AI - Full PostgreSQL Database Schema Migration DDL
-- Database Engine: PostgreSQL 15+ with pgvector extension
-- Target Architecture: Surveillance Video Analytics & AI Vector Search
-- =============================================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- -----------------------------------------------------------------------------
-- ENUM TYPES
-- -----------------------------------------------------------------------------

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('admin', 'investigator', 'viewer');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'videostatus') THEN
        CREATE TYPE videostatus AS ENUM ('pending', 'processing', 'completed', 'failed');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'searchtype') THEN
        CREATE TYPE searchtype AS ENUM ('text', 'image', 'hybrid', 'metadata');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reportstatus') THEN
        CREATE TYPE reportstatus AS ENUM ('draft', 'generating', 'completed', 'archived');
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- TRIGGER FUNCTION FOR UPDATED_AT
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- =============================================================================
-- TABLE 1: ROLES (Role-Based Access Control)
-- =============================================================================

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE roles IS 'Stores authorization roles and permission scopes for RBAC';
COMMENT ON COLUMN roles.name IS 'Unique role string identifier (admin, investigator, viewer)';
COMMENT ON COLUMN roles.permissions IS 'JSON object defining granular scope capabilities';

-- Seed default system roles
INSERT INTO roles (name, display_name, description, permissions)
VALUES 
    ('admin', 'Administrator', 'Full system control, user management, and system configuration', '{"system": ["*"], "videos": ["*"], "reports": ["*"], "users": ["*"]}'::jsonb),
    ('investigator', 'Investigator', 'Can upload videos, perform AI searches, and generate investigative reports', '{"videos": ["create", "read", "update", "delete"], "search": ["*"], "reports": ["*"]}'::jsonb),
    ('viewer', 'Viewer', 'Read-only access to assigned surveillance videos and search results', '{"videos": ["read"], "search": ["read"], "reports": ["read"]}'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- TABLE 2: USERS (Authentication & User Accounts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    supabase_user_id VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    role userrole NOT NULL DEFAULT 'viewer',
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_email_verified BOOLEAN NOT NULL DEFAULT false,
    last_login_at VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    is_deleted BOOLEAN NOT NULL DEFAULT false
);

COMMENT ON TABLE users IS 'System users, credentials mapping, and profile attributes';
COMMENT ON COLUMN users.email IS 'User primary login email identifier';
COMMENT ON COLUMN users.supabase_user_id IS 'External Supabase authentication user ID';

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_supabase_user_id ON users(supabase_user_id);
CREATE INDEX IF NOT EXISTS ix_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS ix_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS ix_users_email_is_deleted ON users(email, is_deleted);

-- =============================================================================
-- TABLE 3: VIDEOS (Uploaded Video Files & Processing State)
-- =============================================================================

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'video/mp4',
    duration_seconds DOUBLE PRECISION,
    fps DOUBLE PRECISION,
    width INT,
    height INT,
    total_frames INT,
    status videostatus NOT NULL DEFAULT 'pending',
    error_message TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

COMMENT ON TABLE videos IS 'Ingested surveillance video assets and pipeline processing status';

CREATE INDEX IF NOT EXISTS ix_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS ix_videos_title ON videos(title);
CREATE INDEX IF NOT EXISTS ix_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS ix_videos_created_at ON videos(created_at);

-- =============================================================================
-- TABLE 4: FRAMES (Extracted Keyframes & Timestamps)
-- =============================================================================

CREATE TABLE IF NOT EXISTS frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    frame_number INT NOT NULL,
    timestamp_seconds DOUBLE PRECISION NOT NULL,
    image_path VARCHAR(512) NOT NULL,
    width INT,
    height INT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE frames IS 'Extracted video keyframes and sampling offset markers';

CREATE INDEX IF NOT EXISTS ix_frames_video_id ON frames(video_id);
CREATE INDEX IF NOT EXISTS ix_frames_video_timestamp ON frames(video_id, timestamp_seconds);
CREATE INDEX IF NOT EXISTS ix_frames_video_frame_number ON frames(video_id, frame_number);

-- =============================================================================
-- TABLE 5: OBJECTS (AI Object Detections & Tracking)
-- =============================================================================

CREATE TABLE IF NOT EXISTS objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    frame_id UUID NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    track_id INT,
    label VARCHAR(100) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    bounding_box JSONB NOT NULL,
    crop_path VARCHAR(512),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE objects IS 'AI object detections, class labels, bounding box coordinates, and tracking IDs';

CREATE INDEX IF NOT EXISTS ix_objects_frame_id ON objects(frame_id);
CREATE INDEX IF NOT EXISTS ix_objects_video_id ON objects(video_id);
CREATE INDEX IF NOT EXISTS ix_objects_label ON objects(label);
CREATE INDEX IF NOT EXISTS ix_objects_confidence ON objects(confidence);
CREATE INDEX IF NOT EXISTS ix_objects_track_id ON objects(track_id);
CREATE INDEX IF NOT EXISTS ix_objects_label_confidence ON objects(label, confidence);
CREATE INDEX IF NOT EXISTS ix_objects_video_track ON objects(video_id, track_id);

-- =============================================================================
-- TABLE 6: EMBEDDINGS (AI Vector Feature Representation - pgvector)
-- =============================================================================

CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    frame_id UUID REFERENCES frames(id) ON DELETE CASCADE,
    object_id UUID REFERENCES objects(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL DEFAULT 'CLIP-ViT-B/32',
    dimension INT NOT NULL DEFAULT 512,
    embedding vector(512) NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE embeddings IS '512-dimensional CLIP feature vectors for natural language and visual similarity search';

CREATE INDEX IF NOT EXISTS ix_embeddings_frame_id ON embeddings(frame_id);
CREATE INDEX IF NOT EXISTS ix_embeddings_object_id ON embeddings(object_id);
CREATE INDEX IF NOT EXISTS ix_embeddings_model_name ON embeddings(model_name);

-- HNSW Vector Index for ultra-fast approximate nearest neighbor cosine similarity search
CREATE INDEX IF NOT EXISTS ix_embeddings_vector_hnsw 
ON embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- =============================================================================
-- TABLE 7: SEARCH_HISTORY (User Search Query Analytics)
-- =============================================================================

CREATE TABLE IF NOT EXISTS search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT,
    query_image_path VARCHAR(512),
    search_type searchtype NOT NULL DEFAULT 'text',
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_count INT NOT NULL DEFAULT 0,
    execution_time_ms DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE search_history IS 'Operational log of user queries, filters applied, and latency performance';

CREATE INDEX IF NOT EXISTS ix_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS ix_search_history_search_type ON search_history(search_type);
CREATE INDEX IF NOT EXISTS ix_search_history_user_created ON search_history(user_id, created_at);

-- =============================================================================
-- TABLE 8: REPORTS (Investigative Reports & Evidence Bundles)
-- =============================================================================

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL DEFAULT 'investigation',
    status reportstatus NOT NULL DEFAULT 'draft',
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    file_path VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

COMMENT ON TABLE reports IS 'Investigative intelligence summaries, keyframe timeline bookmarks, and exported PDF reports';

CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS ix_reports_title ON reports(title);
CREATE INDEX IF NOT EXISTS ix_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS ix_reports_report_type ON reports(report_type);

-- =============================================================================
-- AUTOMATED UPDATED_AT TRIGGERS FOR ALL TABLES
-- =============================================================================

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_frames_updated_at BEFORE UPDATE ON frames FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_objects_updated_at BEFORE UPDATE ON objects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_embeddings_updated_at BEFORE UPDATE ON embeddings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_search_history_updated_at BEFORE UPDATE ON search_history FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
