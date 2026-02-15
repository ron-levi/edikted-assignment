# Product Requirements Document: Fashion Product Lifecycle Management System

---

## 1. Executive Summary

The Fashion Product Lifecycle Management (PLM) System is a full-stack web application that manages the entire journey of fashion garments from initial design concept through production readiness. It provides a centralized platform for tracking garments, their material compositions, design attributes, supplier relationships, and lifecycle progression.

The system enforces critical business rules inherent to fashion product development: preventing incompatible design attribute combinations, managing state transitions for both garment lifecycle and supplier pipelines, and protecting production-stage records from deletion. It models the real-world complexity where garments evolve through variations, multiple suppliers compete for production rights, and only some suppliers ultimately reach store shelves.

**MVP Goal**: Deliver a working full-stack application that demonstrates solid domain modeling, business rule enforcement, and clean architectural separation across database, API, and UI layers -- with emphasis on the garment lifecycle and supplier pipeline as the core value drivers.

---

## 2. Mission

**Mission Statement**: Provide fashion product teams with a reliable system to manage garment development from concept to production, ensuring data integrity through enforced business rules and clear lifecycle tracking.

**Core Principles**:
1. **Domain-Driven Design** -- The data model and business logic reflect real-world fashion product development workflows
2. **State Integrity** -- All lifecycle and supplier transitions are validated; invalid state changes are rejected with clear feedback
3. **Constraint Enforcement** -- Business rules (attribute incompatibility, deletion protection) are enforced at the service layer, not left to client-side validation alone
4. **Clean Separation** -- Three distinct layers (database, API, UI) with clear boundaries and responsibilities
5. **Pragmatic Scope** -- Focus on demonstrating architectural thinking over feature completeness

---

## 3. Target Users

### Primary Personas

**Product Manager**
- Oversees garment pipeline from concept to production
- Needs: Dashboard view of all garments and their lifecycle stages, ability to transition garments through stages, overview of supplier status per garment
- Technical comfort: Moderate -- expects intuitive UI, not raw API access

**Designer**
- Defines garment attributes, materials, and creates design variations
- Needs: Assign/remove materials and attributes, create variations from existing garments, see design evolution history
- Technical comfort: Low -- relies on clear UI with validation feedback

**Procurement Manager**
- Manages supplier relationships, evaluates offers, tracks sample quality
- Needs: Associate suppliers with garments, track supplier status through the pipeline, manage sample sets, compare offers
- Technical comfort: Moderate

### Key User Needs
- At-a-glance view of where every garment sits in its lifecycle
- Clear feedback when business rules are violated (incompatible attributes, invalid transitions)
- Traceability of design evolution (which garment was derived from which)
- Visibility into supplier pipeline status per garment

---

## 4. MVP Scope

### In Scope -- Core Functionality
- ✅ Garment CRUD (create, read, update, delete with protection)
- ✅ Garment lifecycle state machine (CONCEPT -> DESIGN -> DEVELOPMENT -> SAMPLING -> PRODUCTION)
- ✅ Backward lifecycle transitions (rework scenarios)
- ✅ Deletion protection for PRODUCTION-stage garments
- ✅ Material management and assignment to garments with percentage composition
- ✅ Attribute management with categories (sleeve type, neckline, garment category, fit, feature)
- ✅ Attribute incompatibility rule engine (prevent conflicting combinations)
- ✅ Design evolution -- create garment variations linked to parent garment
- ✅ Supplier CRUD and association with garments (offers with price/lead time)
- ✅ Supplier status state machine (OFFERED -> SAMPLING -> APPROVED -> IN_PRODUCTION -> IN_STORE, with REJECTED exit)
- ✅ Sample set tracking per garment-supplier association
- ✅ Seed data for materials, attributes, incompatibility rules, and sample suppliers

### In Scope -- Technical
- ✅ RESTful API with full CRUD operations and documented endpoints (Swagger/OpenAPI)
- ✅ PostgreSQL database with proper schema design and constraints
- ✅ SQLAlchemy ORM models with Alembic migration support
- ✅ Pydantic request/response validation
- ✅ Service layer pattern separating business logic from HTTP routing
- ✅ Responsive React + TypeScript frontend
- ✅ TanStack Query for server state management
- ✅ Tailwind CSS for styling
- ✅ Docker Compose for PostgreSQL

