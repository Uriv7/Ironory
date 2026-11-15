# Ironory — Master Feature Ticket List & Production Backlog

**Product:** Ironory  
**Category:** B2B Industrial Quality Inspection SaaS  
**Version:** 1.0.0-PROD-AUDITED  
**Target:** Academic MVP (INT422) + Enterprise Production SaaS Product  
**Audit Reconciliation Date:** 2026-11-16  

---

## PRIORITY DEFINITIONS
- **P0 — Critical:** Required for the first functional MVP and basic production viability.
- **P1 — High:** Required for enterprise readiness, security compliance, and packaging.
- **P2 — Medium:** Advanced functionality, multi-model fine-tuning, and optimization.
- **P3 — Future:** Commercial expansion, edge hardware streaming, and enterprise SSO.

## STATUS DEFINITIONS
- `NOT_STARTED`
- `IN_PROGRESS`
- `PARTIAL`
- `BLOCKED`
- `COMPLETED`
- `DEFERRED`

---

## EPIC 01 — PROJECT FOUNDATION AND ARCHITECTURE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-001 | Repository and Architecture Audit | P0 | COMPLETED | None | docs/, IMPLEMENTATION_LOG.md, ARCHITECTURE_DECISIONS.md |
| VISION-002 | Project Architecture | P0 | COMPLETED | VISION-001 | docs/architecture/, backend/, frontend/, ml/ |
| VISION-003 | Development Environment | P0 | COMPLETED | VISION-001, VISION-002 | .env.example, .gitignore, infrastructure/scripts/dev.sh, test.sh |
| VISION-004 | Database Foundation | P0 | COMPLETED | VISION-003 | backend/app/models/, backend/app/db/, backend/alembic/ |
| VISION-005 | API Foundation | P0 | COMPLETED | VISION-003, VISION-004 | backend/app/api/v1/, backend/app/main.py, backend/app/core/ |

---

## EPIC 02 — AUTHENTICATION AND AUTHORIZATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-006 | User Registration | P0 | COMPLETED | VISION-004, VISION-005 | backend/app/api/v1/endpoints/auth.py, frontend/app/(auth)/register/page.tsx |
| VISION-007 | Login and Logout | P0 | COMPLETED | VISION-006 | backend/app/api/v1/endpoints/auth.py, frontend/app/(auth)/login/page.tsx |
| VISION-008 | Email Verification | P1 | COMPLETED | VISION-006 | backend/app/services/email.py, backend/app/api/v1/endpoints/auth.py |
| VISION-009 | Password Recovery | P1 | COMPLETED | VISION-006, VISION-007 | backend/app/api/v1/endpoints/auth.py, frontend/app/(auth)/forgot-password/page.tsx |
| VISION-010 | Role-Based Access Control | P0 | COMPLETED | VISION-007 | backend/app/security/rbac.py, backend/app/security/tenant.py |
| VISION-011 | Account Security | P1 | COMPLETED | VISION-007, VISION-010 | backend/app/security/rate_limiter.py |

---

## EPIC 03 — MULTI-TENANT ORGANIZATION MANAGEMENT
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-012 | Organization Registration | P0 | COMPLETED | VISION-006, VISION-010 | backend/app/api/v1/endpoints/auth.py, backend/app/services/auth_service.py |
| VISION-013 | Organization Profile | P1 | COMPLETED | VISION-012 | backend/app/api/v1/endpoints/organizations.py, frontend/app/(dashboard)/settings/page.tsx |
| VISION-014 | Organization Membership | P0 | COMPLETED | VISION-012, VISION-010 | backend/app/api/v1/endpoints/organizations.py, frontend/app/(dashboard)/team/page.tsx |
| VISION-015 | Tenant Isolation | P0 | COMPLETED | VISION-012, VISION-004 | backend/app/security/tenant.py, backend/tests/test_tenant_isolation.py |
| VISION-016 | Organization Settings | P1 | COMPLETED | VISION-013 | backend/app/api/v1/endpoints/organizations.py, frontend/app/(dashboard)/settings/page.tsx |

---

## EPIC 04 — PLATFORM ADMINISTRATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-017 | Super Admin Dashboard | P1 | NOT_STARTED | VISION-010, VISION-012 | frontend/app/(admin)/dashboard/ |
| VISION-018 | Organization Administration | P1 | NOT_STARTED | VISION-017 | backend/app/api/v1/admin/organizations.py |
| VISION-019 | Platform User Management | P1 | NOT_STARTED | VISION-017 | backend/app/api/v1/admin/users.py |
| VISION-020 | Platform Audit Logs | P1 | NOT_STARTED | VISION-017 | backend/app/services/audit.py |

