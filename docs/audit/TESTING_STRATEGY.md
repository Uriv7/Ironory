# Ironory — Comprehensive Quality Assurance & Testing Strategy

**Document ID:** IRONORY-AUD-007  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Lead QA Architect:** Automation & Verification Lead  
**Audit Date:** 2026-11-16  

---

## 1. Test Pyramid & Methodology

Ironory adheres to a multi-tiered verification methodology designed to guarantee zero data leakage between tenants, deterministic AI outputs, and high availability on factory shop floors.

```
                  ┌───────────────────────┐
                  │   E2E Browser Tests   │  (Playwright - Backlog)
                  ├───────────────────────┤
                  │   API Integration     │  (35 Tests Passing, 14.48s)
                  ├───────────────────────┤
                  │   ML Unit & Weights   │  (9 ML Tests Passing)
                  ├───────────────────────┤
                  │  Static Typing & Lint │  (0 TypeScript Errors, 14 Routes)
                  └───────────────────────┘
```

---

## 2. Current Test Inventory & Execution Evidence

### 2.1 Backend & ML Test Suite Summary
- **Execution Command:** `.venv/bin/pytest --cov=backend.app --cov=ml backend/tests/ ml/tests/ -q`
- **Pass Rate:** **35 / 35 Passed (100%)**
- **Execution Duration:** 14.48 seconds
- **Total Code Coverage:** **75%** (2,513 statements, 629 missed)

### 2.2 Coverage Breakdown by Critical Module
| Module | File Path | Statements | Missed | Coverage | Key Verified Behaviors |
|---|---|:---:|:---:|:---:|---|
| **Tenant Isolation** | `backend/tests/test_tenant_isolation.py` | 38 | 7 | **82%** | Cross-tenant access blocked (HTTP 403), strict tenant data separation |
| **Authentication** | `backend/tests/test_auth.py` | 44 | 9 | **80%** | Registration, login, duplicate email rejection, JWT generation |
| **Inspection API** | `backend/tests/test_inspections.py` | 161 | 40 | **75%** | Single upload, batch upload (20 frames), CSV export, PDF report generation |
| **Product Catalog**| `backend/tests/test_products.py` | 50 | 3 | **94%** | Part creation, SKU uniqueness, custom threshold assignment |
| **Analytics** | `backend/tests/test_analytics.py` | 30 | 0 | **100%** | Defect distribution, yield rates, date-filtered metrics |
| **ML Inference** | `ml/tests/test_ml.py` | 79 | 0 | **100%** | Baseline CNN forward pass, autoencoder reconstruction, U-Net shapes |
| **Storage Engine** | `backend/tests/test_storage.py` | 76 | 11 | **86%** | File write, read, tenant directory partitioning, delete |

### 2.3 Frontend Static Verification
- **TypeScript Type-Check:** `npm --prefix frontend run type-check` $\rightarrow$ `tsc --noEmit` exited with code 0 (0 errors).
- **Next.js Production Build:** `npm --prefix frontend run build` $\rightarrow$ 14 / 14 static and dynamic routes compiled and prerendered cleanly.

---

## 3. High-Priority Testing Gaps & Missing Test Scenarios

1. **End-to-End (E2E) Browser Verification:**
   - *Current Status:* Absent. Relies on manual browser exploration and API testing.
   - *Required Action:* Implement Playwright suite covering full user journey: Onboarding $\rightarrow$ Product Creation $\rightarrow$ Ingest Scan $\rightarrow$ Review Verdict $\rightarrow$ Export CSV.
2. **Factory Floor Concurrency & Load Testing:**
   - *Current Status:* Absent.
   - *Required Action:* Build Locust load test simulating 50 concurrent camera streams uploading 1080p surface scan images at 5 frames per second.
3. **Corrupted & Malicious Image Upload Tests:**
   - *Current Status:* Handled via Pillow exception catch, but lacks targeted tests for zero-byte files, SVG XML bombs, and truncated JPEG headers.
4. **Token Expiration & Concurrent Session Revocation:**
   - *Required Action:* Add automated tests verifying that expired JWT tokens are rejected with HTTP 401 and that deactivated users cannot invoke cached bearer tokens.

---

## 4. Production Release Quality Gates

Before any pull request is merged into `main` or deployed to production:
1. **Gate 1 (Unit & Integration):** 100% test pass rate across `backend/tests/` and `ml/tests/`.
2. **Gate 2 (Coverage Threshold):** Minimum 75% code coverage on core backend and 80% on security middleware.
3. **Gate 3 (Frontend Health):** Zero TypeScript errors and clean production build with all routes prerendered.
4. **Gate 4 (Tenant Isolation Assertions):** Automated negative tests asserting HTTP 403 on all unauthorized cross-tenant operations.
5. **Gate 5 (Container Security Scan):** Trivy / Docker vulnerability scanner with zero High or Critical CVEs.