### Out of Scope
- ❌ Authentication / authorization
- ❌ Role-based access control
- ❌ File uploads (design images, tech packs)
- ❌ Email notifications
- ❌ Audit logging / change history
- ❌ Bulk import/export (CSV, Excel)
- ❌ Advanced reporting / analytics dashboards
- ❌ Real-time updates (WebSockets)
- ❌ Deployment / CI/CD pipeline
- ❌ Internationalization (i18n)
- ❌ Unit/integration test suite (time-constrained)

---

## 5. User Stories

### Garment Management

**US-1: Create a new garment**
> As a product manager, I want to create a new garment with a name and description, so that I can begin tracking it from the concept stage.
>
> *Example*: Create "Summer Breeze Tee" with description "Lightweight cotton t-shirt for SS26 collection". It starts in CONCEPT stage automatically.

**US-2: View all garments**
> As a product manager, I want to see a list of all garments with their lifecycle stages, so that I can monitor the product pipeline at a glance.
>
> *Example*: Dashboard shows 12 garments -- 3 in CONCEPT, 4 in DESIGN, 2 in DEVELOPMENT, 2 in SAMPLING, 1 in PRODUCTION -- with color-coded stage badges.

**US-3: View garment details**
> As a product manager, I want to view the full details of a garment (materials, attributes, suppliers, lifecycle stage, variations), so that I understand its complete current state.
>
> *Example*: Clicking "Summer Breeze Tee" shows: 60% cotton + 40% polyester composition, attributes [short sleeve, crew neck, casual], 3 associated suppliers at various statuses, and 1 child variation.

**US-4: Update garment information**
> As a product manager, I want to edit a garment's name and description, so that product information stays accurate.

**US-5: Delete a garment (with protection)**
> As a product manager, I want to delete a garment that is no longer viable, but be prevented from deleting garments in production, so that production records are never lost.
>
> *Example*: Deleting a CONCEPT-stage garment succeeds. Attempting to delete a PRODUCTION-stage garment returns an error: "Garment 'Classic Denim Jacket' is in PRODUCTION stage and cannot be deleted."

### Materials & Attributes

**US-6: Assign materials to a garment**
> As a designer, I want to specify which materials compose a garment and their percentages, so that the bill of materials is tracked.
>
> *Example*: Assign 70% denim + 28% cotton + 2% lycra to "Stretch Skinny Jean".

**US-7: Assign attributes to a garment**
> As a designer, I want to tag a garment with attributes from various categories, so that its characteristics are well-defined.
>
> *Example*: Tag "Performance Hoodie" with [long sleeve, mock neck, activewear, regular fit, with zipper].

**US-8: Enforce incompatible attribute rules**
> As a designer, I want the system to reject incompatible attribute combinations with a clear error, so that only valid garment configurations exist.
>
> *Example*: A garment already tagged "nightwear" -- attempting to add "activewear" is rejected with: "Attribute 'activewear' is incompatible with existing attribute: nightwear."

### Design Evolution

**US-9: Create a garment variation**
> As a designer, I want to create a variation of an existing garment, so that design evolution is tracked and linked to the original.
>
> *Example*: From "Classic Tee (short sleeve)", create variation "Classic Tee (long sleeve)" -- the new garment has `parent_garment_id` pointing to the original.

**US-10: View design lineage**
> As a product manager, I want to see which garments are variations of which originals, so that I can trace design evolution.
>
> *Example*: "Classic Tee" detail page shows a "Variations" section listing "Classic Tee (long sleeve)" and "Classic Tee (with logo)".

### Lifecycle Management

**US-11: Progress garment through lifecycle**
> As a product manager, I want to advance a garment to the next lifecycle stage (or send it back for rework), so that the pipeline reflects reality.
>
> *Example*: Transition "Summer Breeze Tee" from DESIGN to DEVELOPMENT. Later, send it back from DEVELOPMENT to DESIGN for revisions. Invalid jumps (e.g., CONCEPT -> PRODUCTION) are rejected.

