# Ironory — Architecture Decisions (ADR)

**Product Name:** Ironory  
**Document Version:** 1.1  
**Date:** 2026-11-16  
**Status:** Approved & Verified (Phase 1 Foundation Active)  

---

## 1. System Overview & Context

Ironory is an enterprise-grade B2B SaaS platform for industrial visual quality inspection combining:
1. An academic deep learning system demonstrating core INT422 concepts (CNNs, Transfer Learning, Autoencoders, U-Net Segmentation, GANs, LSTM forecasting).
2. A commercial multi-tenant SaaS architecture supporting manufacturing organizations with strict tenant isolation, role-based access control, persistent inspection records, real-time analytics, and automated PDF reporting.

---

## 2. Architecture Decision Records (ADRs)

### ADR-001: Technology Stack Selection
- **Frontend:** Next.js 14+ (App Router), React 18, TypeScript (Strict), Tailwind CSS, Lucide icons, Recharts for responsive analytics, React Hook Form + Zod for validation.
- **Backend:** FastAPI (Python 3.11 runtime), Pydantic v2, SQLAlchemy 2.0, Alembic migrations.
- **Database:** PostgreSQL 14+; normalized schema with UUID primary keys, foreign keys, compound unique constraints, and indexes.
- **Deep Learning / AI:** TensorFlow 2.x, Keras, NumPy, OpenCV (headless), Scikit-learn, Matplotlib, TensorBoard.
- **Academic Demo:** Streamlit multi-page application consuming the exact same trained model artifacts and preprocessing pipelines as the FastAPI backend.
- **Object Storage:** Pluggable storage abstraction supporting local file system adapter (`storage/tenants/`) with safe tenant path partitioning and future S3-compatible cloud storage adapter.

### ADR-002: Multi-Tenancy & Tenant Isolation
- **Pattern:** Shared database with discriminator column (`organization_id`) on all tenant-owned entities.
- **Enforcement:**
  - Database level: Foreign keys, compound unique constraints `(organization_id, product_code)`, unique constraints on `(user_id, organization_id)`, indexes on `organization_id`.
  - Backend level: Dependency injection via FastAPI `get_current_tenant_user`, ensuring all database queries in repositories automatically filter by `organization_id`.
  - Storage level: S3/local paths partitioned as `storage/tenants/{tenant_id}/{subfolder}/{sanitized_uuid_filename}`.
  - No client-provided `organization_id` is trusted for authentication or querying.

### ADR-003: Role-Based Access Control (RBAC)
- **Platform Level:**
  - `SUPER_ADMIN`: Cross-tenant platform management, global model registry, system telemetry.
  - `PLATFORM_SUPPORT`: Read-only access to customer support diagnostics upon explicit authorization.
- **Organization Level:**
  - `OWNER`: Full organization control, billing, invitations, settings.
  - `ADMIN`: User management, product configuration, reports.
  - `QUALITY_MANAGER`: Quality review, approve/override AI predictions, defect threshold configuration.
  - `INSPECTOR`: Image upload, run inspections, submit review requests.
  - `READ_ONLY`: View dashboards and inspection records.

### ADR-004: AI Model Architecture & Inference Pipeline
- **Strict Real Inference Rule:** No mock or random prediction functions in production inference.
- **Datasets:**
  - NEU Surface Defect Database (6 surface defect classes: Crazing, Inclusion, Patches, Pitted Surface, Rolled-in Scale, Scratches).
  - MVTec Anomaly Detection benchmark dataset for Autoencoder reconstruction and anomaly maps.
- **Model Hierarchy:**
  1. *Model A (Baseline CNN):* Custom convolutional network (Conv2D, BatchNormalization, ReLU, MaxPool2D, Dropout, Dense) trained from scratch.
  2. *Model B (Transfer Learning):* MobileNetV2 / EfficientNetB0 with ImageNet pretrained weights, fine-tuned dense classification head, comparing loss and accuracy curves.
  3. *Model C (Convolutional Autoencoder):* Encoder-decoder network trained on defect-free samples; reconstruction error exceeding calibrated threshold flags anomaly.
  4. *Model D (U-Net Segmentation):* Encoder-decoder with skip connections predicting pixel-level defect masks.
  5. *Model E (DCGAN Experimental):* Generator and discriminator for synthetic surface defect generation with adversarial loss logging.
  6. *Model F (LSTM Forecasting):* Sequential defect rate trend analysis over inspection time windows.
- **Model Persistence & Artifacts:** All models saved in standard Keras format (`.keras` / `.h5`) with structured evaluation metadata (`model_metadata.json`), version tags, test metrics, and checksums.

### ADR-005: Database Schema Architecture
Entities implemented in Phase 1:
- `users`: Core account details, email (normalized, unique), hashed password, active status, super admin flag.
- `organizations`: Tenant profiles, name, slug (unique, indexed), industry, contact email, logo URL.
- `organization_memberships`: User-organization mapping with assigned RBAC roles (`OWNER`, `ADMIN`, `QUALITY_MANAGER`, `INSPECTOR`, `READ_ONLY`) and compound unique constraint `(user_id, organization_id)`.

### ADR-006: Asynchronous Processing & Correlation ID Tracing
- `CorrelationIdMiddleware` assigns or preserves `X-Correlation-ID` header on all incoming requests.
- Structured logging formats output with correlation ID for distributed tracing across services.
- FastAPI endpoints accept image uploads, validate MIME/dimensions, persist database records with status `QUEUED`, and trigger asynchronous background processing.
