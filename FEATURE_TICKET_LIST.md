# Ironory — Master Feature Ticket List

**Product:** Ironory  
**Category:** B2B Industrial Quality Inspection SaaS  
**Version:** 1.0  
**Status:** Phase 1 Foundation Completed & Verified  
**Target:** Academic MVP (INT422) + Commercial SaaS Product  
**Audit Date:** 2026-11-16  

---

## PRIORITY DEFINITIONS
- **P0 — Critical:** Required for the first functional MVP.
- **P1 — High:** Required for a complete initial product.
- **P2 — Medium:** Advanced functionality and optimization.
- **P3 — Future:** Commercial expansion and enterprise capabilities.

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
| VISION-006 | User Registration | P0 | NOT_STARTED | VISION-004, VISION-005 | backend/app/api/v1/auth.py, frontend/app/(auth)/register/ |
| VISION-007 | Login and Logout | P0 | NOT_STARTED | VISION-006 | backend/app/api/v1/auth.py, frontend/app/(auth)/login/ |
| VISION-008 | Email Verification | P1 | NOT_STARTED | VISION-006 | backend/app/services/email.py |
| VISION-009 | Password Recovery | P1 | NOT_STARTED | VISION-006, VISION-007 | backend/app/api/v1/auth.py, frontend/app/(auth)/forgot-password/ |
| VISION-010 | Role-Based Access Control | P0 | NOT_STARTED | VISION-007 | backend/app/security/rbac.py |
| VISION-011 | Account Security | P1 | NOT_STARTED | VISION-007, VISION-010 | backend/app/security/rate_limiter.py |

---

## EPIC 03 — MULTI-TENANT ORGANIZATION MANAGEMENT
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-012 | Organization Registration | P0 | NOT_STARTED | VISION-006, VISION-010 | backend/app/api/v1/organizations.py |
| VISION-013 | Organization Profile | P1 | NOT_STARTED | VISION-012 | frontend/app/(dashboard)/settings/organization/ |
| VISION-014 | Organization Membership | P0 | NOT_STARTED | VISION-012, VISION-010 | backend/app/api/v1/members.py, frontend/app/(dashboard)/team/ |
| VISION-015 | Tenant Isolation | P0 | NOT_STARTED | VISION-012, VISION-004 | backend/app/security/tenant.py, backend/app/repositories/ |
| VISION-016 | Organization Settings | P1 | NOT_STARTED | VISION-013 | backend/app/api/v1/organizations.py |

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
| VISION-021 | Product Creation | P0 | NOT_STARTED | VISION-012, VISION-015 | backend/app/api/v1/products.py, frontend/app/(dashboard)/products/new/ |
| VISION-022 | Product Management | P0 | NOT_STARTED | VISION-021 | frontend/app/(dashboard)/products/ |
| VISION-023 | Product Categories | P1 | NOT_STARTED | VISION-021 | backend/app/api/v1/categories.py |
| VISION-024 | Inspection Configuration | P0 | NOT_STARTED | VISION-021 | backend/app/api/v1/inspection_configs.py |
| VISION-025 | Product Inspection History | P1 | NOT_STARTED | VISION-022, VISION-037 | frontend/app/(dashboard)/products/[id]/history/ |

---

## EPIC 06 — IMAGE MANAGEMENT AND PREPROCESSING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-026 | Image Upload | P0 | NOT_STARTED | VISION-005, VISION-015 | backend/app/services/storage.py, backend/app/api/v1/uploads.py |
| VISION-027 | Batch Image Upload | P1 | NOT_STARTED | VISION-026 | frontend/app/(dashboard)/inspections/batch/ |
| VISION-028 | Image Metadata Extraction | P1 | NOT_STARTED | VISION-026 | backend/app/services/image_processor.py |
| VISION-029 | Image Preprocessing | P0 | NOT_STARTED | VISION-026 | ml/preprocessing/pipeline.py |
| VISION-030 | Image Augmentation | P1 | NOT_STARTED | VISION-029 | ml/preprocessing/augmentation.py |

---

