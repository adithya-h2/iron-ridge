# Frontend Module 1 Readiness Report

**Project:** Iron Ridge Public Digital Experience  
**Scope:** Public marketing website + consultation form  
**Date:** 2026-07-10

## 1. Folder Structure

```
frontend/src/
├── app/
│   ├── (marketing)/          # Public site routes
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Home
│   │   ├── products/
│   │   ├── industries/
│   │   ├── process/
│   │   ├── about/
│   │   ├── contact/
│   │   ├── request-consultation/
│   │   ├── track-order/
│   │   ├── privacy/
│   │   └── terms/
│   ├── app/                    # Internal portal (Module 0 stubs)
│   │   ├── layout.tsx
│   │   └── dashboard|leads|workflow|orders|approvals|tracking|settings/
│   ├── (auth)/login/
│   ├── layout.tsx
│   └── not-found.tsx
├── components/marketing/       # Public site components
├── content/                    # Static copy and data
├── features/consultation/      # Lead form + contact form
└── lib/seo.ts                  # Metadata + JSON-LD helpers
```

## 2. Components Created

| Component | Path |
|-----------|------|
| Container | `components/marketing/container.tsx` |
| Section | `components/marketing/section.tsx` |
| PublicNavbar | `components/marketing/public-navbar.tsx` |
| PublicFooter | `components/marketing/public-footer.tsx` |
| Hero | `components/marketing/hero.tsx` |
| TrustedBy | `components/marketing/trusted-by.tsx` |
| FeatureCard | `components/marketing/feature-card.tsx` |
| VehicleCard | `components/marketing/vehicle-card.tsx` |
| IndustryCard | `components/marketing/industry-card.tsx` |
| ProcurementTimeline | `components/marketing/procurement-timeline.tsx` |
| StatsRow | `components/marketing/stats-row.tsx` |
| CtaBanner | `components/marketing/cta-banner.tsx` |
| PageHero | `components/marketing/page-hero.tsx` |
| FadeIn / SlideUp / Stagger | `components/marketing/motion.tsx` |
| ConsultationForm | `features/consultation/form.tsx` |
| ContactForm | `features/consultation/contact-form.tsx` |

## 3. Pages Created

| Route | Description |
|-------|-------------|
| `/` | Premium home page with hero, trusted-by, features, vehicles, timeline, stats, CTA |
| `/products` | Vehicle catalog with specs and Request Quote CTAs |
| `/industries` | Industry segments grid |
| `/process` | Procurement process timeline |
| `/about` | Mission, manufacturing, engineering, quality, safety, compliance |
| `/contact` | Office info, map, business hours, contact form |
| `/request-consultation` | Multi-section consultation form |
| `/track-order` | Placeholder (coming soon) |
| `/privacy` | Privacy policy |
| `/terms` | Terms of service |
| `404` | Branded not-found page |

Internal portal migrated to `/app/*` (not linked from public nav).

## 4. Backend APIs Connected

| Feature | Endpoint | Auth |
|---------|----------|------|
| Request Consultation | `POST /api/v1/leads` | None (public) |
| Contact Form | `POST /api/v1/leads` | None (public) |

Payload: `source: "WEBSITE"`, `submission_channel: "web_form"` or `"contact_form"`.  
Flow: Frontend → FastAPI → n8n (no direct n8n calls from browser).

## 5. Performance Optimizations

- Server Components for all marketing pages (client islands only for navbar scroll, motion, forms)
- `next/image` with `sizes`, `priority` on hero, lazy loading elsewhere
- Static prerendering for all marketing routes
- Remote image domain restricted to `images.unsplash.com` in `next.config.ts`
- Framer Motion uses `viewport={{ once: true }}` to avoid repeat animations

## 6. Accessibility Checklist

- [x] Semantic HTML (`header`, `nav`, `main`, `footer`, `section`, `fieldset`, `legend`)
- [x] One `h1` per page
- [x] Navbar keyboard accessible with mobile menu toggle (`aria-expanded`, `aria-label`)
- [x] Form labels associated with inputs via shadcn Form
- [x] Success/error states use `aria-live="polite"`
- [x] Focus management on consultation success (tabIndex + focus)
- [x] Alt text on all images
- [x] Sufficient color contrast (charcoal on white, red CTAs on white)

## 7. Responsive Checklist

- [x] Desktop-first layouts with `max-w-7xl` containers
- [x] Tablet: 2-column grids at `md:` breakpoint
- [x] Mobile: single column, hamburger nav, stacked hero CTAs
- [x] Timeline: horizontal on desktop, vertical on process page
- [x] Stats: 2×2 grid on mobile, 4 columns on desktop

## 8. SEO Checklist

- [x] Per-page `metadata` via `createPageMetadata()`
- [x] OpenGraph + Twitter cards
- [x] `metadataBase` from `NEXT_PUBLIC_SITE_URL`
- [x] JSON-LD Organization schema on home
- [x] JSON-LD WebPage schema on interior pages
- [x] Canonical URLs
- [x] Proper heading hierarchy

## 9. Production Readiness Summary

| Criterion | Status |
|-----------|--------|
| `npm run build` | Pass |
| `npm run lint` | Pass |
| Strict TypeScript | Pass |
| No customer-facing AI/agent language | Pass |
| US enterprise design language | Pass |
| Consultation form wired to backend | Pass |
| Dashboard at `/app/*` | Pass |
| Module 0 foundation intact | Pass |

## 10. Verification Steps

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL and NEXT_PUBLIC_SITE_URL
npm run build
npm run lint
npm run dev
```

Manual verification:

1. Open http://localhost:3000 — home hero, transparent navbar, scroll to solid
2. Navigate all public routes via navbar and footer
3. Submit consultation form with backend running (`uvicorn` on :8000)
4. Confirm success reference ID (`deal_id`) displays
5. Test `/request-consultation?vehicle=Ambulance` pre-fills vehicle type
6. Toggle mobile menu on small viewport
7. Visit `/app/dashboard` — internal portal shell (not linked from public site)
8. Visit invalid URL — branded 404

**CORS:** Backend `ALLOWED_ORIGINS` must include `http://localhost:3000`.
