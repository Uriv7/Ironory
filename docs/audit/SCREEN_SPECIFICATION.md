# Ironory — Complete Screen & User Journey Specification

**Document ID:** IRONORY-AUD-003  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Target Architecture:** Next.js 14 App Router + Tailwind CSS + Lucide Icons  
**Audit Date:** 2026-11-16  

---

## 1. Screen Inventory & Route Mapping

| Route | Screen Name | Role Requirement | Production Status | Primary API Dependencies |
|---|---|---|---|---|
| `/` | Enterprise Operations Dashboard | All Authenticated | **Implemented** | `GET /analytics/overview`, `GET /inspections?limit=10` |
| `/login` | Secure User Login | Public | **Implemented** | `POST /auth/login` |
| `/register` | Tenant Onboarding & Org Registration | Public | **Implemented** | `POST /auth/register` |
| `/forgot-password` | Password Recovery Request | Public | **Implemented** | `POST /auth/forgot-password` |
| `/products` | Industrial Part Catalog | All Authenticated | **Implemented** | `GET /products` |
| `/products/new` | Product Registration & DL Thresholds | Admin / Quality Mgr | **Implemented** | `POST /products` |
| `/inspections` | Ingest Center (Single & Batch) | Inspector+ | **Implemented** | `POST /inspections`, `POST /inspections/batch` |
| `/inspections/[id]` | Inspection Detail & Human Review | Inspector+ | **Implemented** | `GET /inspections/{id}`, `POST /inspections/{id}/review` |
| `/analytics` | Defect Telemetry & Yield Trends | All Authenticated | **Implemented** | `GET /analytics/defect-distribution` |
| `/reports` | ISO Compliance & CSV Export Center | All Authenticated | **Implemented** | `GET /inspections/export/csv`, `GET /inspections/{id}/report` |
| `/models` | AI Model Registry & Benchmarks | All Authenticated | **Implemented** | `GET /models` (Local catalog) |
| `/team` | Organization Team & RBAC Invites | Admin / Owner | **Implemented** | `GET /organizations/members`, `POST /organizations/invitations` |
| `/settings` | Tenant Profile & Pipeline Settings | Admin / Owner | **Implemented** | `GET /organizations/me`, `PATCH /organizations/me` |
| `/admin/*` | Platform Super Admin Portal | Super Admin | **Backlog (P1)** | `GET /admin/organizations`, `GET /admin/audit-logs` |
| `localhost:8501` | Streamlit Academic Portal (INT422) | Academic Evaluators | **Implemented** | Direct Python ML Engine / Model Artifacts |

---

## 2. Detailed Screen Specifications

### 2.1 Ingest Center & Batch Processing (`/inspections`)
- **Primary Purpose:** Factory floor terminal for ingesting high-resolution surface scan visual assets (steel sheets, machined parts). Supports single drag-and-drop and batch ingest up to 20 frames per run.
- **Layout & Structure:**
  - Header: Ingest pipeline status, active product selector, line designation tag.
  - Main Panel: Drag-and-drop dropzone with dashed border, accepted formats (`.png`, `.jpg`, `.jpeg`), size limit (15MB).
  - Batch Queue Table: Real-time file upload list with thumbnail, byte size, ingest status, and progress indicators.
  - Action Bar: "Run AI Quality Scan", "Clear Queue", "Select Camera Feed".
- **States:**
  - *Empty:* Industrial placeholder illustration prompting operator to drop surface scan images.
  - *Loading:* Pulse animation with circular spinner and inference elapsed timer.
  - *Success:* Automated redirection to batch results or inspection detail view.
  - *Error:* Red alert banner displaying validation errors (e.g., unsupported format, oversized image).

### 2.2 Inspection Detail & Human Review (`/inspections/[id]`)
- **Primary Purpose:** Interactive defect validation console. Operators and Quality Managers inspect the original high-resolution frame alongside Grad-CAM heatmaps, bounding box coordinates, and defect class probabilities.
- **Key Components:**
  - Dual-pane image comparator: Toggle between Original Raw Asset, Grad-CAM Explainability Heatmap, and Bounding Box Overlay.
  - Telemetry Card: Predicted Defect Class, Confidence Score (0-100%), Anomaly Score, Inference Latency (ms), Target Product SKU.
  - Human Review Console (RBAC Gated):
    - "Confirm AI Verdict": Records `CONFIRMED` decision into database.
    - "Override Verdict": Dropdown selecting correct defect class (e.g., Patches, Inclusions, Scratches) + mandatory audit justification text field.
    - "Generate Signed PDF Certificate": Downloads official inspection report.

### 2.3 Quality Analytics & Defect Trends (`/analytics`)
- **Primary Purpose:** Executive and managerial yield monitoring.
- **Key Metrics & Charts:**
  - Cumulative Defect Rate (%) and First Pass Yield (FPY).
  - Defect Class Distribution: Bar chart breaking down occurrences across Crazing, Inclusion, Patches, Pitted Surface, Rolled-in Scale, and Scratches.
  - Daily Inspection Throughput: Line chart illustrating daily volume and pass/fail ratios.
  - Filter Controls: Date range picker (7d, 30d, 90d), product line filter, severity filter.

### 2.4 Reports & Compliance Center (`/reports`)
- **Primary Purpose:** ISO 9001 quality audit export and traceability.
- **Capabilities:**
  - One-click CSV Audit Log Export (`GET /api/v1/inspections/export/csv`): Emits RFC-4180 compliant CSV including timestamps, tenant IDs, operator names, model versions, predicted classes, confidence, and human review decisions.
  - Batch PDF Export: Queue batch PDF generation for formal customer documentation.

### 2.5 AI Model Registry (`/models`)
- **Primary Purpose:** Transparency into deployed deep learning architectures.
- **Components:**
  - Model Cards for:
    - Custom Baseline CNN (4 Convolutional Blocks + BatchNorm + Dropout, 98.6% Accuracy).
    - MobileNetV2 (Inverted Residuals, Edge-Optimized).
    - EfficientNet-B0 (Compound Scaling).
    - Convolutional Autoencoder (MSE Reconstruction Anomaly Detection).
    - DCGAN (Synthetic Defect Augmentation).
    - Bi-directional Forecast LSTM (Time-series defect rate projection).
  - Performance Metrics: Parameter count, inference latency on CPU/GPU, Top-1 accuracy, F1-score.

---

## 3. Industrial UX & Ergonomics Guidelines

1. **High-Contrast Dark Theme:** Defaulting to Slate-900 / Navy-950 palette prevents eye strain under bright manufacturing floor lighting and highlights visual defect color maps (red/amber heatmaps).
2. **Keyboard Accelerators:** For rapid factory line review, operators should be able to trigger verdicts using keys: `C` (Confirm), `O` (Override), `Space` (Toggle Heatmap).
3. **Optimistic Updates:** Immediate visual state updates upon review action with automatic background sync and rollback on network failure.
