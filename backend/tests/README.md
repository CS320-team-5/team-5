# Backend tests

Run from `backend/`:

```bash
pytest -v                 # all offline tests
pytest -v tests/users     # user routes, services, repository
pytest -v tests/auth      # authentication dependency
pytest -v tests/carts     # existing cart tests
```

`conftest.py` provides reusable fixtures for the FastAPI `TestClient`,
mock database client, authenticated session, and dependency cleanup.
Tests under `users/` separate HTTP contract, business rules, and query shape.
Mocks are applied at the boundary each test is targeting:

- Router tests replace the service callable referenced by the router.
- Service tests replace repository calls.
- Repository tests inspect queries on a fake Supabase client.
- Authentication tests fake Supabase Auth responses rather than using real tokens.

No test uses real Supabase credentials. New integration tests that need a
separate test database should be explicitly marked `@pytest.mark.integration`
and run by a dedicated workflow rather than as part of normal unit tests.
