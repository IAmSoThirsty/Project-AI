<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP API

Production-grade FastAPI application for texture pack repository management.

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Create initial admin user (optional)
python scripts/create_admin.py
```

### Running Locally

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Project Structure

```
api/
├── app/
│   ├── core/          # Configuration, database, logging
│   ├── models/        # SQLAlchemy ORM models
│   ├── routes/        # API endpoint definitions
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Business logic layer
│   ├── middleware/    # Custom middleware
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── alembic/           # Database migrations
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

### Packs
- `GET /api/v1/packs` - List packs (with pagination/filtering)
- `GET /api/v1/packs/{pack_id}` - Get pack details
- `POST /api/v1/packs` - Create new pack (requires creator role)
- `PUT /api/v1/packs/{pack_id}` - Update pack
- `DELETE /api/v1/packs/{pack_id}` - Delete pack (requires admin role)

### Health
- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe
- `GET /metrics` - Prometheus metrics

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Docker

```bash
# Build image
docker build -t ttp-api:latest .

# Run container
docker run -p 8000:8000 --env-file .env ttp-api:latest
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing secret
- `S3_BUCKET` - S3 bucket for texture assets

## License

MIT License - See LICENSE file for details.
