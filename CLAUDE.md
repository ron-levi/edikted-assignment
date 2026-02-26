# CLAUDE.md — Fashion PLM Codebase Guide

This file describes the structure, conventions, and development workflows for this Fashion Product Lifecycle Management (PLM) system. Read it before making changes.

---

## Project Overview

A fullstack Fashion PLM application that manages garments through a defined lifecycle (CONCEPT → DESIGN → DEVELOPMENT → SAMPLING → PRODUCTION), including materials, attributes, suppliers, and sample tracking.

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, TanStack Query v5, Tailwind CSS |
| Infrastructure | Docker Compose (3 services: db, api, frontend) |

---

## Repository Layout

```
edikted-assignment/
├── CLAUDE.md                # This file
├── README.md                # Human-readable setup guide
├── PRD.md                   # Product requirements
├── Makefile                 # Root-level convenience targets (delegates to backend)
├── docker-compose.yml       # Orchestrates db + api + frontend
├── backend/                 # Python FastAPI backend
└── frontend/                # React/TypeScript frontend
```

---

## Running the Project

### Full Stack (Docker)
```bash
make stack          # docker compose up --build
make stack-down     # docker compose down
```

### Backend Only (local)
```bash
cd backend
cp .env.example .env       # First time only
make install               # Install dependencies (uv/pip)
make db-up                 # Start PostgreSQL in Docker only
make migrate               # Apply Alembic migrations
make dev                   # Start FastAPI with --reload on port 8000
```

### Frontend Only (local)
```bash
cd frontend
npm install
npm run dev                # Vite dev server on port 5173
```

The frontend proxies `/api` requests to `http://localhost:8000` (configured in `vite.config.ts`).

### Swagger UI
Available at `http://localhost:8000/docs` when the backend is running.

---

## Backend

### Directory Structure

```
backend/
├── pyproject.toml           # Dependencies and project metadata
├── alembic.ini              # Alembic migration config
├── Makefile                 # Backend-specific commands
├── Dockerfile               # Backend container
├── docker-compose.yml       # Standalone backend stack (db + api)
├── .env.example             # Environment variable template
└── app/
    ├── main.py              # App factory, CORS, exception handlers, router registration
    ├── config.py            # Pydantic Settings (reads .env)
    ├── database.py          # Async engine, session factory, Base
    ├── exceptions.py        # Custom exception hierarchy
    ├── seed.py              # Idempotent seed data (runs on startup)
    ├── models/              # SQLAlchemy ORM models
    ├── schemas/             # Pydantic request/response schemas
    ├── services/            # Business logic layer
    └── routers/             # FastAPI route handlers (HTTP only)
```

### Three-Layer Architecture

```
Router (HTTP) → Service (Business Logic) → Model (ORM/DB)
```

- **Routers** (`app/routers/`) handle HTTP request/response only. No business logic here.
- **Services** (`app/services/`) enforce all business rules: state machine validation, incompatibility checks, protection rules.
- **Models** (`app/models/`) are SQLAlchemy ORM classes; no business logic.

Always add new business rules to the service layer, not routers.

### Environment Variables

