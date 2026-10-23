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
The landing page is at `/` and the dashboard is at `/dashboard`. Use the
landing page's **Browse carts** link to open the dashboard, and the dashboard's
CoCart logo to return home. Direct visits and reloads of `/dashboard` work with Vite;
production hosting must serve `index.html` for app routes as well.

Each page imports its own CSS. Landing styles are scoped to `.landing-page`
and dashboard styles to `.dashboard-page`; `index.css` contains shared defaults.
The dashboard still uses sample carts and filters. Login, signup, start-cart,
join-cart, and filter actions remain placeholders for later integration.

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

