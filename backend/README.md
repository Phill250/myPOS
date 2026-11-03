# Charisma Library POS — backend

FastAPI + SQLAlchemy API for book sales and library lending. See the [main README](../README.md) for setup, endpoints and business rules.

## Architecture

Models ──► Schemas ──► Repositories ──► Services ──► Routers

- `routers/pos.py` + `services/pos.py`: checkout, lending, returns, history, dashboard. Each action is one transaction.
- The other routers are the original per-table CRUD endpoints.
- `core/config.py` reads all settings from the environment / `.env`.

## Tests

The suite runs against an in-memory SQLite database. Each test gets a fresh schema, so it never touches your real data.

```bash
pip install -r requirements.txt
pytest -q
```
