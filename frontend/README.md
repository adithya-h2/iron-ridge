# Iron Ridge — Sales Operations Frontend

A React + Vite + TypeScript dashboard for the Iron Ridge Intelligent Sales Workflow.
Built to sit on top of the FastAPI backend Adithya built, orchestrated by n8n, with
Victor's Slack approval step surfaced as a real UI.

## Running it right now (no backend needed)

```bash
npm install
npm run dev
```

Open `http://localhost:5173`. This runs entirely on realistic mock data — every
page works, every interaction (approve/reject a deal) works — with zero backend
required. This is intentional: you can build/demo the UI independently of
backend setup issues.

## Pages

| Page | What it shows |
|---|---|
| **Dashboard** | KPI counts + all active deals |
| **Pipeline** | Kanban board of every deal grouped by stage |
| **Deal detail** | Full deal info + the **stage rail** (visual progress) + **audit trail** (every stage transition, timestamped) |
| **Approvals** | Victor's queue — approve/reject, with **SLA overdue flagging** if a deal has waited past `approval_sla_hours` |
| **System Health** | Failed/retrying agent calls, so backend/n8n issues are visible instead of silent |
| **Settings** | Shows current backend connection config |

## Connecting to the real backend

Everything routes through **one file**: `src/api/client.ts`. To go live:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_USE_MOCKS=false
   ```
3. Confirm the real endpoint paths in `app/api/routes/` match the `ENDPOINTS`
   object at the top of `src/api/client.ts`. Update if they differ — these are
   currently best-guesses based on the pipeline README:
   - `GET  /deals`
   - `GET  /deals/:id`
   - `GET  /deals/:id/events`
   - `POST /deals/:id/approve`
   - `POST /deals/:id/reject`
   - `GET  /deals/stats/by-stage`
   - `GET  /jobs`
4. Confirm the JSON shapes returned match `src/types/deal.ts` (`Deal`,
   `DealEvent`, `AgentJob`, `StageCount`). This is the other file to edit if
   the backend's real Pydantic schemas differ — field names especially
   (`org_name` vs `organization_name`, etc.).

**If an endpoint above doesn't exist on the backend yet**, that's expected —
this frontend was designed slightly ahead of confirmed backend routes for:
- `deals/:id/events` (audit trail) — needs a `deal_events` table + endpoint
- `jobs` (system health) — needs failed/retrying agent call logging
- `approval_sla_hours` / `approval_requested_at` on `Deal` — needed for the
  SLA overdue flag on the Approvals page

Flag these to your backend teammate rather than faking the data — they map
directly to the "audit trail," "error visibility," and "SLA escalation"
improvements in the project plan.

## Design notes

Dark, dispatch-console aesthetic (deep charcoal base, amber "signal" accent,
red "alarm" for rejections/overdue, green "clear" for completed) — deliberately
themed around the emergency-vehicle sales domain rather than a generic SaaS
look. The **stage rail** (a route-map style progress indicator) is the
signature element, reused on the dashboard and deal detail pages so a deal's
position in the pipeline is always visually legible at a glance. Light mode is
available via the toggle in the top bar.

## Tech stack

React 18, TypeScript, Vite, React Router, Tailwind CSS, lucide-react icons.
No state management library — data volume doesn't warrant Redux/Zustand yet;
each page fetches what it needs via `src/api/client.ts`. Revisit if the app
grows shared cross-page state.
