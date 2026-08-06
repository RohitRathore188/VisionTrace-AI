"""Create users table with role-based access

Revision ID: 001
Revises: 
Create Date: 2026-08-05 16:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create users table with role-based access control.
    
    Includes:
    - UUID primary key
    - Email (unique identifier)
    - Supabase user ID mapping
    - Full name
    - Role enum (admin, investigator, viewer)
    - Account status flags
    - Timestamps (created_at, updated_at, deleted_at)
    - Soft delete support
    """
    # Create user role enum
    user_role_enum = postgresql.ENUM(
        'admin',
        'investigator',
        'viewer',
        name='userrole',
        create_type=True
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        # Primary key (UUID)
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            comment='User UUID'
        ),
        
        # Authentication
        sa.Column(
            'email',
            sa.String(255),
            nullable=False,
            unique=True,
            index=True,
            comment='User email address (unique identifier)'
        ),
        sa.Column(
            'supabase_user_id',
            sa.String(255),
            nullable=True,
            unique=True,
            index=True,
            comment='Supabase auth user ID'
        ),
        
        # Profile
        sa.Column(
            'full_name',
            sa.String(255),
            nullable=True,
            comment="User's full name"
        ),
        
        # Role-based access control
        sa.Column(
            'role',
            user_role_enum,
            nullable=False,
            server_default='viewer',
            comment='User role for access control'
        ),
        
        # Account status
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
            comment='Account active status'
        ),
        sa.Column(
            'is_email_verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Email verification status'
        ),
        
        # Login tracking
        sa.Column(
            'last_login_at',
            sa.String(255),
            nullable=True,
            comment='Last login timestamp (ISO format)'
        ),
        
        # Timestamps (from TimestampMixin)
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
            comment='Record creation timestamp'
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
            comment='Record last update timestamp'
        ),
        
        # Soft delete (from SoftDeleteMixin)
        sa.Column(
            'deleted_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Soft delete timestamp'
        ),
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            index=True,
            comment='Soft delete flag'
        ),
    )
    
    # Create indexes
    op.create_index(
        'ix_users_email_is_deleted',
        'users',
        ['email', 'is_deleted'],
        unique=False
    )
    op.create_index(
        'ix_users_role',
        'users',
        ['role'],
        unique=False
    )
    op.create_index(
        'ix_users_is_active',
        'users',
        ['is_active'],
        unique=False
    )
    
    # Create trigger for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop users table and related objects"""
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop indexes
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_email_is_deleted', table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    # Drop enum
    user_role_enum = postgresql.ENUM(
        'admin',
        'investigator',
        'viewer',
        name='userrole'
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)
