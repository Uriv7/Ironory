# Ironory — Master Role & Permission Matrix

**Document ID:** IRONORY-AUD-002  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Security Level:** Enterprise Grade  
**Audit Date:** 2026-11-16  

---

## 1. Architectural Role Hierarchy

Ironory operates a strict dual-tier authorization model:
1. **Platform-Level Roles:** Global administrators managing infrastructure, billing, tenant lifecycle, and platform telemetry.
2. **Organization-Level Roles (Tenant RBAC):** Scoped to a specific manufacturing tenant account (`organization_id`), enforced cryptographically via JWT claims and HTTP headers.

```
                  ┌───────────────────────────────┐
                  │     Platform Super Admin      │ (is_super_admin = True)
                  └──────────────┬────────────────┘
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                                                       ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     Platform Support Admin    │               │       Platform Analyst        │
└───────────────────────────────┘               └───────────────────────────────┘

================================= TENANT BOUNDARY =================================

┌───────────────────────────────────────────────────────────────────────────────┐
│                           Organization Roles (RBAC)                          │
├───────────────────────────────────────────────────────────────────────────────┤
│  Level 5: OWNER               (Full control, legal, billing, membership)     │
│  Level 4: ADMIN               (Operational admin, team invites, config)       │
│  Level 3: QUALITY_MANAGER     (Model overrides, threshold setting, audit sign)│
│  Level 2: INSPECTOR           (Live camera ingest, upload, run inference)     │
│  Level 1: READ_ONLY           (Dashboard observer, PDF report viewer)         │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Granular Role & Permission Matrix

### Legend
- `ALLOW`: Permitted action.
- `DENY`: Strictly forbidden (HTTP 403 Forbidden).
- `COND`: Conditional (requires ownership or specific approval workflow).
- `SYS`: Platform-only administrative privilege.

| Functional Domain | Permission Action | Platform Super Admin | Org Owner | Org Admin | Quality Manager | Inspector | Read-Only | Enforcement Point |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Organization Lifecycle** | `org.create` | ALLOW | ALLOW | DENY | DENY | DENY | DENY | `POST /api/v1/auth/register` |
| | `org.read` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/organizations/me` |
| | `org.update` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `PATCH /api/v1/organizations/me` |
| | `org.delete` | ALLOW | ALLOW | DENY | DENY | DENY | DENY | `DELETE /api/v1/organizations/{id}` |
| | `org.settings.manage` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `PATCH /api/v1/organizations/settings` |
| **Team & Membership** | `members.read` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/organizations/members` |
| | `members.invite` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `POST /api/v1/organizations/invitations` |
| | `members.role_update` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `PATCH /api/v1/organizations/members/{id}` |
| | `members.remove` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `DELETE /api/v1/organizations/members/{id}` |
| **Products & Parts** | `product.create` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `POST /api/v1/products` |
| | `product.read` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/products` |
| | `product.update` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `PATCH /api/v1/products/{id}` |
| | `product.delete` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `DELETE /api/v1/products/{id}` |
| | `product.config_threshold` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `PUT /api/v1/products/{id}/config` |
| **Inspection & Ingest** | `inspection.upload` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | DENY | `POST /api/v1/inspections` |
| | `inspection.batch_upload`| ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | DENY | `POST /api/v1/inspections/batch` |
| | `inspection.read` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/inspections` |
| | `inspection.delete` | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY | `DELETE /api/v1/inspections/{id}` |
| | `inspection.export_csv` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/inspections/export/csv` |
| | `inspection.download_pdf`| ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/inspections/{id}/report` |
| **Human Review & QA** | `review.view_queue` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/inspections?status=REQUIRES_REVIEW` |
| | `review.confirm` | ALLOW | ALLOW | ALLOW | ALLOW | COND | DENY | `POST /api/v1/inspections/{id}/review` |
| | `review.override` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `POST /api/v1/inspections/{id}/review` |
| | `review.add_defect_note` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | DENY | `POST /api/v1/inspections/{id}/review` |
| **Analytics & Telemetry** | `analytics.overview` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/analytics/overview` |
| | `analytics.defect_dist` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/analytics/defect-distribution` |
| | `analytics.export` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `GET /api/v1/analytics/export` |
| **AI Models & Calibration** | `models.view_registry` | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | `GET /api/v1/models` |
| | `models.select_active` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `PATCH /api/v1/products/{id}/model` |
| | `models.trigger_training`| ALLOW | ALLOW | DENY | DENY | DENY | DENY | `POST /api/v1/models/train` |
| **Audit Logs & Compliance**| `audit.read_tenant` | ALLOW | ALLOW | ALLOW | ALLOW | DENY | DENY | `GET /api/v1/audit/logs` |
| | `audit.read_platform` | ALLOW | DENY | DENY | DENY | DENY | DENY | `GET /api/v1/admin/audit-logs` |

---

## 3. Enforcement Implementation in Code

### 3.1 Role Hierarchy Enforcer (`backend/app/security/rbac.py`)
```python
ROLE_HIERARCHY = {
    OrganizationRole.OWNER: 5,
    OrganizationRole.ADMIN: 4,
    OrganizationRole.QUALITY_MANAGER: 3,
    OrganizationRole.INSPECTOR: 2,
    OrganizationRole.READ_ONLY: 1,
}
```
Endpoints require roles using:
`require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.QUALITY_MANAGER])`

### 3.2 Tenant Context Dependency (`backend/app/security/tenant.py`)
- Reads Bearer token from `Authorization` header.
- Resolves `User` record; verifies `user.is_active is True`.
- Checks `X-Organization-ID` header.
- Asserts active membership in `OrganizationMembership` table matching both `user_id` and `organization_id`.
- Rejects cross-tenant attempts with HTTP 403 `CROSS_TENANT_ACCESS_DENIED`.

---

## 4. Proposed Production Hardening & Recommendations

1. **Explicit Permission Enums:** Transition from coarse role strings to granular action permissions (e.g., `Permission.INSPECTION_OVERRIDE`).
2. **Fine-Grained Audit Logging:** Automatically record every privileged action into `AuditLog` via FastAPI middleware.
3. **Session Revocation List:** Maintain a Redis blacklist of revoked refresh tokens and invalidated sessions.
4. **Conditional Override Rules:** Allow inspectors to submit proposed overrides, but require a Quality Manager signature before final status transition from `REQUIRES_REVIEW` to `COMPLETED`.