### Supplier Pipeline

**US-12: Associate suppliers with a garment**
> As a procurement manager, I want to link suppliers to a garment with their offer details (price, lead time), so that I can evaluate multiple sourcing options.
>
> *Example*: Associate "Fabric Co Ltd" with "Stretch Skinny Jean" at $12.50/unit, 45-day lead time.

**US-13: Progress supplier status**
> As a procurement manager, I want to move a supplier through the pipeline stages, recognizing that not all will make it to production.
>
> *Example*: "Fabric Co Ltd" moves OFFERED -> SAMPLING -> APPROVED -> IN_PRODUCTION -> IN_STORE. Meanwhile, "Budget Textiles" gets REJECTED after SAMPLING due to quality issues.

**US-14: Track sample sets**
> As a procurement manager, I want to record sample sets produced by each supplier, so that I can evaluate quality before committing to production.
>
> *Example*: Create a sample set for "Fabric Co Ltd" / "Stretch Skinny Jean" with date and initial status PENDING, later updated to APPROVED.

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                   │
│        Vite + TypeScript + Tailwind + TanStack Query  │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (REST/JSON)
┌──────────────────────▼──────────────────────────────┐
│                  API Layer (FastAPI)                   │
│   ┌──────────┐  ┌──────────┐  ┌────────────────┐    │
│   │ Routers  │→ │ Services │→ │ SQLAlchemy ORM │    │
│   │ (HTTP)   │  │ (Logic)  │  │ (Data Access)  │    │
│   └──────────┘  └──────────┘  └───────┬────────┘    │
└───────────────────────────────────────┼──────────────┘
                                        │ SQL
                       ┌────────────────▼─────────────┐
                       │     PostgreSQL Database        │
                       └───────────────────────────────┘
