# Ironory — Master Production Implementation Roadmap

**Document ID:** IRONORY-AUD-010  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Lead Product Manager & Principal Architect:** Executive Engineering Consortium  
**Target:** Enterprise Production Release 1.0 (GA)  
**Audit Date:** 2026-11-16  

---

## 1. Roadmap Strategic Phases Overview

| Phase | Strategic Focus | Target Duration | Effort (Person-Days) | Key Deliverable |
|---|---|:---:|:---:|---|
| **Phase 1** | **Critical Blockers & Packaging** | Weeks 1 - 2 | 14 days | Multi-stage Docker, Async Celery Queue, Frontend Token Interceptor, Audit Alembic Migration |
| **Phase 2** | **RBAC Hardening & Review Workflow** | Weeks 3 - 4 | 16 days | Quality Manager signature workflow, session revocation, automated audit trail |
| **Phase 3** | **Multi-Model ML Artifacts & Robustness** | Weeks 5 - 6 | 18 days | Fine-tuned weights for MobileNetV2, EfficientNet, U-Net; automated drift monitoring |
| **Phase 4** | **Industrial Edge Ingest & Live Streaming** | Weeks 7 - 8 | 20 days | WebSocket live feeds, RTSP factory camera ingest, edge caching |
| **Phase 5** | **Enterprise SaaS & Multi-Tenancy** | Weeks 9 - 10 | 22 days | Stripe subscription billing, usage metering, SSO / SAML 2.0 integration |
| **Phase 6** | **SRE Observability & Security Hardening** | Weeks 11 - 12 | 15 days | Prometheus/Grafana dashboards, Locust load testing, external penetration testing |

---

## 2. Phase-by-Phase Execution Details

### Phase 1: Critical Blockers & Production Packaging
- **Goal:** Eliminate container crashes and request starvation under factory load.
- **Backlog Tickets:**
  - `IRONORY-OPS-001`: Refactor `backend/Dockerfile` to include `ml/` package and ML runtime dependencies (`tensorflow`, `reportlab`, `opencv-python-headless`).
  - `IRONORY-INS-001`: Decouple inspection execution from HTTP request loop using Redis / Celery background workers returning `HTTP 202 Accepted`.
  - `IRONORY-UI-001`: Implement automatic JWT and tenant header interceptors in `frontend/lib/api-client.ts`.
  - `IRONORY-DATA-001`: Generate and apply Alembic migration revision for `audit_logs` table.
- **Acceptance Gate:** `docker compose up --build` launches cleanly without manual volume hacks; batch uploads execute asynchronously in background.

### Phase 2: RBAC Hardening & Human Review Governance
- **Goal:** Ensure full ISO 9001 compliance for human sign-offs and security isolation.
- **Backlog Tickets:**
  - `IRONORY-SEC-001`: Implement sliding window session revocation via Redis blacklist.
  - `IRONORY-AUD-002`: Wire FastAPI middleware to automatically log all mutations to `audit_logs`.
  - `IRONORY-INS-002`: Enforce Quality Manager signature requirement before overriding AI verdict on critical safety parts.
- **Acceptance Gate:** Negative RBAC tests pass with 100% rejection rate for unauthorized actions; audit log records actor, IP, timestamp, and diff.

### Phase 3: Multi-Model ML Artifacts & Explainability
- **Goal:** Complete the AI model registry with verified fine-tuned weights on disk.
- **Backlog Tickets:**
  - `IRONORY-ML-001`: Execute transfer learning fine-tuning pipelines and persist `mobilenet_v2.keras` and `efficientnet_b0.keras` in `ml/artifacts/`.
  - `IRONORY-ML-002`: Train U-Net segmentation model and save `unet.keras` for direct pixel-level defect masks.
  - `IRONORY-ML-003`: Implement Temperature Scaling calibration to align softmax probabilities with empirical defect frequencies.
  - `IRONORY-ML-004`: Implement automated data drift monitoring using population stability index (PSI).
- **Acceptance Gate:** All models in the registry have verified weights files on disk with test accuracy $> 97.5\%$.

### Phase 4: Industrial Edge Ingest & Streaming
- **Goal:** Enable direct connectivity to factory floor optical sensors and cameras.
- **Backlog Tickets:**
  - `IRONORY-INS-003`: WebSocket endpoint (`ws://.../inspections/live`) for real-time progress broadcast.
  - `IRONORY-INS-004`: RTSP / GenICam streaming connector for industrial GigE cameras (Basler, FLIR).
  - `IRONORY-OPS-002`: Local edge caching service with LRU pruning for remote plant deployments.
- **Acceptance Gate:** Real-time camera feed processes 10 FPS with UI latency $< 150\text{ ms}$.

### Phase 5: Enterprise SaaS, Billing & SSO
- **Goal:** Enable commercial B2B monetization and enterprise identity federation.
- **Backlog Tickets:**
  - `IRONORY-BILL-001`: Stripe integration for tiered subscription plans (Starter, Professional, Enterprise).
  - `IRONORY-BILL-002`: Usage tracking and automated throttling when inspection quotas are exceeded.
  - `IRONORY-SEC-002`: SAML 2.0 / Okta SSO integration for enterprise user provisioning.
- **Acceptance Gate:** Enterprise customers can log in via corporate SSO and are billed accurately per inspection volume.

### Phase 6: SRE Observability & Release Hardening
- **Goal:** Guarantee 99.9% uptime SLA and resistance to cyber attacks.
- **Backlog Tickets:**
  - `IRONORY-OPS-003`: Prometheus metrics exporter (`/metrics`) instrumenting inference latency, queue depth, and HTTP error rates.
  - `IRONORY-OPS-004`: Grafana operational dashboards for operations and executive management.
  - `IRONORY-QA-001`: Locust distributed load test validating 100 concurrent factory camera streams.
  - `IRONORY-SEC-003`: Third-party penetration testing and OWASP ASVS Level 2 remediation.
- **Acceptance Gate:** System maintains $< 100\text{ ms}$ p95 response time under 1,000 RPM load with zero errors.
