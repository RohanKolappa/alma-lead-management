# Design Document

## Overview

Alma Lead Management is a REST API that allows immigration prospects to submit their information and resume, and allows attorneys to review and manage those leads. The system sends confirmation emails to prospects and notification emails to attorneys on each submission.

## Architecture

The application follows a three-layer design:

```
Routes  -->  Services  -->  Repositories
  |              |
  |         StorageBackend
  |         EmailBackend
  v
Pydantic schemas (validation + serialization)
```

- **Routes** handle HTTP concerns: request parsing, auth, status codes, response serialization.
- **Services** contain business logic: orchestrating storage, persistence, and notifications. They raise HTTP exceptions for domain errors (404, 409).
- **Repositories** are a thin data-access layer over SQLAlchemy. They own all queries and know nothing about HTTP.

This separation keeps each layer independently testable and prevents business logic from leaking into route handlers or database queries.

## Key Design Decisions

| Area | Choice | Rationale |
|------|--------|-----------|
| **Database** | PostgreSQL 16 | Production-grade, matches target deployment (Supabase is Postgres). Docker Compose provides zero-config local setup. |
| **File Storage** | Local filesystem behind `StorageBackend` protocol | Abstraction allows swapping to S3 or Supabase Storage without changing business logic. Local storage is sufficient for development and demo. |
| **Auth** | JWT + OAuth2 password bearer | Maps directly to Supabase Auth's JWT-based approach. Hardcoded user for demo; production would validate against a user table. |
| **Email** | Console backend behind `EmailBackend` protocol | Production would swap to SendGrid or SES. Emails are fire-and-forget: failures are logged but never block lead submission. |
| **API versioning** | `/api/v1` prefix | Forward-compatible. A `/v2` can be introduced alongside `/v1` without breaking existing clients. |
| **Testing** | SQLite async + httpx | No external dependencies required. Tests run in ~2s. The in-memory DB is created/torn down per test for full isolation. |

## State Machine

Lead status follows a one-way transition:

```
PENDING  -->  REACHED_OUT
```

- All leads start as `PENDING`.
- An authenticated attorney can mark a lead as `REACHED_OUT` via `PATCH /api/v1/leads/{id}/status`.
- Attempting to transition an already `REACHED_OUT` lead returns **409 Conflict**, providing idempotency safety.

## Trade-offs and Future Improvements

**What I would add with more time:**

- **Rate limiting** on the public submission endpoint to prevent abuse.
- **File virus scanning** (ClamAV or a cloud service) before persisting uploads.
- **Cursor-based pagination** instead of offset/limit for stable page results under concurrent writes.
- **Background job queue** (Celery or ARQ) for email delivery, retries, and dead-letter handling.
- **Full user management** with role-based access control replacing the hardcoded attorney account.

**Storage migration path:**

The `StorageBackend` protocol makes this a single-class swap. Implement an `S3StorageBackend` satisfying the same `save` / `get_path` / `delete` interface, register it in the dependency, and the rest of the application is unaware of the change.

**Observability:**

Production would add structured JSON logging, request-id propagation, and integration with an observability platform (Datadog, Betterstack) for tracing and alerting.

**Testing note:**

The test suite caught a real bug during development: Pydantic's `EmailStr` validation was raising an unhandled `ValidationError` when constructing `LeadCreate` from form fields inside the route handler. FastAPI only auto-catches validation errors on declared request bodies, not on manually constructed models. The fix was a targeted `try/except` converting it to a proper 422 response.