```

### Key Design Patterns

1. **Service Layer Pattern**: Routers handle HTTP concerns only (parsing requests, returning responses). All business logic, validation, and state transitions live in the service layer. This makes business rules testable independently of HTTP.

2. **Repository via ORM**: SQLAlchemy models serve as both domain entities and data access layer. For this scope, a separate repository pattern would be over-engineering.

3. **State Machine as Transition Maps**: Lifecycle and supplier state machines are implemented as simple dictionaries mapping `current_state -> set(valid_target_states)`. No external library needed for this complexity.

4. **Canonical Ordered Pairs for Incompatibility**: Attribute incompatibility is stored as `(min_id, max_id)` pairs with a CHECK constraint, eliminating duplicate inverse entries and simplifying queries.

5. **Pydantic Schema Separation**: Separate schemas for Create, Update, and Response per entity. Prevents over-posting and ensures clean API contracts.

6. **Feature-Based Frontend Organization**: React components grouped by domain feature (garments, suppliers) rather than by type (components, hooks, pages).

---

## 7. Features Detail

### 7.1 Garment Lifecycle Engine
- **Purpose**: Track garments through 5 development stages with validated transitions
- **Stages**: CONCEPT | DESIGN | DEVELOPMENT | SAMPLING | PRODUCTION
- **Operations**: Forward transition (advance one stage), backward transition (rework), query current stage
- **Key rules**: PRODUCTION is terminal (no exit), deletion blocked at PRODUCTION
- **UI**: Visual stepper component with colored stages, "Advance" / "Send Back" buttons

### 7.2 Attribute Incompatibility Engine
- **Purpose**: Prevent invalid attribute combinations on garments
- **Storage**: `attribute_incompatibilities` table with ordered pair constraint
- **Operations**: Define incompatibility rule, validate attribute assignment, list all rules
- **Validation flow**: On attribute assignment, query for conflicts between new attribute and all existing garment attributes; return conflicting attribute names in error message
- **Seed rules**: nightwear+activewear, formal+activewear, sleeveless+long_sleeve

### 7.3 Material Composition Tracker
- **Purpose**: Track which materials compose each garment and their percentages
- **Operations**: Add material with percentage, update percentage, remove material
- **Validation**: Total percentage per garment must not exceed 100%
- **UI**: Table showing material name and percentage, with add/remove controls

### 7.4 Design Evolution (Variations)
- **Purpose**: Track how garments evolve into new designs
- **Implementation**: Self-referential foreign key (`parent_garment_id`) on garments table
- **Operations**: Create variation from existing garment, list variations of a garment
- **UI**: "Variations" section in garment detail showing child garments, "Create Variation" button

### 7.5 Supplier Pipeline Manager
- **Purpose**: Manage multiple suppliers per garment through a qualification pipeline
- **Stages**: OFFERED | SAMPLING | APPROVED | REJECTED | IN_PRODUCTION | IN_STORE
- **Operations**: Associate supplier with garment (with offer), transition status, record sample sets
- **Key behavior**: Not all suppliers reach production -- REJECTED is an exit state available from OFFERED, SAMPLING, and APPROVED
- **UI**: Supplier table per garment with status badges, transition buttons, offer details

### 7.6 Sample Set Tracking
- **Purpose**: Record and track quality samples from suppliers
- **Scoped to**: garment-supplier association (not garment alone)
- **Statuses**: PENDING | RECEIVED | APPROVED | REJECTED
- **Operations**: Create sample set, update status, list per garment-supplier

---

## 8. Technology Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.110+ | Web framework / REST API |
| Uvicorn | 0.29+ | ASGI server |
| SQLAlchemy | 2.0+ | ORM / data access |
| Alembic | 1.13+ | Database migrations |
| Pydantic | 2.0+ | Request/response validation |
| pydantic-settings | 2.0+ | Configuration management |
| psycopg2-binary | 2.9+ | PostgreSQL driver |

### Database
| Technology | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 16+ | Primary database |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18+ | UI framework |
| TypeScript | 5.0+ | Type safety |
| Vite | 5.0+ | Build tool / dev server |
| Tailwind CSS | 3.4+ | Utility-first styling |
| TanStack Query | 5.0+ | Server state management |
| React Router | 6.0+ | Client-side routing |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| Docker Compose | PostgreSQL container |

---

## 9. Security & Configuration

### Security Scope
- ✅ **In scope**: Input validation via Pydantic, SQL injection prevention via ORM, CORS configuration
- ❌ **Out of scope**: Authentication, authorization, RBAC, rate limiting, HTTPS (per assessment: "No authentication/authorization required")

### Configuration Management
All configuration via environment variables with Pydantic Settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/fashion_plm` | PostgreSQL connection string |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `DEBUG` | `true` | Debug mode flag |

### `.env.example`
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fashion_plm
CORS_ORIGINS=["http://localhost:5173"]
DEBUG=true
```

---

## 10. API Specification

Base URL: `http://localhost:8000/api`

### Garments

#### `GET /api/garments`
List all garments with optional filters.

**Query Parameters**: `?stage=CONCEPT&search=tee`

**Response** `200`:
```json
[
  {
    "id": 1,
    "name": "Summer Breeze Tee",
    "description": "Lightweight cotton t-shirt",
    "lifecycle_stage": "DESIGN",
    "parent_garment_id": null,
    "created_at": "2026-02-15T10:00:00Z",
    "updated_at": "2026-02-15T12:00:00Z"
  }
]
```

#### `POST /api/garments`
Create a new garment (starts in CONCEPT).

**Request**:
```json
{
  "name": "Summer Breeze Tee",
  "description": "Lightweight cotton t-shirt"
}
```

**Response** `201`: Full garment object.

#### `GET /api/garments/{id}`
Get garment with all related data.

**Response** `200`:
```json
{
  "id": 1,
  "name": "Summer Breeze Tee",
  "description": "Lightweight cotton t-shirt",
  "lifecycle_stage": "DESIGN",
  "parent_garment_id": null,
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-15T12:00:00Z",
  "materials": [
    { "id": 1, "name": "cotton", "percentage": 60.0 },
    { "id": 2, "name": "polyester", "percentage": 40.0 }
  ],
  "attributes": [
    { "id": 1, "name": "short sleeve", "category": "SLEEVE_TYPE" },
    { "id": 5, "name": "casual", "category": "GARMENT_CATEGORY" }
  ],
  "suppliers": [
    { "supplier_id": 1, "supplier_name": "Fabric Co", "status": "SAMPLING", "offer_price": 12.50 }
  ],
  "variations": [
    { "id": 3, "name": "Summer Breeze Tee (Long Sleeve)", "lifecycle_stage": "CONCEPT" }
  ]
}
```

