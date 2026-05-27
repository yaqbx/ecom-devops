# Architecture Overview

## System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│               nginx (localhost:8080)                             │
│               HTML/CSS/JS                                        │
└────┬─────────┬──────────┬──────────┬──────────┬─────────────────┘
     │         │          │          │          │
     │ 3000    │ 8000     │ 8001     │ 8100     │
     ▼         ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Product  │ │User     │ │Checkout │ │Payment  │
│Catalog  │ │Mgmt     │ │Service  │ │Mock     │
│(Node.js)│ │(Django) │ │(FastAPI)│ │(FastAPI)│
├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤
│Port 3000│ │Port 8000│ │Port 8001│ │Port 8100│
└────┬────┘ └────┬────┘ └────┬────┘ └─────────┘
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ MongoDB │ │PostgreSQL│ │  Redis  │
│equip-   │ │user_    │ │ Checkout│
│ment_cat.│ │management│ │ data    │
└─────────┘ └─────────┘ └─────────┘
```

## Service Breakdown

### 1. Product Catalog — Node.js/Express (port 3000)

| Detail | Value |
|--------|-------|
| **Stack** | Express 4, Mongoose 8, Winston, Helmet |
| **Database** | MongoDB (`equipment_catalog.equipments`) |
| **Purpose** | CRUD for heavy equipment inventory, search, categories |
| **Endpoints** | `GET/POST/PUT/DELETE /api/v1/equipment`, `GET /api/v1/search`, `GET /api/v1/categories`, `GET /health` |
| **Seed data** | 38 items across 11 categories: excavators, bulldozers, cranes, loaders, dump_trucks, compactors, graders, forklifts, aerial_lifts, concrete_equipment, attachments |

### 2. User Management — Django/DRF (port 8000)

| Detail | Value |
|--------|-------|
| **Stack** | Django 4.2, DRF, PostgreSQL, SimpleJWT |
| **Database** | PostgreSQL (`user_management`) |
| **Purpose** | User registration, login, role-based access, JWT auth |
| **Endpoints** | `POST /api/v1/users/login/`, `POST /api/v1/users/`, `GET/PUT/DELETE /api/v1/users/{id}`, `POST /api/v1/token/`, `POST /api/v1/token/refresh/` |
| **Auth** | Session + JWT (Bearer tokens). Login returns `access` + `refresh` tokens alongside user data. |
| **Seed data** | 15 users: 1 admin, 3 company admins, 2 company managers, 4 operators, 5 customers. Password: `Test1234!` |
| **Companies/Rentals** | Stub apps (`__init__.py` only) — not implemented |

### 3. Checkout Service — FastAPI (port 8001)

| Detail | Value |
|--------|-------|
| **Stack** | FastAPI 0.109, Pydantic 2, Redis, httpx |
| **Database** | Redis (persistent storage for quotes, orders, delivery schedules) |
| **Purpose** | Quote generation, order management, delivery scheduling, payment integration |
| **Endpoints** | Quotes (`POST/GET /api/v1/quotes/`), Orders (`POST/GET /api/v1/orders/`), Delivery (`POST/GET /api/v1/delivery/`), `GET /health` |
| **Data persistence** | All data stored in Redis as JSON with `quote:`, `order:`, `delivery:` key prefixes. TTL 90 days. |

### 4. Mock Payment Service — FastAPI (port 8100)

| Detail | Value |
|--------|-------|
| **Stack** | FastAPI, Pydantic, in-memory dict |
| **Purpose** | Simulated payment authorization, capture, refund. No real payment provider. |
| **Endpoints** | `POST /api/v1/payments/authorize`, `POST /api/v1/payments/capture`, `POST /api/v1/payments/refund`, `GET /api/v1/payments/{id}` |
| **Behavior** | ~5% random failure rate. Special card tokens for testing: `4111111111111111` → declined, `4000000000000005` → insufficient funds, `4000000000000069` → expired |

## Database per Service (Polyglot Persistence)

| Service | Database | Type | Why |
|---------|----------|------|-----|
| Product Catalog | MongoDB | Document store | Equipment items have deeply nested, variable schemas (specs, pricing, availability). Document model fits naturally. |
| User Management | PostgreSQL | Relational | Users have strict relations (roles, permissions, future companies). ACID for auth. |
| Checkout Service | Redis | Key-value | Quote/order data is short-lived, high-throughput, needs TTL expiry. Redis handles this natively. |

Each database is **in-cluster** (embedded in the Docker Compose stack or K8s namespace). No external managed databases.

## Inter-service Communication

```
┌──────────────┐     HTTP     ┌──────────────────┐
│  Checkout    │─────────────►│  Product Catalog  │
│  Service     │  GET /api/v1/│  (port 3000)      │
│  (port 8001) │  equipment/  │  Fetch real       │
│              │  {id}        │  pricing.         │
└──────┬───────┘              └──────────────────┘
       │
       │  HTTP
       │  GET /api/v1/users/{id}
       ▼