Defined in `backend/.env` (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/fashion_plm` | Async PostgreSQL connection |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | JSON array of allowed origins |
| `DEBUG` | `true` | Enable debug mode |

### Async Pattern

All database operations are async. Follow this pattern everywhere:

```python
# Service function signature
async def my_service_fn(db: AsyncSession, ...) -> Schema:
    result = await db.execute(select(Model).where(...))
    ...

# Router dependency injection
@router.get(...)
async def endpoint(db: AsyncSession = Depends(get_db)):
    return await service.my_service_fn(db, ...)
```

Never use synchronous SQLAlchemy calls (no `db.query()`). Always use `await db.execute(select(...))`.

### Domain Models

| Model | File | Key Fields |
|-------|------|-----------|
| `Garment` | `models/garment.py` | `lifecycle_stage`, `parent_garment_id` (self-ref FK for variations) |
| `Material` | `models/material.py` | `name` (unique) |
| `GarmentMaterial` | `models/material.py` | `percentage` (0–100), unique on `(garment_id, material_id)` |
| `Attribute` | `models/attribute.py` | `name`, `category`; unique on `(name, category)` |
| `GarmentAttribute` | `models/attribute.py` | Junction; unique on `(garment_id, attribute_id)` |
| `AttributeIncompatibility` | `models/attribute.py` | Stored as ordered pair `(id_1 < id_2)` with DB CHECK constraint |
| `Supplier` | `models/supplier.py` | `name`, `contact_info` |
| `GarmentSupplier` | `models/supplier.py` | `status`, `offer_price`, `lead_time_days`; unique on `(garment_id, supplier_id)` |
| `SampleSet` | `models/sample_set.py` | `status`, linked to `GarmentSupplier` |

### State Machines

State machines are defined as dicts in `app/services/lifecycle.py`. Terminal states map to `set()`.

**Garment lifecycle:**
```
CONCEPT → DESIGN → DEVELOPMENT → SAMPLING → PRODUCTION (terminal)
```
(DESIGN and DEVELOPMENT also allow backward transitions)

**Supplier status:**
```
OFFERED → SAMPLING → APPROVED → IN_PRODUCTION → IN_STORE (terminal)
         ↘ REJECTED (terminal from OFFERED, SAMPLING, APPROVED)
```

**Sample set status:**
```
PENDING → RECEIVED → APPROVED (terminal)
                   → REJECTED (terminal)
```

Transitions are validated in service methods (`transition_garment`, `transition_supplier`, `update_sample_set`). Raise `InvalidTransitionError` on invalid transitions.

### Custom Exceptions

All in `app/exceptions.py`. Use the correct class — routers map them to HTTP status codes automatically via the exception handler in `main.py`:

| Exception | HTTP | When to use |
|-----------|------|-------------|
| `NotFoundError` | 404 | Resource not found |
| `InvalidTransitionError` | 409 | Bad state machine transition |
| `IncompatibleAttributeError` | 409 | Attribute conflict |
| `DeletionProtectedError` | 403 | Trying to delete a PRODUCTION garment |
| `ProductionProtectedError` | 403 | Trying to modify a PRODUCTION garment |
| `ValidationError` | 422 | Input validation failure |

### Schemas

For every domain entity there are separate Pydantic v2 schemas in `app/schemas/`:
- `<Entity>Create` — request body for creation
- `<Entity>Update` — request body for updates (all fields optional)
- `<Entity>Response` — response serialization

Never reuse the same schema for input and output.

### Eager Loading

In `garment_service.get_garment()`, use `selectinload`/`joinedload` to pre-fetch relationships and avoid N+1 queries. When adding new relationships to `Garment`, add appropriate eager loading in this function.

### Seed Data

`app/seed.py` runs on startup (in the `lifespan` context of `main.py`) and is idempotent. It populates:
- 10 materials
- 15 attributes across 5 categories
- 5 attribute incompatibility rules
- 3 sample suppliers

If you add new reference data, add it to `seed.py`.

### Makefile Commands (backend/)

```bash
make install    # Install Python dependencies
make dev        # Run FastAPI dev server (port 8000)
make db-up      # Start PostgreSQL container only
make migrate    # Apply Alembic migrations
make help       # Show all available targets
```

---

## Frontend

### Directory Structure

```
frontend/
├── package.json             # Dependencies, scripts
├── vite.config.ts           # Vite config (port 5173, /api proxy)
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind CSS config
├── eslint.config.js         # ESLint config
└── src/
    ├── main.tsx             # React entry point
    ├── App.tsx              # Router + QueryClientProvider setup
    ├── index.css            # Global Tailwind imports
    ├── types/
    │   └── index.ts         # All TypeScript interfaces (mirrors backend schemas)
    ├── lib/
    │   └── api.ts           # Typed fetch wrapper; all API calls go here
    ├── hooks/               # TanStack Query hooks per domain
    │   ├── useGarments.ts
    │   ├── useMaterials.ts
    │   ├── useAttributes.ts
    │   └── useSuppliers.ts
    ├── pages/
    │   ├── Dashboard.tsx    # Garment list with filters
    │   └── GarmentDetail.tsx # Full garment editor
    └── components/
        ├── layout/
        │   └── Layout.tsx   # Nav header + Outlet
        └── ui/
            ├── Badge.tsx    # Status/stage badge
            ├── Modal.tsx    # Generic modal dialog
            └── Spinner.tsx  # Loading indicator
```

### Data Fetching Pattern

All API calls go through `src/lib/api.ts`. All server state is managed by TanStack Query hooks in `src/hooks/`.

**Adding a new API call:**
1. Add a typed function to `src/lib/api.ts`
2. Add a query or mutation hook to the appropriate `src/hooks/use<Domain>.ts`
3. Invalidate relevant query keys in mutation `onSuccess` callbacks

**Example pattern:**
```typescript
// lib/api.ts
export async function createWidget(data: WidgetCreateRequest): Promise<Widget> {
  return request<Widget>('/widgets', { method: 'POST', body: JSON.stringify(data) });
}

// hooks/useWidgets.ts
export function useCreateWidget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createWidget,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['widgets'] }),
  });
}
```

### TypeScript Types

All interfaces are in `src/types/index.ts`. These must match the backend Pydantic schemas exactly. When changing a backend schema, update the corresponding TypeScript interface.

The file also mirrors the backend state machine constants:
- `LIFECYCLE_STAGES` — ordered array of garment stages
- `GARMENT_TRANSITIONS` — allowed garment transitions
- `SUPPLIER_TRANSITIONS` — allowed supplier transitions

### Error Handling

`api.ts` throws `ApiError` (with `errorCode` and `message`) on non-2xx responses. Hooks display errors via `react-hot-toast`. Always show user-facing errors from the API's `detail` field, not raw error objects.

### Styling

Tailwind CSS utility classes only — no custom CSS except for global imports in `index.css`. Follow existing component patterns for spacing, color, and layout.

### Scripts (frontend/)

```bash
npm run dev      # Vite dev server on port 5173
npm run build    # TypeScript check + Vite bundle
npm run lint     # ESLint
```

---

## Database

### Schema Summary

9 tables:
- `garments` — core entity, self-referential FK for design variations
- `materials` — reference data
- `garment_materials` — junction with `percentage` (sum ≤ 100% per garment)
- `attributes` — reference data with `category` enum
- `garment_attributes` — junction
- `attribute_incompatibilities` — ordered pairs `(id_1 < id_2)` with DB CHECK constraint
- `suppliers` — reference data
- `garment_suppliers` — association with status, pricing, lead time
- `sample_sets` — linked to garment-supplier association

### Migrations

Alembic is configured but the initial migration (`fa22dbce3e75_initial_schema.py`) is empty — tables are created by `metadata.create_all()` in the lifespan handler. For schema changes:

1. Modify the SQLAlchemy model
2. Generate a migration: `alembic revision --autogenerate -m "description"`
3. Apply it: `make migrate` (or `alembic upgrade head`)

---

## Key Conventions

### Backend
- Use `async`/`await` for all database operations
- Business rules belong in services, not routers
- Raise the correct `AppException` subclass; let the exception handler convert to HTTP
- Incompatibility pairs must be stored with `min_id` as `attribute_id_1` (enforce ordering before inserting)
- PRODUCTION garments are immutable — always check `lifecycle_stage == "PRODUCTION"` before mutations
- Material percentage sum per garment must not exceed 100%

### Frontend
- All API calls go through `src/lib/api.ts`
- All server state goes through TanStack Query hooks
- Never call `fetch()` directly from components or pages
- Type everything; no `any` unless absolutely unavoidable
- Keep pages thin — complex logic belongs in hooks
- Use `react-hot-toast` for all user feedback (success/error notifications)

### General
- No authentication — all endpoints are public (MVP scope)
- No test suite currently — validate via Swagger UI at `/docs`
- No audit trail — changes are not logged historically
- `PRD.md` is the authoritative source for product requirements

---

## Common Tasks

### Add a new garment field
1. Add column to `backend/app/models/garment.py`
2. Update `GarmentCreate`, `GarmentUpdate`, `GarmentResponse` in `backend/app/schemas/garment.py`
3. Update service logic in `backend/app/services/garment_service.py` if needed
4. Generate and apply an Alembic migration
5. Update `Garment` / `GarmentDetail` interfaces in `frontend/src/types/index.ts`
6. Update `api.ts` request/response types if needed
7. Update UI in `GarmentDetail.tsx` or `Dashboard.tsx`

### Add a new API endpoint
1. Add a service function in `backend/app/services/<domain>_service.py`
2. Add a router function in `backend/app/routers/<domain>.py`
3. Add a typed function in `frontend/src/lib/api.ts`
4. Add a TanStack Query hook in `frontend/src/hooks/use<Domain>.ts`
5. Use the hook in the appropriate page component

### Add a new state transition
1. Update the transition dict in `backend/app/services/lifecycle.py`
2. Update the mirrored constant in `frontend/src/types/index.ts`
3. Update UI transition buttons in `GarmentDetail.tsx`

### Add seed data
1. Add to `backend/app/seed.py` following the existing idempotent pattern (check before insert)
