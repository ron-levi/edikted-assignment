# Fashion PLM - Product Lifecycle Management System

A full-stack web application for managing the journey of fashion garments from initial design concept through production readiness.

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 (async) / PostgreSQL 16
- **Frontend**: React 19 / TypeScript / Vite / Tailwind CSS / TanStack Query
- **Infrastructure**: Docker Compose (PostgreSQL)

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

## Quick Start

### One-command setup (Docker)

```bash
docker compose up --build
```

This starts Postgres, the backend (with auto-seeded data), and the frontend. Open http://localhost:5173 once everything is up.

To stop: `docker compose down`

### Manual setup

#### 1. Start PostgreSQL

```bash
cd backend
make db-up
```

#### 2. Start Backend

```bash
cd backend
make install   # creates venv and installs dependencies
make dev       # starts FastAPI on http://localhost:8000
```

API docs available at http://localhost:8000/docs

#### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev    # starts Vite on http://localhost:5173
```

## Architecture

```
frontend/ (React SPA)  -->  HTTP/REST  -->  backend/ (FastAPI)  -->  PostgreSQL
```

Three-layer backend architecture:
- **Routers** - HTTP concerns only (request parsing, response formatting)
- **Services** - All business logic, validation, state transitions
- **Models** - SQLAlchemy ORM (data access + domain entities)

### Key Design Decisions

1. **State machines as transition maps** - Garment lifecycle and supplier pipeline implemented as simple dictionaries (`current_state -> set(valid_targets)`). Validated at the service layer.

2. **Canonical ordered pairs for incompatibility** - Attribute incompatibility stored as `(min_id, max_id)` with a CHECK constraint, eliminating duplicate inverse entries.

3. **Async throughout** - Backend uses asyncpg + SQLAlchemy async sessions for non-blocking database operations.

4. **Service layer pattern** - Business rules are enforced in the service layer, not in routers or models. This keeps HTTP routing thin and business logic testable.

5. **Seed data on startup** - Materials, attributes, incompatibility rules, and sample suppliers are auto-populated on first run (idempotent).

## Domain Model

### Garment Lifecycle
```
CONCEPT -> DESIGN -> DEVELOPMENT -> SAMPLING -> PRODUCTION
```
- Forward and backward transitions allowed (rework scenarios)
- PRODUCTION is terminal (no exit)
- PRODUCTION garments cannot be deleted

### Supplier Pipeline
```
OFFERED -> SAMPLING -> APPROVED -> IN_PRODUCTION -> IN_STORE
                                   \-> REJECTED (exit from OFFERED, SAMPLING, APPROVED)
```

### Business Rules
- Material composition percentages must total <= 100%
- Incompatible attributes cannot coexist on the same garment (e.g., nightwear + activewear)
- Garment variations are linked via parent_garment_id (design evolution tracking)
- Sample set statuses follow a defined transition flow (PENDING -> RECEIVED -> APPROVED/REJECTED)

## Project Structure

```
backend/
  app/
    models/          # SQLAlchemy ORM models
    schemas/         # Pydantic request/response schemas
    services/        # Business logic layer
    routers/         # FastAPI route handlers
    config.py        # Environment-based configuration
    database.py      # Async database session management
    exceptions.py    # Custom exception hierarchy
    seed.py          # Initial data population
    main.py          # FastAPI app entry point
frontend/
  src/
    components/      # Reusable UI components (Badge, Modal, Spinner, Layout)
    hooks/           # TanStack Query hooks per domain entity
    lib/api.ts       # Typed API client
    pages/           # Dashboard and GarmentDetail pages
    types/index.ts   # TypeScript interfaces matching backend schemas
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/fashion_plm` | PostgreSQL connection string |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |
| `DEBUG` | `true` | Debug mode |

## Assumptions & Trade-offs

- **No authentication** - Out of scope for MVP; all endpoints are public
- **No test suite** - Time-constrained; business rules validated via Swagger UI and frontend testing
- **PostgreSQL only** - SQLAlchemy supports other databases but migrations are PostgreSQL-specific
- **Seed data is idempotent** - Runs on every startup, skips if data already exists
- **Frontend relies on server validation** - Client-side validation is minimal; the backend is the source of truth for business rules