┌──────────────┐
│  User Mgmt   │
│  (port 8000) │
│  Validate    │
│  customer    │
└──────────────┘

┌──────────────┐     HTTP     ┌──────────────────┐
│  Checkout    │─────────────►│  Mock Payment    │
│  Service     │  POST /api/v1│  (port 8100)     │
│              │  payments/   │  Authorize on    │
│              │  authorize   │  order confirm.  │
└──────────────┘              └──────────────────┘
```

Service URLs are configured via environment variables:

```yaml
PRODUCT_CATALOG_URL: "http://product-catalog:3000"
USER_MANAGEMENT_URL: "http://user-management:8000"
PAYMENT_MOCK_URL: "http://payment-mock:8100"
```

## Frontend

- **Served by**: nginx (static files) — added if needed for K8s deploy
- **Local access**: `index.html` opened directly or served via `python -m http.server`
- **Architecture**: Single-page application (vanilla JS, no framework)
- **Pages**: Equipment catalog, user login/register, quote creation, order tracking
- **API calls**: Direct fetch to each service's port (browser → localhost:XXXX)

## End-to-End Flow

```
1. User browses equipment catalog         → GET /api/v1/equipment (port 3000)
2. User registers                          → POST /api/v1/users/ (port 8000)
3. User logs in                            → POST /api/v1/users/login/ → JWT tokens
4. User requests quote                     → POST /api/v1/quotes/ (port 8001)
   │
   ├─ Checkout fetches real pricing        → GET /api/v1/equipment/{id} (port 3000)
   └─ Checkout validates customer          → GET /api/v1/users/{id} (port 8000)
5. User accepts quote                      → POST /api/v1/quotes/{id}/accept
6. User creates order                      → POST /api/v1/orders/?quote_id=...&customer_id=...
7. User confirms order (payment)           → POST /api/v1/orders/{id}/confirm
   │
   └─ Checkout authorizes payment          → POST /api/v1/payments/authorize (port 8100)
8. Admin cancels order (refund)            → POST /api/v1/orders/{id}/cancel
   │
   └─ Checkout refunds payment             → POST /api/v1/payments/refund (port 8100)
```

## Development Setup (Docker Compose)

**Start:**
```bash
cd apps/
docker compose up --build
```

This starts 7 containers: 4 services + 3 databases, all on `equipment-network`.

**Access points:**

| Service | URL | Auth |
|---------|-----|------|
| Product Catalog API | http://localhost:3000 | None |
| User Management API | http://localhost:8000 | JWT + Session |
| Checkout Service API | http://localhost:8001 | None (internally validates via User Mgmt) |
| Mock Payment API | http://localhost:8100 | None |
| Swagger UI (Checkout) | http://localhost:8001/docs | None |
| Django Admin | http://localhost:8000/admin/ | JWT + Session |
| Frontend | Open `apps/frontend/index.html` directly | JWT in localStorage |

**Seeds run automatically on compose up:**
- MongoDB: 38 equipment items (`node scripts/seed-data.js`)
- PostgreSQL: 15 users (`python manage.py seed_users`)

**Test users (all passwords: `Test1234!`):**

| Email | Role |
|-------|------|
| admin@ecomdevops.com | Platform Admin |
| k.nowak@budex.pl | Company Admin |
| anna.jankowska@gmail.com | Individual Customer |
| marek.kaminski@gmail.com | Individual Customer |

## Deployment Target (Future)

- **AWS EKS** cluster with `t3.micro` nodes
- **Helm charts** for each service + database (in `charts/`)
- **ArgoCD** for GitOps sync (in `argocd/`)
- **Per-service values** in `helmfiles/`
- Service type: `ClusterIP` (internal only, no Ingress yet)

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Database per service** | Independent scaling, no shared schema coupling, each picks the right DB type |
| **Redis for checkout** | Quotes/orders are ephemeral; TTL handles cleanup; fast reads/writes |
| **Mock payment** | No real merchant account needed; special card tokens enable testing decline/fail scenarios |
| **JWT + Session auth** | Session for Django Admin, JWT for API clients (frontend, mobile) |
| **Inter-service HTTP** | Simple, synchronous, debuggable. For production, consider async (message queue) for resilience |
| **Vanilla JS frontend** | No build step, zero dependencies, demonstrates API integration clearly for learning purposes |