---

## EPIC 05 — PRODUCT AND INSPECTION CONFIGURATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-021 | Product Creation | P0 | COMPLETED | VISION-012, VISION-015 | backend/app/api/v1/endpoints/products.py, frontend/app/(dashboard)/products/new/page.tsx |
| VISION-022 | Product Management | P0 | COMPLETED | VISION-021 | backend/app/api/v1/endpoints/products.py, frontend/app/(dashboard)/products/page.tsx |
| VISION-023 | Product Categories | P1 | COMPLETED | VISION-021 | backend/app/api/v1/endpoints/products.py, backend/app/models/product.py |
| VISION-024 | Inspection Configuration | P0 | COMPLETED | VISION-021 | backend/app/models/product.py, frontend/app/(dashboard)/products/new/page.tsx |
| VISION-025 | Product Inspection History | P1 | COMPLETED | VISION-022, VISION-037 | frontend/app/(dashboard)/inspections/page.tsx |

---

## EPIC 06 — IMAGE MANAGEMENT AND PREPROCESSING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-026 | Image Upload | P0 | COMPLETED | VISION-005, VISION-015 | backend/app/services/image_processor.py, backend/app/api/v1/endpoints/inspections.py |
| VISION-027 | Batch Image Upload | P1 | COMPLETED | VISION-026 | backend/app/api/v1/endpoints/inspections.py, frontend/app/(dashboard)/inspections/page.tsx |
| VISION-028 | Image Metadata Extraction | P1 | COMPLETED | VISION-026 | backend/app/services/image_processor.py, backend/app/models/inspection.py |
| VISION-029 | Image Preprocessing | P0 | COMPLETED | VISION-026 | backend/app/services/image_processor.py |
| VISION-030 | Image Augmentation | P1 | COMPLETED | VISION-029 | ml/preprocessing/augmentation.py |

---

## EPIC 07 — CORE AI INSPECTION ENGINE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-031 | Inspection Record Creation | P0 | COMPLETED | VISION-021, VISION-026 | backend/app/api/v1/endpoints/inspections.py, backend/app/repositories/inspection_repository.py |
| VISION-032 | Inspection Job Processing | P0 | COMPLETED | VISION-031 | backend/app/models/inspection.py (Lifecycle State Machine: QUEUED, PROCESSING, COMPLETED, REQUIRES_REVIEW, FAILED) |
| VISION-033 | AI Inference Service | P0 | COMPLETED | VISION-029, VISION-041 | ml/inference/service.py, backend/app/services/inspection_execution_service.py |
| VISION-034 | Defect Classification | P0 | COMPLETED | VISION-033 | ml/inference/service.py, ml/models/cnn/baseline_cnn.py |
| VISION-035 | Anomaly Detection | P1 | COMPLETED | VISION-033, VISION-045 | ml/models/autoencoder/conv_autoencoder.py, ml/training/train_autoencoder.py |
| VISION-036 | Defect Localization | P1 | COMPLETED | VISION-033, VISION-048 | ml/inference/service.py, ml/visualization/gradcam.py |
| VISION-037 | Inspection Result Persistence | P0 | COMPLETED | VISION-033, VISION-031 | backend/app/repositories/inspection_repository.py, backend/app/models/inspection.py |
| VISION-038 | Inspection Failure Management | P0 | COMPLETED | VISION-032 | backend/app/repositories/inspection_repository.py, backend/app/api/v1/endpoints/inspections.py |

---

## EPIC 08 — CNN AND TRANSFER LEARNING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-039 | Dataset Loading Pipeline | P0 | COMPLETED | None | ml/datasets/neu_loader.py, ml/datasets/__init__.py |
| VISION-040 | Baseline CNN | P0 | COMPLETED | VISION-039 | ml/models/cnn/baseline_cnn.py, ml/training/train_cnn.py |
| VISION-041 | Transfer Learning | P0 | COMPLETED | VISION-039 | ml/models/transfer_learning/mobilenet.py, efficientnet.py |
| VISION-042 | Model Evaluation | P0 | COMPLETED | VISION-040, VISION-041 | ml/evaluation/metrics.py |
| VISION-043 | TensorBoard Integration | P1 | COMPLETED | VISION-040 | ml/training/train_cnn.py |
| VISION-044 | Activation Map Visualization | P1 | COMPLETED | VISION-040 | ml/visualization/gradcam.py |