## EPIC 07 — CORE AI INSPECTION ENGINE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-031 | Inspection Record Creation | P0 | NOT_STARTED | VISION-021, VISION-026 | backend/app/api/v1/inspections.py |
| VISION-032 | Inspection Job Processing | P0 | NOT_STARTED | VISION-031 | backend/app/workers/inspection_worker.py |
| VISION-033 | AI Inference Service | P0 | NOT_STARTED | VISION-029, VISION-041 | ml/inference/service.py, backend/app/services/inference.py |
| VISION-034 | Defect Classification | P0 | NOT_STARTED | VISION-033 | ml/inference/classifier.py |
| VISION-035 | Anomaly Detection | P1 | NOT_STARTED | VISION-033, VISION-045 | ml/inference/anomaly.py |
| VISION-036 | Defect Localization | P1 | NOT_STARTED | VISION-033, VISION-048 | ml/inference/segmentation.py |
| VISION-037 | Inspection Result Persistence | P0 | NOT_STARTED | VISION-033, VISION-031 | backend/app/repositories/inspection_repo.py |
| VISION-038 | Inspection Failure Management | P0 | NOT_STARTED | VISION-032 | backend/app/services/error_handler.py |

---

## EPIC 08 — CNN AND TRANSFER LEARNING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-039 | Dataset Loading Pipeline | P0 | NOT_STARTED | None | ml/datasets/neu_loader.py, ml/datasets/mvtec_loader.py |
| VISION-040 | Baseline CNN | P0 | NOT_STARTED | VISION-039 | ml/models/cnn/baseline_cnn.py, ml/training/train_cnn.py |
| VISION-041 | Transfer Learning | P0 | NOT_STARTED | VISION-039 | ml/models/transfer_learning/mobilenet.py, efficientnet.py |
| VISION-042 | Model Evaluation | P0 | NOT_STARTED | VISION-040, VISION-041 | ml/evaluation/metrics.py |
| VISION-043 | TensorBoard Integration | P1 | NOT_STARTED | VISION-040 | ml/training/callbacks.py |
| VISION-044 | Activation Map Visualization | P1 | NOT_STARTED | VISION-040 | ml/visualization/gradcam.py |

---

## EPIC 09 — AUTOENCODER AND ANOMALY DETECTION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-045 | Autoencoder Architecture | P1 | NOT_STARTED | VISION-039 | ml/models/autoencoder/conv_autoencoder.py |
| VISION-046 | Anomaly Threshold Calibration | P1 | NOT_STARTED | VISION-045 | ml/evaluation/calibrate_threshold.py |
| VISION-047 | Image Reconstruction Interface | P1 | NOT_STARTED | VISION-045, VISION-046 | frontend/app/(dashboard)/inspections/anomaly/ |

---

## EPIC 10 — IMAGE SEGMENTATION
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-048 | U-Net Implementation | P2 | NOT_STARTED | VISION-039 | ml/models/segmentation/unet.py |
| VISION-049 | Segmentation Training | P2 | NOT_STARTED | VISION-048 | ml/training/train_unet.py |
| VISION-050 | Segmentation Evaluation | P2 | NOT_STARTED | VISION-049 | ml/evaluation/segmentation_metrics.py |
| VISION-051 | Defect Overlay Interface | P2 | NOT_STARTED | VISION-048 | frontend/components/inspections/DefectOverlay.tsx |

---

## EPIC 11 — GAN AND ADVANCED AI
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-052 | GAN Architecture | P2 | NOT_STARTED | VISION-039 | ml/models/gan/dcgan.py |
| VISION-053 | Synthetic Defect Generation | P2 | NOT_STARTED | VISION-052 | ml/experiments/generate_defects.py |
| VISION-054 | FGSM Adversarial Robustness | P3 | NOT_STARTED | VISION-040 | ml/experiments/fgsm_robustness.py |
| VISION-055 | LSTM Defect Forecasting | P3 | NOT_STARTED | VISION-060 | ml/models/lstm/forecast_lstm.py |

---

