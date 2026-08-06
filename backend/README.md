# VisionTrace AI - Backend API

Intelligent Video Search Platform - FastAPI Backend

## Features

- ✅ **Production-Ready Architecture**: Clean architecture with separation of concerns
- ✅ **Async SQLAlchemy**: Non-blocking database operations
- ✅ **Structured Logging**: JSON logging with request IDs (structlog)
- ✅ **Error Handling**: Consistent error responses across all endpoints
- ✅ **Health Checks**: Liveness and readiness probes for Kubernetes
- ✅ **API Versioning**: v1 routes with support for future versions
- ✅ **OpenAPI/Swagger**: Auto-generated interactive API documentation
- ✅ **Docker Support**: Multi-stage Docker build with docker-compose
- ✅ **Type Safety**: Full type hints with Pydantic validation
- ✅ **Security**: JWT authentication, bcrypt password hashing, CORS
- ✅ **Database Migrations**: Alembic with async support

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for future features)

## Quick Start

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env and set your database credentials and secrets
```

### 3. Database Setup

```bash
# Create database
createdb visiontrace

# Run migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
# Direct run
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/system/health

## Docker Deployment

### Development with Docker Compose

```bash
# Start all services (API + PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Docker Build

```bash
# Build image
docker build -t visiontrace-api:latest .

# Run container
docker run -p 8000:8000 --env-file .env visiontrace-api:latest
```

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   ├── v1/                 # Version 1 endpoints
│   │   │   └── system.py       # Health/readiness checks
│   │   ├── middleware/         # Custom middleware
│   │   │   ├── error_handler.py
│   │   │   ├── logging.py
│   │   │   └── request_id.py
│   │   └── router.py           # Master router
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py          # Logging config
│   │   └── security.py         # JWT + password hashing
│   ├── db/                     # Database
│   │   ├── base.py             # Base classes + mixins
│   │   ├── session.py          # Async session factory
│   │   └── migrations/         # Alembic migrations
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic schemas
│   │   ├── base.py             # Base schemas
│   │   └── system.py           # System schemas
│   ├── dependencies.py         # FastAPI dependencies
│   └── main.py                 # App entry point
├── tests/                      # Test suite
├── .env.example                # Example environment variables
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Local development compose
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Tool configuration
└── README.md                   # This file
```

## API Endpoints

### System
- `GET /api/v1/system/health` - Health check (liveness)
- `GET /api/v1/system/readiness` - Readiness check (dependencies)

### Future Endpoints (Coming Soon)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/videos/upload` - Video upload
- `POST /api/v1/search/image` - Image search
- `POST /api/v1/search/text` - Text search

## Development

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/

# Run all checks
black app/ && ruff check app/ && mypy app/
```

### Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing secret (256-bit random key)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key

### Optional Variables

- `DEBUG` - Enable debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)
- `SENTRY_DSN` - Sentry error tracking (optional)
- `REDIS_URL` - Redis connection string (future use)

## Architecture

### Middleware Stack (Execution Order)

1. **ErrorHandlerMiddleware** - Global exception handling
2. **CORSMiddleware** - CORS policy enforcement
3. **LoggingMiddleware** - Request/response logging
4. **RequestIDMiddleware** - Request ID injection

### Logging

Structured JSON logging with request context:

```json
{
  "event": "request_completed",
  "timestamp": "2026-08-05T10:30:15.123Z",
  "level": "info",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/v1/system/health",
  "status_code": 200,
  "duration_ms": 12.34,
  "app": "VisionTrace AI",
  "version": "1.0.0",
  "environment": "development"
}
```

### Error Responses

All errors return consistent JSON format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "details": {}
  }
}
```

## Production Deployment

### Checklist

- [ ] Set strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `DATABASE_URL` for production database
- [ ] Set `ALLOWED_ORIGINS` to your frontend domain
- [ ] Configure `SENTRY_DSN` for error tracking
- [ ] Enable SSL/TLS for database connections
- [ ] Set up database backups
- [ ] Configure health check monitoring
- [ ] Set resource limits (CPU/memory)
- [ ] Review and adjust `DB_POOL_SIZE` based on load

### Recommended Infrastructure

- **Compute**: Railway, Render, AWS ECS, Google Cloud Run
- **Database**: Railway PostgreSQL, AWS RDS, Supabase
- **Monitoring**: Sentry, Datadog, New Relic
- **Logging**: CloudWatch, Logtail, Better Stack

## Troubleshooting

### Database Connection Issues

```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check if database exists
psql $DATABASE_URL -c "\l"
```

### Migration Issues

```bash
# Reset database (⚠️ DESTRUCTIVE)
alembic downgrade base
alembic upgrade head

# Check current migration version
alembic current
```

### Logging Issues

Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `ruff check app/`
5. Format code: `black app/`
6. Submit a pull request

## License

Proprietary - VisionTrace AI Team

## Support

For issues and questions, contact the development team.