---

## EPIC 09 — AUTOENCODER AND ANOMALY DETECTION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-045 | Autoencoder Architecture | P1 | COMPLETED | VISION-039 | ml/models/autoencoder/conv_autoencoder.py |
| VISION-046 | Anomaly Threshold Calibration | P1 | COMPLETED | VISION-045 | ml/training/train_autoencoder.py, ml/artifacts/anomaly_threshold.json |
| VISION-047 | Image Reconstruction Interface | P1 | COMPLETED | VISION-045, VISION-046 | streamlit_app/app.py |

---

## EPIC 10 — IMAGE SEGMENTATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-048 | U-Net Implementation | P2 | COMPLETED | VISION-039 | ml/models/segmentation/unet.py |
| VISION-049 | Segmentation Training | P2 | COMPLETED | VISION-048 | ml/training/train_unet.py |
| VISION-050 | Segmentation Evaluation | P2 | COMPLETED | VISION-049 | ml/models/segmentation/unet.py, ml/tests/test_ml.py |
| VISION-051 | Defect Overlay Interface | P2 | COMPLETED | VISION-048 | frontend/app/(dashboard)/inspections/[id]/page.tsx |

---

## EPIC 11 — GAN AND ADVANCED AI
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-052 | GAN Architecture | P2 | COMPLETED | VISION-039 | ml/models/gan/dcgan.py |
| VISION-053 | Synthetic Defect Generation | P2 | COMPLETED | VISION-052 | ml/models/gan/dcgan.py, streamlit_app/app.py |
| VISION-054 | FGSM Adversarial Robustness | P3 | COMPLETED | VISION-040 | ml/experiments/fgsm_robustness.py |
| VISION-055 | LSTM Defect Forecasting | P3 | COMPLETED | VISION-060 | ml/models/lstm/forecast_lstm.py, ml/training/train_lstm.py |

---

## EPIC 12 — INSPECTION MANAGEMENT AND HUMAN REVIEW
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-056 | Inspection History | P0 | COMPLETED | VISION-031, VISION-037 | backend/app/api/v1/endpoints/inspections.py, frontend/app/(dashboard)/inspections/page.tsx |
| VISION-057 | Human Review | P0 | COMPLETED | VISION-056 | backend/app/api/v1/endpoints/inspections.py, frontend/app/(dashboard)/inspections/[id]/page.tsx |
| VISION-058 | Review Workflow | P1 | COMPLETED | VISION-057 | backend/app/services/review_workflow.py |
| VISION-059 | Inspection Audit Trail | P1 | COMPLETED | VISION-057 | backend/app/models/audit.py, backend/app/services/audit.py |

---

## EPIC 13 — ANALYTICS AND REPORTING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-060 | Organization Dashboard | P0 | COMPLETED | VISION-031, VISION-037 | frontend/app/page.tsx, backend/app/api/v1/endpoints/analytics.py |
| VISION-061 | Defect Analytics | P1 | COMPLETED | VISION-060 | backend/app/api/v1/endpoints/analytics.py |
| VISION-062 | Inspection Performance Analytics | P1 | COMPLETED | VISION-060 | backend/app/api/v1/endpoints/analytics.py |
| VISION-063 | PDF Inspection Reports | P0 | COMPLETED | VISION-037 | backend/app/services/report_generator.py, backend/app/api/v1/endpoints/inspections.py |
| VISION-064 | Batch Reports | P2 | COMPLETED | VISION-063 | backend/app/api/v1/endpoints/inspections.py, frontend/app/(dashboard)/reports/page.tsx |

---

## EPIC 14 — SAAS SUBSCRIPTION AND USAGE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-065 | Subscription Plans | P2 | NOT_STARTED | VISION-012 | backend/app/models/subscription.py |
| VISION-066 | Usage Tracking | P1 | NOT_STARTED | VISION-031, VISION-065 | backend/app/services/usage_tracker.py |
| VISION-067 | Subscription Enforcement | P2 | NOT_STARTED | VISION-066 | backend/app/security/plan_limits.py |
| VISION-068 | Payment Integration | P3 | NOT_STARTED | VISION-065 | backend/app/services/payment.py |

