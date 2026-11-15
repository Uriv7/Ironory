# Ironory — AI Industrial Quality Inspection SaaS

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![PostgreSQL 14](https://img.shields.io/badge/PostgreSQL-14-blue.svg)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)]()

> **Detect Defects. Ensure Quality. Build Trust.**  
> An enterprise-grade B2B SaaS platform for automated visual surface inspection and quality management using deep learning and computer vision.  
> Developed as both an academic Deep Learning project for **INT422** and a commercial B2B SaaS product.

---

## 1. System Architecture

Ironory is engineered as a modular multi-tenant system:

```
                                  +-------------------------------------------------------------+
                                  |                         Ironory UI                          |
                                  |         Next.js 14 (App Router) + TypeScript + Tailwind     |
                                  |            Full-Width Industrial Operations Console         |
                                  +------------------------------+------------------------------+
                                                                 |
                                                          REST API / JWT
                                                                 |
                                  +------------------------------v------------------------------+
                                  |                     FastAPI Backend                         |
                                  |           Authentication, Multi-Tenant RBAC,                |
                                  |           Product & Inspection Management,                  |
                                  |           Analytics Engine, PDF Report Generator            |
                                  +--------------+---------------+--------------+---------------+
                                                 |               |              |
                      +--------------------------+               |              +--------------------------+
                      |                                          |                                         |
+---------------------v---------------------+  +-----------------v-----------------+  +--------------------v--------------------+
|         PostgreSQL Database               |  |     Pluggable Storage Layer       |  |       AI Inference Service              |
| Relational schema with tenant isolation,  |  |  Local filesystem storage adapter |  | Real TensorFlow 2.x / Keras pipelines:  |
| indexed UUIDs, audit trails, and foreign  |  |  with tenant path partitioning:   |  | Baseline CNN, MobileNetV2,              |
| key integrity                             |  |  /storage/tenants/{org_id}/...    |  | Autoencoder, U-Net, DCGAN, LSTM         |
+-------------------------------------------+  +-----------------------------------+  +--------------------+--------------------+
                                                                                                           ^
                                                                                                           |
                                              +------------------------------------------------------------+
                                              |
                               +--------------+---------------+
                               |  Streamlit Academic Demo App |
                               |   INT422 Curriculum Pages    |
                               |  Reuses shared model weights |
                               +------------------------------+
```

---

## 2. Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router), React 18
- **Language:** TypeScript (Strict mode)
- **Styling:** Tailwind CSS, Custom Industrial Design Tokens (Deep Navy `#0B132B`, Slate, Electric Blue `#0EA5E9`)
- **Icons:** Lucide React
- **Client:** Native Fetch API client with structured error handling and correlation ID tracing

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Validation:** Pydantic v2 & Pydantic-Settings
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Database Driver:** `psycopg2-binary` / `asyncpg`
- **Testing:** Pytest, pytest-asyncio, HTTPX

### Database & Storage
- **Primary Database:** PostgreSQL 14+
- **Multi-Tenancy:** Tenant isolation enforced via `organization_id` foreign keys and compound unique constraints
- **Storage:** Local filesystem adapter with tenant partitioning, filename sanitization, and path-traversal prevention

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Scripting:** Shell automation scripts (`infrastructure/scripts/`)

---

## 3. Repository Structure

```
Ironory/
├── frontend/                     # Next.js 14 App Router frontend
│   ├── app/                      # App router layouts and pages
│   ├── components/               # Reusable UI (Button, Card, Input, Table, EmptyState, etc.)
│   ├── lib/                      # API client and utility helpers
│   ├── Dockerfile                # Multi-stage production container
│   └── package.json
├── backend/                      # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/               # Versioned API endpoints (health, ready, system info)
│   │   ├── core/                 # Config, structured logging, exception handlers
│   │   ├── db/                   # Database engine, session, Alembic migrations
│   │   ├── models/               # SQLAlchemy models (User, Organization, Membership)
│   │   ├── repositories/         # Database persistence repositories
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Storage service abstraction and local adapter
│   │   └── middleware/           # Correlation ID tracing middleware
│   ├── alembic/                  # Database migration versions
│   ├── tests/                    # Pytest automated test suite
│   ├── Dockerfile                # Production Python 3.11 container
│   └── requirements.txt
├── ml/                           # Deep learning pipelines (Phases 4 & 5)
├── streamlit_app/                # Academic demonstration interface (Phase 7)
├── infrastructure/
│   ├── docker/                   # Docker deployment configurations
│   └── scripts/                  # dev.sh, test.sh launcher scripts
├── storage/                      # Local development file storage (excluded from git)
├── docker-compose.yml            # Multi-container orchestration (DB, Redis, Backend, Frontend)
├── .env.example                  # Environment configuration template
├── FEATURE_TICKET_LIST.md        # Master 90-ticket tracking board
├── ARCHITECTURE_DECISIONS.md     # Architecture Decision Records (ADRs)
└── IMPLEMENTATION_LOG.md         # Detailed chronological development audit
```

---

## 4. Prerequisites

- **macOS** or **Linux**
- **Python 3.11** (Required for TensorFlow binary compatibility; system Python 3.14 is incompatible)
- **Node.js v20+** (Tested on Node `v22.23.2` and npm `10.9.8`)
- **PostgreSQL 14+** (Locally installed or containerized)
- **Docker & Docker Compose** (Optional for containerized execution)

---

## 5. Local Setup & Installation

### Step 1: Clone and Configure Environment
```bash
git clone <repo-url> Ironory
cd Ironory
cp .env.example .env
```

Ensure your `.env` contains your PostgreSQL credentials:
```bash
DATABASE_URL=postgresql://satendergupta@localhost:5432/visioninspect
TEST_DATABASE_URL=postgresql://satendergupta@localhost:5432/visioninspect_test
```

### Step 2: Database Initialization
Create the development and test databases:
```bash
psql -d postgres -c "CREATE DATABASE visioninspect;"
psql -d postgres -c "CREATE DATABASE visioninspect_test;"
```

### Step 3: Automated Launch (Recommended)
Run the all-in-one local development launcher:
```bash
./infrastructure/scripts/dev.sh
```
This script will:
1. Initialize the Python 3.11 virtual environment (`.venv`).
2. Install Python dependencies.
3. Run Alembic migrations to `head`.
4. Launch FastAPI on `http://localhost:8000`.
5. Launch Next.js on `http://localhost:3000`.

---

## 6. Manual Execution Commands

### Backend API
```bash
# Activate virtual environment
source .venv/bin/activate

# Apply migrations
alembic -c backend/alembic.ini upgrade head

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
- API Root: `http://localhost:8000/`
- Interactive Swagger UI: `http://localhost:8000/api/v1/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`
- Readiness Endpoint: `http://localhost:8000/api/v1/ready`

### Frontend Application
```bash
cd frontend
npm install
npm run dev
```
- Operations Dashboard: `http://localhost:3000/`

---

## 7. Verification & Testing

Execute the comprehensive automated test suite:
```bash
./infrastructure/scripts/test.sh
```

Or run individual test runners:
```bash
# Backend pytest suite (10 unit/integration tests)
.venv/bin/pytest backend/tests -v

# Frontend TypeScript check
cd frontend && npm run type-check

# Frontend Production Build verification
cd frontend && npm run build
```

---

## 8. Docker Deployment

To launch Ironory via Docker Compose:
```bash
docker compose up --build
```

> **Note on Docker Daemon:** If your Docker daemon is not active (`dial unix /Users/.../.docker/run/docker.sock: connect: no such file or directory`), start Docker Desktop or execute via native commands as documented in Section 5.

---

## 9. Current Implementation Status

- **Phase 0 (Audit & Planning):** Completed (`VISION-001`, `VISION-002`).
- **Phase 1 (Project Foundation):** Completed (`VISION-003`, `VISION-004`, `VISION-005`, `VISION-078` scaffolding).
- **Next Milestone:** Phase 2 (Authentication, JWT Token Lifecycle, Multi-Tenant RBAC, Organization Invitations).
