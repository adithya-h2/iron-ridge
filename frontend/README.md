# Iron Ridge Frontend

Next.js App Router frontend for Iron Ridge — public marketing site and internal sales platform.

## Prerequisites

- Node.js 20+
- npm
- FastAPI backend running (default `http://localhost:8000`)

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | FastAPI base URL (required for forms) |
| `NEXT_PUBLIC_SITE_URL` | Public site URL for SEO metadata (default `http://localhost:3000`) |

Ensure the backend `ALLOWED_ORIGINS` includes `http://localhost:3000` for CORS.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server |
| `npm run build` | Production build + type check |
| `npm run lint` | ESLint |
| `npm run start` | Start production server |

## Architecture

```
src/
├── app/
│   ├── (marketing)/     # Public website (Module 1)
│   ├── app/             # Internal portal stubs (Module 0)
│   └── (auth)/          # Login stub
├── components/
│   ├── marketing/       # Public site components
│   ├── layout/          # Internal portal shell
│   ├── ui/              # shadcn primitives
│   └── forms/           # RHF form wrappers
├── content/             # Static marketing copy
├── features/            # consultation, auth, etc.
├── services/            # Axios API wrappers
└── lib/                 # seo, design tokens, utils
```

## Public site (Module 1)

| Route | Page |
|-------|------|
| `/` | Home |
| `/products` | Vehicle catalog |
| `/industries` | Industry segments |
| `/process` | Procurement process |
| `/about` | About Iron Ridge |
| `/contact` | Contact + form |
| `/request-consultation` | Consultation form → `POST /api/v1/leads` |
| `/track-order` | Placeholder |

## Internal portal (Module 0)

Dashboard stubs at `/app/dashboard`, `/app/leads`, `/app/workflow`, etc. Not linked from the public site.

## Backend connection

- **Consultation / contact forms:** `POST /api/v1/leads` (no auth required)
- **Internal portal (future):** JWT via `POST /auth/login`

See:

- `docs/FRONTEND_READINESS_REPORT.md` — Module 0 foundation checklist
- `docs/FRONTEND_MODULE1_READINESS_REPORT.md` — Module 1 public site checklist
