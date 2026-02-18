# Alma Lead Management

REST API for managing immigration prospect leads, built with FastAPI and PostgreSQL.

Prospects submit their information through a public endpoint. Authenticated attorneys can then view leads and mark them as contacted.

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for running tests locally)

## Quick Start
```bash
cp .env.example .env
docker compose up --build
```

The API will be available at **http://localhost:8000**.
Interactive Swagger docs at **http://localhost:8000/docs**.

Database migrations run automatically on startup.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Health check |
| `POST` | `/api/v1/leads/` | No | Submit a new lead (multipart form with resume) |
| `GET` | `/api/v1/leads/` | Yes | List all leads |
| `GET` | `/api/v1/leads/{id}` | Yes | Get a single lead |
| `PATCH` | `/api/v1/leads/{id}/status` | Yes | Update lead status to REACHED_OUT |
| `POST` | `/api/v1/auth/login` | No | Obtain JWT access token |

## Authentication

The system uses JWT authentication. For testing, a hardcoded attorney account is provided:
```
username: attorney@alma.com
password: password123
```

Use the `/api/v1/auth/login` endpoint (or the "Authorize" button in Swagger UI) to obtain a token.

## Running Tests

Tests use an in-memory SQLite database, so no external services are required.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

## Project Structure
```
app/
  api/           Routes and FastAPI dependency injection
  core/          Swappable backends (storage, email) behind Protocol interfaces
  models/        SQLAlchemy ORM models
  repositories/  Data access layer (queries only, no business logic)
  schemas/       Pydantic request/response schemas
  services/      Business logic layer
tests/           pytest + httpx async integration tests
alembic/         Database migration scripts
```