---

## EPIC 15 — NOTIFICATIONS
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-069 | In-App Notifications | P1 | NOT_STARTED | VISION-032, VISION-057 | backend/app/api/v1/notifications.py, frontend/components/notifications/ |
| VISION-070 | Email Notifications | P2 | NOT_STARTED | VISION-069 | backend/app/services/email_notifications.py |
| VISION-071 | Notification Preferences | P2 | NOT_STARTED | VISION-069 | frontend/app/(dashboard)/settings/notifications/ |

---

## EPIC 16 — STREAMLIT ACADEMIC DEMONSTRATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-072 | Streamlit Application | P0 | COMPLETED | VISION-040, VISION-041 | streamlit_app/app.py |
| VISION-073 | CNN Demonstration | P0 | COMPLETED | VISION-040, VISION-072 | streamlit_app/app.py |
| VISION-074 | Transfer Learning Comparison | P1 | COMPLETED | VISION-041, VISION-072 | streamlit_app/app.py |
| VISION-075 | Autoencoder Demonstration | P1 | COMPLETED | VISION-045, VISION-072 | streamlit_app/app.py |
| VISION-076 | GAN Demonstration | P2 | COMPLETED | VISION-052, VISION-072 | streamlit_app/app.py |
| VISION-077 | TensorBoard Demonstration | P1 | COMPLETED | VISION-043, VISION-072 | streamlit_app/app.py |

---

## EPIC 17 — INFRASTRUCTURE, SECURITY AND DEPLOYMENT
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-078 | Docker Environment | P0 | PARTIAL | VISION-003 | docker-compose.yml, backend/Dockerfile, frontend/Dockerfile |
| VISION-079 | Production Configuration | P1 | NOT_STARTED | VISION-078 | infrastructure/env/ |
| VISION-080 | GPU Support | P2 | NOT_STARTED | VISION-078 | infrastructure/docker/Dockerfile.gpu |
| VISION-081 | Logging and Monitoring | P1 | COMPLETED | VISION-005 | backend/app/core/logging.py, backend/app/middleware/correlation.py |
| VISION-082 | Backup and Recovery | P1 | NOT_STARTED | VISION-004 | scripts/backup_db.sh |
| VISION-083 | CI/CD | P2 | COMPLETED | None | .github/workflows/ci.yml |

---

## EPIC 18 — TESTING, DOCUMENTATION AND RELEASE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-084 | Frontend Testing | P0 | COMPLETED | Frontend completion | frontend/ (Type-check 0 errors, Next.js build 14/14 prerendered) |
| VISION-085 | Backend Testing | P0 | COMPLETED | Backend completion | backend/tests/ (26/26 backend tests passing) |
| VISION-086 | AI Model Testing | P0 | COMPLETED | ML completion | ml/tests/ (9/9 ML tests passing) |
| VISION-087 | End-to-End Testing | P0 | COMPLETED | Full integration | backend/tests/test_analytics.py, test_inspections.py |
| VISION-088 | Academic Documentation | P0 | COMPLETED | ML evaluation | docs/INT422_ACADEMIC_REPORT.md |
| VISION-089 | Technical Documentation | P1 | COMPLETED | Architecture | docs/ |
| VISION-090 | MVP Release Validation | P0 | COMPLETED | All P0 tickets | Full system verified |

---