## EPIC 12 — INSPECTION MANAGEMENT AND HUMAN REVIEW
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-056 | Inspection History | P0 | NOT_STARTED | VISION-031, VISION-037 | frontend/app/(dashboard)/inspections/history/ |
| VISION-057 | Human Review | P0 | NOT_STARTED | VISION-056 | backend/app/api/v1/reviews.py, frontend/components/inspections/ReviewDialog.tsx |
| VISION-058 | Review Workflow | P1 | NOT_STARTED | VISION-057 | backend/app/services/review_workflow.py |
| VISION-059 | Inspection Audit Trail | P1 | NOT_STARTED | VISION-057 | backend/app/models/audit.py |

---

## EPIC 13 — ANALYTICS AND REPORTING
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-060 | Organization Dashboard | P0 | NOT_STARTED | VISION-031, VISION-037 | frontend/app/(dashboard)/page.tsx, backend/app/api/v1/analytics.py |
| VISION-061 | Defect Analytics | P1 | NOT_STARTED | VISION-060 | frontend/app/(dashboard)/analytics/ |
| VISION-062 | Inspection Performance Analytics | P1 | NOT_STARTED | VISION-060 | backend/app/services/analytics_service.py |
| VISION-063 | PDF Inspection Reports | P0 | NOT_STARTED | VISION-037 | backend/app/services/report_generator.py |
| VISION-064 | Batch Reports | P2 | NOT_STARTED | VISION-063 | backend/app/api/v1/reports.py |

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
| VISION-072 | Streamlit Application | P0 | NOT_STARTED | VISION-040, VISION-041 | streamlit_app/app.py |
| VISION-073 | CNN Demonstration | P0 | NOT_STARTED | VISION-040, VISION-072 | streamlit_app/pages/04_cnn_results.py |
| VISION-074 | Transfer Learning Comparison | P1 | NOT_STARTED | VISION-041, VISION-072 | streamlit_app/pages/05_transfer_learning.py |
| VISION-075 | Autoencoder Demonstration | P1 | NOT_STARTED | VISION-045, VISION-072 | streamlit_app/pages/06_autoencoder.py |
| VISION-076 | GAN Demonstration | P2 | NOT_STARTED | VISION-052, VISION-072 | streamlit_app/pages/08_gan_samples.py |
| VISION-077 | TensorBoard Demonstration | P1 | NOT_STARTED | VISION-043, VISION-072 | streamlit_app/pages/09_tensorboard.py |

---

## EPIC 17 — INFRASTRUCTURE, SECURITY AND DEPLOYMENT
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-078 | Docker Environment | P0 | PARTIAL | VISION-003 | docker-compose.yml, backend/Dockerfile, frontend/Dockerfile |
| VISION-079 | Production Configuration | P1 | NOT_STARTED | VISION-078 | infrastructure/env/ |
| VISION-080 | GPU Support | P2 | NOT_STARTED | VISION-078 | infrastructure/docker/Dockerfile.gpu |
| VISION-081 | Logging and Monitoring | P1 | NOT_STARTED | VISION-005 | backend/app/core/logging.py |
| VISION-082 | Backup and Recovery | P1 | NOT_STARTED | VISION-004 | scripts/backup_db.sh |
| VISION-083 | CI/CD | P2 | NOT_STARTED | None | .github/workflows/ci.yml |

---

## EPIC 18 — TESTING, DOCUMENTATION AND RELEASE
| Ticket ID | Title | Priority | Status | Dependencies | Files Changed / Modules |
|---|---|---|---|---|---|
| VISION-084 | Frontend Testing | P0 | NOT_STARTED | Frontend completion | frontend/__tests__/ |
| VISION-085 | Backend Testing | P0 | NOT_STARTED | Backend completion | backend/tests/ |
| VISION-086 | AI Model Testing | P0 | NOT_STARTED | ML completion | ml/tests/ |
| VISION-087 | End-to-End Testing | P0 | NOT_STARTED | Full integration | tests/e2e/ |
| VISION-088 | Academic Documentation | P0 | NOT_STARTED | ML evaluation | docs/INT422_ACADEMIC_REPORT.md |
| VISION-089 | Technical Documentation | P1 | NOT_STARTED | Architecture | docs/ |
| VISION-090 | MVP Release Validation | P0 | NOT_STARTED | All P0 tickets | release/ |

---
*End of Master Feature Ticket List.*
