# CoCart

CoCart is a React frontend with a FastAPI backend.

## Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The shared `frontend/index.html` loads `src/main.jsx`, which renders `App.jsx`.
The landing page is at `/`, the dashboard at `/dashboard`, and signup at `/signup`.
React Router handles navigation between screens without reloading the app.
The landing page links to both screens. Direct visits and reloads work with Vite;
production hosting must serve `index.html` for app routes as well.

```text
frontend/src/
  App.jsx                 Defines the page routes
  main.jsx                Starts React, BrowserRouter, and global styles
  global.d.ts             TypeScript declaration for CSS imports
  pages/                  Landing, dashboard, and signup screens
  components/dashboard/   Dashboard content, cart cards, and filter buttons
  data/dashboard.ts       Temporary sample carts and filters
  types/cart.ts           Cart data used by the dashboard components
  styles/                 Global defaults and a stylesheet for each page
  lib/                    Supabase client setup
  services/               Authentication helpers and future API requests
```

Pages import their own stylesheet, with selectors scoped to the page's wrapper
class. Keep shared defaults and resets in `styles/global.css`.

Keep shared state, such as the signed-in user or active cart, above the routes
so it stays mounted during navigation. State local to a page resets when that
page unmounts. Refreshing reloads the app, so session restoration still needs
to come from the authentication service or persistent storage.

`DashboardPage` owns the cart and filter state; dashboard components receive data
through props. When connecting the backend, put requests in `services/`, map the
API response to `CartDetails`, and load the results in `DashboardPage` instead of
the sample data in `data/dashboard.ts`.

The dashboard still uses sample carts and filters. Signup renders the existing
screen; authentication, start-cart, join-cart, and filter actions remain
placeholders for later integration.

Run frontend checks with:

```bash
cd frontend
npm ci
npm run build
npm run lint
npm run test -- --run
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