#### `PUT /api/garments/{id}`
Update garment name/description.

**Request**: `{ "name": "Updated Name" }`
**Response** `200`: Updated garment object.

#### `DELETE /api/garments/{id}`
Delete garment. Returns `403` if garment is in PRODUCTION.

**Response** `204` (success) or `403`:
```json
{ "error": "DELETION_PROTECTED", "detail": "Garment 'Classic Jacket' is in PRODUCTION stage and cannot be deleted." }
```

#### `POST /api/garments/{id}/transition`
Advance or revert lifecycle stage.

**Request**: `{ "target_stage": "DEVELOPMENT" }`

**Response** `200` (success) or `409`:
```json
{ "error": "INVALID_TRANSITION", "detail": "Cannot transition from CONCEPT to PRODUCTION. Valid transitions: ['DESIGN']" }
```

#### `POST /api/garments/{id}/variations`
Create a variation linked to parent garment.

**Request**: `{ "name": "Summer Breeze Tee (Long Sleeve)", "description": "Long sleeve variant" }`
**Response** `201`: New garment with `parent_garment_id` set.

#### `POST /api/garments/{id}/materials`
Add material to garment.

**Request**: `{ "material_id": 1, "percentage": 60.0 }`
**Response** `201`.

#### `POST /api/garments/{id}/attributes`
Assign attribute (validates incompatibilities).

**Request**: `{ "attribute_id": 3 }`

**Response** `201` (success) or `409`:
```json
{ "error": "INCOMPATIBLE_ATTRIBUTE", "detail": "Attribute 'activewear' is incompatible with existing attributes: nightwear" }
```

### Suppliers

#### `POST /api/garments/{id}/suppliers`
Associate supplier with garment.

**Request**:
```json
{ "supplier_id": 1, "offer_price": 12.50, "lead_time_days": 45, "notes": "Initial quote for bulk order" }
```

#### `POST /api/garments/{gid}/suppliers/{sid}/transition`
Transition supplier status.

**Request**: `{ "target_status": "SAMPLING" }`

**Response** `200` or `409` (invalid transition).

### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/materials` | List all materials |
| `POST` | `/api/materials` | Create material `{ "name": "silk" }` |
| `GET` | `/api/attributes` | List attributes `?category=SLEEVE_TYPE` |
| `POST` | `/api/attributes` | Create attribute `{ "name": "v-neck", "category": "NECKLINE" }` |
| `GET` | `/api/attributes/incompatibilities` | List all incompatibility rules |
| `POST` | `/api/attributes/incompatibilities` | Create rule `{ "attribute_id_1": 4, "attribute_id_2": 7 }` |
| `GET/POST/PUT/DELETE` | `/api/suppliers` | Full supplier CRUD |

### Sample Sets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/garments/{gid}/suppliers/{sid}/samples` | List sample sets |
| `POST` | `/api/garments/{gid}/suppliers/{sid}/samples` | Create sample `{ "notes": "First batch" }` |
| `PUT` | `/api/garments/{gid}/suppliers/{sid}/samples/{id}` | Update status `{ "status": "APPROVED" }` |

### Error Response Format
All errors follow a consistent structure:
```json
{
  "error": "ERROR_CODE",
  "detail": "Human-readable explanation"
}
```

| Code | HTTP Status | When |
|------|-------------|------|
| `NOT_FOUND` | 404 | Entity does not exist |
| `INVALID_TRANSITION` | 409 | Invalid state machine transition |
| `INCOMPATIBLE_ATTRIBUTE` | 409 | Attribute conflicts with existing |
| `DELETION_PROTECTED` | 403 | Attempting to delete PRODUCTION garment |
| `VALIDATION_ERROR` | 422 | Input validation failure |

---

