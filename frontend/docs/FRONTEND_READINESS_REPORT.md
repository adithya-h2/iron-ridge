# Frontend Foundation Readiness Report

**Project:** Iron Ridge Intelligent Sales Workflow  
**Scope:** Foundation only (no business UI)  
**Date:** 2026-07-10

## Deliverables Checklist

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | `frontend/` at repo root beside `backend/` | Done |
| 2 | Next.js App Router + TypeScript + Tailwind + `src/` | Done |
| 3 | shadcn/ui design system initialized | Done |
| 4 | Iron Ridge design tokens (CSS + `design-tokens.ts`) | Done |
| 5 | Light/dark theme (`next-themes` + navbar toggle) | Done |
| 6 | Folder structure (`features/`, `services/`, `components/`, etc.) | Done |
| 7 | App shell (Navbar, Sidebar, Footer, mobile Sheet) | Done |
| 8 | Axios API client + JWT interceptors | Done |
| 9 | 8 service wrappers aligned to backend | Done |
| 10 | `ApiResponse` / domain TypeScript types | Done |
| 11 | TanStack Query provider + devtools | Done |
| 12 | Auth context, storage, ProtectedRoute, RoleGuard | Done |
| 13 | Global components (PageHeader, StatCard, Timeline stub, etc.) | Done |
| 14 | Form wrappers (RHF + shadcn Form) | Done |
| 15 | Placeholder routes for all modules | Done |
| 16 | `.env.example` + README | Done |
| 17 | Build / lint verification | See below |

## Service → Backend Mapping

| Service | Backend endpoints |
|---------|-------------------|
| `auth.ts` | `/auth/login`, `/auth/me`, `/auth/register` |
| `lead.ts` | `POST /api/v1/leads` |
| `workflow.ts` | `/api/v1/workflows/{deal_id}`, timeline, retry |
| `dashboard.ts` | `/dashboard/summary`, pipeline, agents, revenue, orders, approvals |
| `approval.ts` | `/approvals/*` |
| `notification.ts` | `POST /api/v1/notifications` |
| `order.ts` | `/orders/*` |
| `tracking.ts` | `/audit`, workflow timeline |

## Verification

Run from `frontend/`:

```bash
npm install
npm run build
npm run lint
npm run dev
```

### Manual checks

- [ ] Home page loads at `http://localhost:3000`
- [ ] Theme toggle switches light/dark mode
- [ ] Sidebar navigates to all placeholder routes
- [ ] Mobile sheet navigation opens on small viewports
- [ ] No hardcoded API URLs in source (env only)
- [ ] `NEXT_PUBLIC_API_URL` set in `.env.local`

### CORS note

Backend `ALLOWED_ORIGINS` must include `http://localhost:3000`. No backend changes were made in this sprint.

## Ready for Module 1

The foundation provides:

- Layout shell and navigation
- API service layer with typed envelopes
- Auth context and service methods (login UI pending)
- TanStack Query + form component wrappers
- Design system and global UI primitives

Module 1 can implement login UI, wire `ProtectedRoute` into dashboard layout, and build feature pages on top of existing services and components.
