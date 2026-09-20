# Advanced Point of Sale & Library Management API Engine

A robust, enterprise-grade RESTful API built with FastAPI, SQLAlchemy, and PostgreSQL that implements a comprehensive Point of Sale (POS) book retail system alongside an automated library book rental and tracking facility.

## Architectural Pillars

- **Clean Architecture Pattern:** Strict segregation of project boundaries spanning Models ──► Schemas ──► Repositories ──► Services ──► Routers to maximize testability and maintenance decoupling.

- **Automated Inventory Lifecycle Engine:** Fully integrated, transactional service logic that maintains stock counts safely without race conditions:
  - Submitting a retail transaction line item automatically validates title availability and decrements the book's `retail_stock`.
  - Submitting a library rental checkout dynamically validates and decrements the book's shelf-allocated `library_stock`.
  - Logging an `actual_return` timestamp via a PUT request on library rentals instantly triggers a symmetric relationship traversal to increment stock counts back onto shelf balances.

- **Data Integrity & Relational Guardrails:** Active foreign key database validations mapping categories, suppliers, items, users, and customers to eliminate orphan rows, outputting clean HTTP exceptions rather than server-crashing tracebacks.

## Automated Test Suite & Continuous Integration

The API ships with a comprehensive Pytest suite covering every router: happy-path CRUD flows, schema validation failures (`422`), missing/invalid credentials (`401`), insufficient permissions (`403`), missing resources (`404`), and role-based ownership filtering (e.g. a customer retrieving only their own sales, rentals, and receipts).

**Test isolation:** The suite runs against an in-memory SQLite database, fully decoupled from the PostgreSQL development database. Each test function gets a fresh schema via `Base.metadata.create_all`/`drop_all`, and the app's `get_db` dependency is overridden for the duration of the test session — no risk of touching real data.

### Running Tests Locally

From the `app/` directory, with your virtual environment activated:

```bash
pip install -r requirements.txt
pytest -v
```

To run a single test file:

```bash
pytest tests/test_books.py -v
```

### Continuous Integration

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs the full suite automatically on every push and pull request targeting `main`. It checks out the repository, sets up Python 3.10, installs dependencies, and fails the build if any test fails — ensuring the `main` branch always stays in a known-good, fully tested state.