## 11. Success Criteria

### MVP Success Definition
A working full-stack application where a user can create a garment, assign materials and attributes (with incompatibility checks), progress it through lifecycle stages, associate suppliers with offers, and see the system enforce all business rules.

### Functional Requirements
- ✅ Create, read, update, delete garments
- ✅ Lifecycle state machine validates all transitions (forward and backward)
- ✅ PRODUCTION garments cannot be deleted (returns 403)
- ✅ Materials assigned with percentages (total <= 100%)
- ✅ Attributes assigned with incompatibility validation
- ✅ Garment variations created with parent linkage
- ✅ Suppliers associated with garments including offers
- ✅ Supplier status transitions validated via state machine
- ✅ Sample sets recorded per garment-supplier pair
- ✅ Seed data populated on startup
- ✅ API fully documented via Swagger UI at `/docs`
- ✅ Frontend displays garment dashboard and detail views

### Quality Indicators
- Clean separation between routers (HTTP), services (logic), and models (data)
- Consistent error responses across all endpoints
- Type-safe frontend with TypeScript interfaces matching API contracts
- No N+1 query issues on garment detail endpoint (eager loading)

### User Experience Goals
- Dashboard provides at-a-glance view of all garments and their stages
- Garment detail page shows all related data in organized panels
- Business rule violations produce clear, actionable error messages
- Lifecycle and supplier status displayed as visual indicators

---

## 12. Implementation Phases

### Phase 1: Backend Foundation (~40 minutes)
**Goal**: Working database schema and FastAPI skeleton with all models.

**Deliverables**:
- ✅ Project setup (`pyproject.toml`, directory structure, `docker-compose.yml`)
- ✅ PostgreSQL running via Docker Compose
- ✅ `config.py` + `database.py` + `.env`
- ✅ All SQLAlchemy models (garments, materials, garment_materials, attributes, garment_attributes, attribute_incompatibilities, suppliers, garment_suppliers, sample_sets)
- ✅ All Pydantic schemas (create, update, response per entity)
- ✅ `exceptions.py` with custom exception hierarchy
- ✅ `main.py` with CORS, exception handlers, router includes

**Validation**: `uvicorn app.main:app --reload` starts without errors, tables created in PostgreSQL.

### Phase 2: Business Logic & API (~45 minutes)
**Goal**: All endpoints working with business rule enforcement.

**Deliverables**:
- ✅ `lifecycle.py` -- garment and supplier state machine transition maps
- ✅ `garment_service.py` -- CRUD, lifecycle transitions, deletion protection, variations
- ✅ `attribute_service.py` -- incompatibility validation, assignment
- ✅ `supplier_service.py` -- association, status transitions, sample sets
- ✅ All routers wired to services
- ✅ `seed.py` -- populate materials, attributes, incompatibility rules, sample suppliers

**Validation**: Full API testing via Swagger UI (`/docs`):
1. Create garment -> transitions through all stages -> attempt delete at PRODUCTION (blocked)
2. Assign attributes -> trigger incompatibility error
3. Associate supplier -> transition through pipeline -> create sample set

### Phase 3: Frontend (~25 minutes)
**Goal**: Working React UI for core flows.

**Deliverables**:
- ✅ Vite + React + TypeScript + Tailwind + TanStack Query + React Router setup
- ✅ API client (`lib/api.ts`) + TypeScript interfaces (`types/index.ts`)
- ✅ Dashboard page with garment cards (name, stage badge, action buttons)
- ✅ Garment detail page with lifecycle indicator, materials panel, attributes panel, suppliers panel
- ✅ Create garment form (modal)
- ✅ Stage filter on dashboard

**Validation**: Navigate dashboard -> click garment -> see detail panels -> create new garment -> transitions visible.

### Phase 4: Polish (~10 minutes)
**Goal**: Deliverable documentation and final verification.

**Deliverables**:
- ✅ `README.md` with setup instructions, architecture decisions, assumptions
- ✅ End-to-end smoke test of all critical flows
- ✅ Fix any integration issues discovered during testing

**Validation**: Fresh clone -> follow README -> system works end-to-end.

---

