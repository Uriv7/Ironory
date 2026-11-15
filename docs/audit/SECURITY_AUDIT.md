# Ironory — Application Security & OWASP Audit

**Document ID:** IRONORY-AUD-005  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Security Classification:** Restricted / Enterprise Confidential  
**Assessment Standard:** OWASP Top 10 (2021) & Industrial SaaS Security Standards  
**Audit Date:** 2026-11-16  

---

## 1. Executive Security Assessment

Ironory has implemented foundational application security controls, including bcrypt password hashing, JWT bearer authentication, multi-tenant database partitioning, and rate limiting. However, deploying to industrial enterprise customers requires mitigating several critical vulnerabilities, particularly around file upload validation, model deserialization safety, and token rotation.

---

## 2. OWASP Top 10 (2021) Detailed Findings Matrix

| OWASP Vulnerability Category | Severity | Current Ironory Status | Evidence / File Path | Remediated / Required Action |
|---|:---:|:---:|---|---|
| **A01: Broken Access Control** | **HIGH** | **Partially Hardened** | `backend/app/security/tenant.py:46-77` | Tenant isolation is enforced via `get_current_tenant_membership`. Need strict check that `product_id` matches `organization_id` in all mutations. |
| **A02: Cryptographic Failures** | **MEDIUM** | **Hardened** | `backend/app/core/security.py:20-56` | Bcrypt utilized for password hashing (12 rounds). JWT tokens signed with HMAC-SHA256. Recommend upgrading to asymmetric RS256 for microservices. |
| **A03: Injection** | **LOW** | **Protected** | `backend/app/repositories/*.py` | SQLAlchemy ORM parameterized queries protect against SQL injection. No raw unescaped SQL executed. |
| **A04: Insecure Design** | **MEDIUM** | **Hardened** | `backend/app/security/rate_limiter.py` | Sliding window rate limiting implemented for auth and ingest endpoints. Human review overrides require mandatory reasoning text. |
| **A05: Security Misconfiguration** | **HIGH** | **Vulnerable** | `docker-compose.yml:10, 39` | Default passwords (`ironory_secret_pass`) in compose file; CORS origins allow wildcard localhost. Production deployment must mandate `.env` secret injection. |
| **A06: Vulnerable Dependencies** | **LOW** | **Verified** | `backend/requirements.txt`, `frontend/package.json` | Modern versions: FastAPI 0.110+, Next.js 14.1+, SQLAlchemy 2.0+, Pydantic 2.6+. No critical CVEs reported in automated scanning. |
| **A07: Identification & Auth** | **MEDIUM** | **Hardened** | `backend/app/services/auth_service.py` | JWT access tokens (30 min) + Refresh tokens. Password reset and email verification implemented. Need brute-force account lockout after 5 attempts. |
| **A08: Software & Data Integrity** | **HIGH** | **Vulnerable** | `backend/app/services/image_processor.py:20-45` | Image uploads check file extension and Pillow decode, but lack strict magic-byte validation and anti-decompression bomb protection (`Image.MAX_IMAGE_PIXELS`). |
| **A09: Logging & Monitoring** | **MEDIUM** | **Partially Hardened** | `backend/app/middleware/correlation.py`, `backend/app/models/audit.py` | Correlation IDs attached to requests. AuditLog table defined, but needs automated interception for all administrative and review actions. |
| **A10: Server-Side Request Forgery** | **LOW** | **Protected** | No outbound URL fetching endpoints currently exposed in backend API. | Maintain strict URL allowlisting if external webhook integrations are introduced. |

---

## 3. Deep-Dive Security Findings & Evidence

### 3.1 SEC-01: File Upload Validation & Image Bomb Vulnerability
- **Severity:** HIGH
- **File:** `backend/app/services/image_processor.py` (Lines 22-38)
- **Problem:** When an operator uploads a surface inspection file, the service relies on `ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}` and opens the stream via `Image.open(io.BytesIO(contents))`. It does not explicitly set `Image.MAX_IMAGE_PIXELS = 50_000_000`, creating vulnerability to "decompression bombs" (small file expanding to gigabytes in memory, crashing the worker process).
- **Remediation:**
  ```python
  from PIL import Image
  Image.MAX_IMAGE_PIXELS = 50_000_000  # Enforce 50MP maximum
  # Verify magic numbers: PNG: \x89PNG\r\n\x1a\n, JPEG: \xff\xd8\xff
  ```

### 3.2 SEC-02: Model Artifact Deserialization Integrity
- **Severity:** MEDIUM
- **File:** `ml/inference/service.py` (Line 72)
- **Problem:** `tf.keras.models.load_model(str(model_file))` is invoked on local files. If model files are stored in shared object storage (S3) or uploaded by administrators, untrusted `.keras` / `.h5` files with custom lambda layers could execute arbitrary bytecode.
- **Remediation:** Compute SHA-256 cryptographic hashes for all model checkpoints upon release and verify the hash prior to loading into memory. Set `safe_mode=True` in `tf.keras.models.load_model`.

### 3.3 SEC-03: Cross-Tenant File Path Traversal
- **Severity:** HIGH
- **File:** `backend/app/services/storage.py` (Lines 52-68)
- **Problem:** Local storage writes tenant files using `f"{self.root_dir}/{tenant_id}/{filename}"`. If `filename` contains uncleaned `../` sequences, files could theoretically escape the tenant storage directory.
- **Remediation:** Enforce `secure_filename()` and generate synthetic UUID filenames on disk (e.g., `f"{uuid.uuid4().hex}.png"`), storing the original human filename only as metadata in the PostgreSQL database.

---

## 4. Compliance & Audit Trail Standard

Ironory provides an immutable `AuditLog` model (`backend/app/models/audit.py`) capturing:
- `organization_id`: Tenant context.
- `actor_id`: User initiating action.
- `action`: Specific operation (e.g., `INSPECTION_OVERRIDE`, `THRESHOLD_UPDATE`, `ROLE_PROMOTION`).
- `resource_type`: Target entity (`Inspection`, `Product`, `Membership`).
- `resource_id`: Primary key of affected record.
- `details`: JSON payload containing diffs and reason text.
- `ip_address`: Remote client IP.

To satisfy ISO 9001:2015 Clause 8.5.2 (Identification and traceability), all inspection overrides are cryptographically tied to the quality manager's unique ID and preserved indefinitely.
