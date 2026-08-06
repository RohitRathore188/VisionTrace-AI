# Database Migrations

This directory contains Alembic migrations for the VisionTrace AI database schema.

## Directory Structure

```
migrations/
├── env.py                    # Alembic environment configuration
├── script.py.mako           # Migration script template
├── versions/                # Migration version files
│   └── 20260805_1648_001_create_users_table.py
└── README.md                # This file
```

## Running Migrations

### Apply All Migrations
```bash
# From backend directory
alembic upgrade head
```

### Apply Specific Migration
```bash
alembic upgrade <revision>
# Example: alembic upgrade 001
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

### Rollback to Specific Version
```bash
alembic downgrade <revision>
# Example: alembic downgrade 001
```

### Rollback All Migrations
```bash
alembic downgrade base
```

## Creating New Migrations

### Auto-generate from Model Changes
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Create Empty Migration
```bash
alembic revision -m "Description of changes"
```

## Viewing Migration History

### Show Current Version
```bash
alembic current
```

### Show Migration History
```bash
alembic history
```

### Show SQL Without Executing
```bash
alembic upgrade head --sql
```

## Migration Files

### 001 - Create Users Table
**File**: `20260805_1648_001_create_users_table.py`
**Description**: Initial migration that creates the users table with role-based access control

**Includes**:
- UUID primary key
- Email authentication
- Supabase user ID mapping
- Role enum (admin, investigator, viewer)
- Account status flags (is_active, is_email_verified)
- Timestamps (created_at, updated_at)
- Soft delete support (deleted_at, is_deleted)
- Indexes for performance
- Auto-update trigger for updated_at

## Configuration

Alembic configuration is in `/backend/alembic.ini`:
- Migration scripts location: `app/db/migrations`
- File template: `%%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s`
- Database URL is loaded from `app.core.config.settings`

## Best Practices

1. **Always review auto-generated migrations** - Check that they match your intent
2. **Test migrations** - Run up and down migrations in development
3. **One logical change per migration** - Keep migrations focused
4. **Write reversible migrations** - Always implement `downgrade()`
5. **Don't modify applied migrations** - Create a new migration instead
6. **Backup before production migrations** - Always have a rollback plan

## Troubleshooting

### "Target database is not up to date"
```bash
alembic stamp head  # Mark database as current
```

### "Can't locate revision identified by"
Check that migration files are in `versions/` directory and properly named.

### Database connection errors
Ensure `.env` file has correct DATABASE_URL and database is running:
```bash
docker-compose up -d postgres
```

## Environment Configuration

Migrations use synchronous database URL (without `+asyncpg`):
- Settings loaded from `app.core.config.settings`
- URL automatically converted in `settings.database_url_sync`
- Models imported from `app.models`
