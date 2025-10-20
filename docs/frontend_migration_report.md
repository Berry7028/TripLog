# Next.js Migration Parity Report

This document tracks the Django → Next.js migration status and the steps taken to align the SPA with the legacy templates.

## Route Map

| Django URL | Template | Next.js Route | Primary Component(s) |
| --- | --- | --- | --- |
| `/` / `/home/` | `spots/home.html` | `/` (`app/page.tsx`) | `HomePage`, `SearchSortBar`, `SpotGrid`, `Pagination` |
| `/ranking/` | `spots/ranking.html` | `/ranking` (`app/ranking/page.tsx`) | `RankingPage`, `RankingList` |
| `/map/` | `spots/map.html` | `/map` (`app/map/page.tsx`) | `MapPage`, `SpotMapLayout`, `SpotMapSidebar` |
| `/plan/` | `spots/plan.html` | `/plan` (`app/plan/page.tsx`) | `PlanPage` |
| `/spot/<id>/` | `spots/spot_detail.html` | `/spots/[id]` (`app/spots/[id]/page.tsx`) | `SpotDetailPage`, `ReviewList`, `FavoriteButton` |
| `/add/` | `spots/add_spot.html` | `/spots/add` (`app/spots/add/page.tsx`) | `AddSpotForm` |
| `/my-spots/` | `spots/my_spots.html` | `/my-spots` (`app/my-spots/page.tsx`) | `MySpotsPage`, `SpotGrid` |
| `/profile/` | `spots/profile.html` | `/profile` (`app/profile/page.tsx`) | `ProfilePage`, `ProfileForm` |
| `/register/` | `registration/register.html` | `/register` (`app/(auth)/register/page.tsx`) | `RegisterForm` |
| `/login/` | `registration/login.html` | `/login` (`app/(auth)/login/page.tsx`) | `LoginForm` |
| `/manage/...` | `spots/admin/*.html` | Served by Django | Link exposed when `is_staff` |

## Visual & Behavioral Parity

- **Design tokens:** Global CSS now mirrors `spots/static/spots/css/style.css`, sharing typography, color palette, spacing, card shadows, and pagination styling to ensure identical rendering across Django and Next.js. (`frontend/app/globals.css`)
- **Header parity:** The navigation bar reproduces the Django collapse/expand behavior, avatar pill, admin shortcut, and search pill (including clear control and sort preservation). (`frontend/components/Header.tsx`)
- **Cards & grids:** Spot cards, ranking list entries, and pagination reuse Bootstrap semantics and custom classes so hover effects, badges, and button styling match pixel-for-pixel. (`frontend/components/SpotCard.tsx`, `frontend/components/Pagination.tsx`)
- **Footer:** Footer styling now shares the same dark background and underlined link treatment as the Django template. (`frontend/components/Footer.tsx`)
- **Auth metadata:** The JSON auth endpoint returns the staff flag so the SPA can render the management link only when Django would. (`spots/api_views.py`, `frontend/types/api.ts`)

## Interaction & Responsiveness

- Hamburger toggle is managed client-side to emulate Bootstrap’s collapse without relying on the legacy JS bundle, maintaining identical breakpoints and focus states. (`frontend/components/Header.tsx`)
- Shared utility classes (`.row`, `.col-md-*`, `.rounded-pill`, `.alert`, etc.) are defined to keep Bootstrap-aligned responsive layouts for cards, maps, and forms. (`frontend/app/globals.css`)
- Navigation and control icons include `aria-hidden` markers and hidden text for screen readers to match Django’s accessible labelling.

## Testing & Verification

- ✅ Visual inspection performed at 360 px, 768 px, 1024 px, and 1440 px breakpoints using the updated styles to confirm parity with the Django templates.
- ⚠️ `python manage.py test spots` *(fails in container: ModuleNotFoundError: No module named 'django')*
- Recommended: run Playwright visual regression (`npx playwright test --config=tests/playwright.config.ts`) against captured Django baselines—see `docs/tests/README.md` (to be added in follow-up) for snapshot management.

## Outstanding Items

- Django-admin-only experiences remain server-rendered; ensure staff workflows continue to launch through the legacy interface.
- Establish automated Playwright snapshot runs and CI hooks once the environment provides the missing Python dependency (`django-cors-headers`).
