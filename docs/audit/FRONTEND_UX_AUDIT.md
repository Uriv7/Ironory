# Ironory — Frontend & UI/UX Technical Audit

**Document ID:** IRONORY-AUD-004  
**Product:** Ironory (B2B Industrial AI Quality Inspection SaaS)  
**Framework:** Next.js 14.1 (App Router) + React 18 + Tailwind CSS 3.4  
**Audit Date:** 2026-11-16  

---

## 1. Frontend Architecture & Component Topology

The Ironory frontend is organized around Next.js App Router route groups:
- `(auth)`: Public unauthenticated flows (`/login`, `/register`, `/forgot-password`).
- `(dashboard)`: Authenticated enterprise workspaces (`/products`, `/inspections`, `/analytics`, `/reports`, `/team`, `/models`, `/settings`).
- `components/ui`: Atomic design primitives (`Button`, `Card`, `Badge`, `Table`, `Input`, `EmptyState`).
- `components/layout`: Structural scaffolding (`AppShell`, `Sidebar`, `TopNavbar`).

```
frontend/
├── app/
│   ├── (auth)/             # Auth layouts, login, register, password recovery
│   ├── (dashboard)/        # Main SaaS modules
│   │   ├── analytics/      # Yield trends, defect breakdown charts
│   │   ├── inspections/    # Ingest, batch uploads, inspection detail [id]
│   │   ├── models/         # Deep learning model registry
│   │   ├── products/       # Part catalog and config thresholds
│   │   ├── reports/        # Compliance reports & CSV audit logs
│   │   ├── settings/       # Organization settings
│   │   └── team/           # Member invitations & role management
│   ├── layout.tsx          # Root HTML layout with Inter font and dark theme
│   ├── page.tsx            # Executive Operations Dashboard
│   ├── error.tsx           # Global Next.js error boundary
│   └── loading.tsx         # Route transition skeleton loader
├── components/
│   ├── layout/             # Shell, collapsible Sidebar, TopNavbar
│   └── ui/                 # Reusable atomic UI components
├── lib/
│   ├── api-client.ts       # Fetch wrapper with typed error handling
│   └── utils.ts            # clsx / twMerge class variance utilities
```

---

## 2. Design System & Design Tokens

### 2.1 Color Palette (`frontend/tailwind.config.ts`)
- **Background & Surfaces:** Deep industrial slate and navy:
  - `navy-950` (`#070d18`): Main viewport and sidebar background.
  - `slate-900` (`#0f172a`): Card, modal, and drawer backgrounds.
  - `slate-800` (`#1e293b`): Borders, dividers, table headers.
- **Brand & Action Accents:**
  - `brand-600` (`#2563eb`): Primary interactive elements and call-to-actions.
  - `brand-500` (`#3b82f6`): Hover and focus rings.
- **Defect Severity Semantics:**
  - `emerald-500`: Acceptable / Zero-Defect / Normal Pass.
  - `amber-500`: Minor Defect / Low Confidence / Review Required.
  - `rose-500`: Critical Surface Defect / Immediate Reject.

### 2.2 Typography
- Body: `Inter`, system sans-serif with geometric clarity for rapid reading of numerical metrics.
- Monospace: `JetBrains Mono` / `ui-monospace` for Product SKUs, Batch IDs, Bounding Box coordinates, and timestamps.

---

## 3. UI Component Library Evaluation

| Component | File Path | Variance / Props | Strengths | Areas for Improvement |
|---|---|---|---|---|
| `Button` | `components/ui/Button.tsx` | `primary`, `secondary`, `destructive`, `outline`, `ghost`, `sm`/`md`/`lg` | Clean Tailwind styling, spinner integration, disabled state handling | Add keyboard focus-visible indicator ring |
| `Card` | `components/ui/Card.tsx` | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter` | Modular sub-components, consistent borders | Add elevated / interactive hover states |
| `Badge` | `components/ui/Badge.tsx` | `default`, `success`, `warning`, `destructive`, `outline` | Semantic status chips for defect categories | Support icon prefix inside badge |
| `Table` | `components/ui/Table.tsx` | Header, Body, Row, Head, Cell | Clean tabular layout, responsive horizontal scrolling | Built-in sorting headers and pagination bar |
| `Input` | `components/ui/Input.tsx` | Standard input with label and error message | Clean error feedback text | Add password reveal toggle and search icon slot |
| `EmptyState` | `components/ui/EmptyState.tsx` | Title, description, action button, custom icon | Standardized empty placeholder throughout app | Add illustration or animation options |

---

## 4. Accessibility (a11y) & Usability Findings

1. **Color Contrast:** The dark palette achieves contrast ratios exceeding 7:1 for normal body text (`slate-200` on `slate-900`), complying with WCAG 2.1 Level AAA requirements.
2. **Form Labels:** All inputs in `products/new`, `login`, and `register` use explicit `<label htmlFor="...">` associations.
3. **Missing ARIA Roles in Ingest Dropzone:** The file dropzone in `/inspections` requires explicit `role="region"` and `aria-label="Upload surface scan image"` for screen readers.
4. **Keyboard Traps:** No keyboard traps were identified. Tab navigation smoothly traverses form fields and action buttons.

---

## 5. Frontend Performance & Core Web Vitals

- **Prerendered Routes:** 14 out of 14 static and dynamic routes compile cleanly with zero TypeScript errors (`npm run type-check`).
- **First Contentful Paint (FCP):** Estimated < 0.8s on typical factory terminals due to static layout shell generation.
- **Largest Contentful Paint (LCP):** Pre-optimized by utilizing Next.js font optimization and lightweight SVG icons via `lucide-react`.
- **Bundle Footprint:** Minimal third-party JavaScript dependencies; absence of heavy charting libraries keeps client-side hydration payload under 180KB gzip.

---

## 6. Recommended Frontend Enhancements (Backlog)

1. **`IRONORY-UI-001` (Auth Token Interceptor):** Update `frontend/lib/api-client.ts` to automatically extract the JWT token and tenant ID from `localStorage`/cookies and attach `Authorization: Bearer <token>` and `X-Organization-ID`.
2. **`IRONORY-UI-002` (Live WebSocket Ingest Feed):** Replace HTTP polling for long-running batch inspection jobs with a persistent WebSocket connection to render live real-time inspection progress.
3. **`IRONORY-UI-003` (Interactive Heatmap Opacity Slider):** Add a visual opacity slider on `/inspections/[id]` to smoothly blend between the raw visual asset and the Grad-CAM activation overlay.
