# CoCart

CoCart is a React frontend with a FastAPI backend.

## Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

### Frontend structure

```text
frontend/
  index.html               Shared HTML entry point
  public/                  Static assets served directly, such as delivery.svg
  src/
    main.jsx               Starts React and imports global styles once
    App.jsx                Composes the app and selects which page to render
    pages/
      LandingPage.jsx      Landing page content
    styles/
      global.css           Shared typography defaults and resets
      landing.css          Styles scoped to .landing-page
```

Organize files by their role in the app. Full screens belong in `src/pages/`;
use `src/components/` for UI reused across pages and `src/layouts/` for shared
page shells when those are needed. Keep service clients in `src/lib/` and API
or authentication helpers in `src/services/`. Add these folders when they have
an implementation to contain.

Pages import their own stylesheet from `src/styles/`. Scope page-specific CSS
under a page class, such as `.landing-page`, so selectors do not change another
screen. Keep only app-wide defaults and resets in `global.css`.

When integrating the dashboard, move its page to `src/pages/Dashboard.tsx`
and its stylesheet to `src/styles/dashboard.css`. Import the stylesheet from
the dashboard page, scope its rules under a dashboard wrapper class, and connect
the page through `App.jsx`. Reusable pieces such as cart cards can move into
`src/components/`. Continue using the shared `index.html` and `main.jsx` entry
points; a separate `dashboard.html` is not needed for an in-app page.

The landing page's login and signup buttons are visual placeholders until the
authentication screens are connected.

Before opening a frontend PR, run:

```bash
cd frontend
npm run build
npm run lint
```

## Backend

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and `GET /health` returns its health status.