## 13. Future Considerations

### Post-MVP Enhancements
- **Audit trail**: Track all state changes with timestamps, actor, and reason
- **Image uploads**: Attach design sketches and tech packs to garments
- **Costing module**: Detailed cost breakdown per garment (materials, labor, shipping, margin)
- **Timeline/Gantt view**: Visual timeline of garment development with deadlines
- **Bulk operations**: Import/export garments and supplier data via CSV

### Integration Opportunities
- **ERP systems**: Sync production-ready garments to manufacturing systems
- **PLM tools**: Import from/export to industry-standard PLM platforms
- **Email notifications**: Alert procurement managers when supplier status changes
- **Slack/Teams**: Notify teams of lifecycle stage transitions

### Advanced Features
- **Role-based access**: Different permissions for designers, PMs, procurement
- **Approval workflows**: Require manager sign-off for stage transitions
- **Comparison view**: Side-by-side comparison of supplier offers
- **Analytics dashboard**: Pipeline velocity, rejection rates, time-to-production metrics
- **Version history**: Track all changes to garment specifications over time

---

## 14. Risks & Mitigations

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| 1 | **Time constraint** -- 1.5-2 hours may not cover full feature set | Medium | Prioritize backend domain model and business rules (highest architectural value). Frontend can be minimal but functional. Skip sample set UI and variation tree if needed. |
| 2 | **Complex state machines** -- bugs in transition validation could allow invalid states | High | Implement state machines as simple, testable dictionary lookups. Validate at service layer (not router). Use descriptive error messages that name valid transitions. |
| 3 | **Attribute incompatibility query performance** -- growing number of rules could slow assignment | Low | Canonical ordered pairs halve the data. Query uses indexed FKs. For MVP scale (< 50 rules), performance is not a concern. Could add caching later. |
| 4 | **Frontend-backend contract drift** -- TypeScript types diverging from Pydantic schemas | Medium | Define TypeScript interfaces to mirror Pydantic response schemas exactly. Use consistent naming conventions. FastAPI auto-generates OpenAPI spec that could generate TS types in future. |
| 5 | **PostgreSQL setup friction** -- reviewer may not have Docker installed | Low | Provide `docker-compose.yml` for one-command setup. Document SQLite fallback in README (SQLAlchemy makes this trivial by changing connection string). Include `Base.metadata.create_all` for zero-migration dev mode. |

---

## 15. Appendix

### Seed Data Reference

**Materials** (10):
denim, cotton, lycra, polyester, silk, wool, linen, nylon, viscose, cashmere

**Attributes** (15 across 5 categories):
| Category | Attributes |
|----------|-----------|
| SLEEVE_TYPE | long sleeve, short sleeve, sleeveless |
| NECKLINE | crew neck, v-neck, mock neck |
| GARMENT_CATEGORY | nightwear, activewear, casual, formal |
| FIT | slim, regular, oversized |
| FEATURE | with logo, with pocket, with zipper |

**Incompatibility Rules** (5):
| Attribute 1 | Attribute 2 | Rationale |
|------------|------------|-----------|
| nightwear | activewear | Conflicting use cases |
| formal | activewear | Conflicting use cases |
| sleeveless | long sleeve | Mutually exclusive sleeve types |
| short sleeve | long sleeve | Mutually exclusive sleeve types |
| short sleeve | sleeveless | Mutually exclusive sleeve types |

### Entity Relationship Diagram

```
                    ┌────────────┐
                    │  materials │
                    └─────┬──────┘
                          │
                  garment_materials [%]
                          │
┌──────────┐       ┌──────┴──────┐       ┌────────────┐
│ garments │◄──────│   garments  │       │ attributes │
│ (parent) │ 1───* │   (child)   │       └─────┬──────┘
└──────────┘       └──────┬──────┘             │
                          │           garment_attributes
                          │                    │
                          ├────────────────────┘
                          │
                 garment_suppliers [status, price]
                          │                         attribute_incompatibilities
                   ┌──────┴──────┐                  [attr_1, attr_2]
                   │  suppliers  │
                   └──────┬──────┘
                          │
                    sample_sets [status]
```
