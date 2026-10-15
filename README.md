# CoCart

CoCart is a React frontend with a FastAPI backend.

## Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
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

