# FastAPI Backend - Setup Guide

## Step-by-Step Setup Instructions

### 1. Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
venv\Scripts\Activate.ps1

# On Windows CMD:
venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env

# Edit .env and configure:
# - DATABASE_URL (PostgreSQL connection string)
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - SUPABASE_URL and SUPABASE_SERVICE_KEY
```

### 3. Setup Database

**Option A: Using Docker Compose (Recommended)**

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Wait for services to be healthy
docker-compose ps
```

**Option B: Local PostgreSQL**

```bash
# Install PostgreSQL 15+
# Create database
createdb visiontrace

# Verify connection
psql postgresql://postgres:password@localhost:5432/visiontrace -c "SELECT version();"
```

### 4. Run Database Migrations

```bash
# Run Alembic migrations (creates tables)
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt"
```

### 5. Start Development Server

```bash
# Start FastAPI server with auto-reload
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Installation

Open your browser and test these endpoints:

- **Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/v1/system/health
- **Readiness**: http://localhost:8000/api/v1/system/readiness
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Expected responses:

```bash
# Health check
curl http://localhost:8000/api/v1/system/health
# {"status":"ok","timestamp":"2026-08-05T10:30:00Z"}

# Readiness check
curl http://localhost:8000/api/v1/system/readiness
# {"status":"ready","checks":{"database":{"status":"ok"}},"timestamp":"..."}
```

## Quick Start with Docker Compose

If you want to run everything (API + Database + Redis) with Docker:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Access API at http://localhost:8000

# Stop all services
docker-compose down
```

## Troubleshooting

### Import Error: "No module named 'app'"

Make sure you're running from the `backend` directory and virtual environment is activated.

### Database Connection Error

Check your `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/visiontrace
```

Test connection:
```bash
psql postgresql://postgres:password@localhost:5432/visiontrace -c "SELECT 1"
```

### Alembic Migration Errors

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Downgrade one version
alembic downgrade -1

# Upgrade to latest
alembic upgrade head
```

### Port Already in Use

If port 8000 is already in use:
```bash
# Change port in .env
PORT=8001

# Or specify in command
uvicorn app.main:app --reload --port 8001
```

## Development Workflow

### 1. Code Changes

```bash
# Make your changes
# The server will auto-reload (--reload flag)
```

### 2. Database Schema Changes

```bash
# After modifying models in app/models/
# Create migration
alembic revision --autogenerate -m "Add new table"

# Review the generated migration in app/db/migrations/versions/

# Apply migration
alembic upgrade head
```

### 3. Code Quality Checks

```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/

# Run all at once
black app/ && ruff check app/ && mypy app/
```

### 4. Run Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # On Mac
start htmlcov/index.html # On Windows
```

## Project Structure Overview

```
backend/
├── app/
│   ├── api/                    # API routes and middleware
│   ├── core/                   # Configuration and utilities
│   ├── db/                     # Database and migrations
│   ├── models/                 # SQLAlchemy models (future)
│   ├── schemas/                # Pydantic schemas
│   ├── dependencies.py         # FastAPI dependencies
│   └── main.py                 # Application entry point
├── tests/                      # Test suite (future)
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment variables
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker Compose for local dev
├── Dockerfile                  # Docker image for production
├── requirements.txt            # Production dependencies
└── requirements-dev.txt        # Development dependencies
```

## Next Steps

Now that the foundation is ready, you can:

1. **Add Authentication**: Implement user registration and login
2. **Add Video Routes**: Create video upload and management endpoints
3. **Add Models**: Define SQLAlchemy models in `app/models/`
4. **Add Repositories**: Create data access layer in `app/repositories/`
5. **Add Services**: Implement business logic in `app/services/`

## Useful Commands

```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check Python version
python --version

# List installed packages
pip list

# Update all dependencies
pip install -U -r requirements-dev.txt

# Generate requirements.txt from current environment
pip freeze > requirements.txt

# Test database connection
python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT signing secret |
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | - | Supabase service role key |
| `ENVIRONMENT` | No | development | Environment name |
| `DEBUG` | No | False | Enable debug mode |
| `LOG_LEVEL` | No | INFO | Logging level |
| `PORT` | No | 8000 | Server port |
| `ALLOWED_ORIGINS` | No | localhost | CORS allowed origins |

## Support

For help, refer to:
- **README.md** - Full documentation
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Alembic Docs**: https://alembic.sqlalchemy.org