## EPIC 19 — PRODUCTION READINESS BACKLOG (AUDIT IDENTIFIED)
| Ticket ID | Title | Priority | Status | Target Phase | Files / Modules Affected | Description |
|---|---|:---:|:---:|:---:|---|---|
| `IRONORY-OPS-001` | Multi-Stage Docker ML Dependencies | **P0** | NOT_STARTED | Phase 1 | `backend/Dockerfile`, `docker-compose.yml` | Copy `ml/` package and install ML runtime packages (`tensorflow`, `reportlab`, `opencv`) into backend container. |
| `IRONORY-INS-001` | Asynchronous Celery Worker Queue | **P0** | NOT_STARTED | Phase 1 | `backend/app/api/v1/endpoints/inspections.py`, `backend/app/workers/` | Decouple inference from HTTP thread; return `202 Accepted` and process via Redis queue. |
| `IRONORY-UI-001` | Client-Side Auth Header Interceptor | **P0** | NOT_STARTED | Phase 1 | `frontend/lib/api-client.ts` | Auto-attach `Authorization: Bearer <token>` and `X-Organization-ID` from browser storage. |
| `IRONORY-DATA-001` | Alembic Migration for Audit Logs | **P0** | NOT_STARTED | Phase 1 | `backend/alembic/versions/` | Generate migration version to create `audit_logs` table in production PostgreSQL. |
| `IRONORY-SEC-001` | Redis Session & Token Blacklist | **P1** | NOT_STARTED | Phase 2 | `backend/app/security/session.py` | Sliding window session revocation on logout and role change. |
| `IRONORY-AUD-002` | Automated Mutation Audit Middleware | **P1** | NOT_STARTED | Phase 2 | `backend/app/middleware/audit.py` | Automatically record IP, actor ID, resource diffs into `AuditLog`. |
| `IRONORY-INS-002` | Quality Manager Override Sign-Off | **P1** | NOT_STARTED | Phase 2 | `backend/app/services/review_workflow.py` | Require Quality Manager credential signature before finalizing defect override. |
| `IRONORY-ML-001` | Transfer Learning Weights Persistence | **P1** | NOT_STARTED | Phase 3 | `ml/artifacts/`, `ml/training/train_transfer.py` | Save fine-tuned weights for MobileNetV2 and EfficientNet-B0 on NEU dataset. |
| `IRONORY-ML-002` | U-Net Segmentation Weights Persistence | **P1** | NOT_STARTED | Phase 3 | `ml/artifacts/unet.keras` | Train and persist pixel-level segmentation mask weights. |
| `IRONORY-ML-003` | Softmax Temperature Scaling | **P2** | NOT_STARTED | Phase 3 | `ml/inference/service.py` | Calibrate confidence scores to eliminate overconfidence on out-of-distribution inputs. |
| `IRONORY-ML-004` | PSI Population Drift Telemetry | **P2** | NOT_STARTED | Phase 3 | `ml/evaluation/drift.py` | Calculate Population Stability Index on real-time defect distributions. |
| `IRONORY-INS-003` | WebSocket Live Ingest Broadcasting | **P1** | NOT_STARTED | Phase 4 | `backend/app/api/v1/endpoints/ws.py` | Push live inspection status and heatmaps to active client browsers. |
| `IRONORY-INS-004` | Industrial RTSP / GigE Streamer | **P2** | NOT_STARTED | Phase 4 | `backend/app/services/streamer.py` | Connect directly to factory line Basler/FLIR GigE optical cameras. |
| `IRONORY-OPS-002` | Edge Storage Cache with LRU Pruning | **P2** | NOT_STARTED | Phase 4 | `backend/app/services/storage.py` | Local disk cache with automated pruning for shop floor deployments. |
| `IRONORY-BILL-001` | Stripe Tiered SaaS Billing | **P1** | NOT_STARTED | Phase 5 | `backend/app/services/stripe.py` | Manage customer subscriptions, tiers (Starter, Pro, Enterprise), and invoices. |
| `IRONORY-BILL-002` | Usage Metering & Quota Throttling | **P2** | NOT_STARTED | Phase 5 | `backend/app/security/quotas.py` | Enforce monthly inspection volume limits per tenant tier. |
| `IRONORY-SEC-002` | SAML 2.0 / Okta Enterprise SSO | **P2** | NOT_STARTED | Phase 5 | `backend/app/security/sso.py` | Enterprise identity provider integration for user provisioning. |
| `IRONORY-OPS-003` | Prometheus Metrics Exporter (`/metrics`) | **P1** | NOT_STARTED | Phase 6 | `backend/app/main.py` | Export inference latency, queue depth, error rates for Prometheus scraping. |
| `IRONORY-OPS-004` | Grafana Operations Dashboards | **P2** | NOT_STARTED | Phase 6 | `infrastructure/monitoring/grafana/` | Pre-configured dashboard templates for shop floor uptime and SLA monitoring. |
| `IRONORY-QA-001` | Locust Distributed Factory Load Test | **P1** | NOT_STARTED | Phase 6 | `tests/load/locustfile.py` | Benchmark 100 concurrent camera feeds at 10 FPS. |
| `IRONORY-SEC-003` | Third-Party Penetration Hardening | **P1** | NOT_STARTED | Phase 6 | AppSec Hardening | Remediate findings from formal OWASP ASVS Level 2 penetration audit. |

---
*End of Master Feature Ticket List & Production Backlog.*
