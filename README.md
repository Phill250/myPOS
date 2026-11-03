# Charisma Library POS

A full-stack point-of-sale and lending system for Charisma Library, a bookshop and lending library in Kigali.

- **Till:** search or scan books, build a sale, take cash, MTN MoMo, Airtel Money, card or bank transfer, work out change, print a receipt.
- **Library desk:** lend books to members with a due date, check them back in, and charge late fees automatically.
- **Back office:** books and stock, customers and members, sales history (with voiding), categories, suppliers, staff accounts.
- **Today screen:** what came in today, the last 7 days, overdue loans, books running low, best sellers.
- **Customer portal:** members sign in to see the books they have out, their due dates and their receipts.

```
charisma-pos/
├── backend/    FastAPI + SQLAlchemy + PostgreSQL (tests use SQLite)
└── frontend/   React + TypeScript + Vite
```

## Run it locally

You need **Python 3.10+**, **Node 20+** and **PostgreSQL**.

### 1. Backend (http://localhost:8000)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit DATABASE_URL and JWT_SECRET_KEY
createdb mypos_db                  # or create it in pgAdmin

python seed_demo_data.py           # optional: sample books, customers, sales, loans
uvicorn main:app --reload
```

Open http://localhost:8000/docs to try every endpoint.

Without demo data, create the first administrator with `python seed_super_admin.py`.

### 2. Frontend (http://localhost:5173)

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env               # VITE_API_URL=http://localhost:8000
npm run dev
```

### Demo accounts (after `seed_demo_data.py`)

| Username | Password    | Role          |
|----------|-------------|---------------|
| admin    | admin123    | Administrator |
| cashier  | cashier123  | Staff         |
| aline    | aline123    | Customer      |

Change or delete these before using the system in the real shop.

## Upgrading an existing database

If your database was created by the first version of the API, run this once:

```bash
psql -U postgres -d mypos_db -f backend/migrations/001_charisma_v2.sql
```

It adds a `paid_at` time to payments and makes customer email optional. A new, empty database doesn't need it.

## How the backend is organised

Each feature follows the same path: **models → schemas → repositories → services → routers**.

The original CRUD endpoints (`/books`, `/sales`, `/library-rentals`, …) are unchanged. On top of them, `/pos` holds the workflows the frontend uses. Each one is a single database transaction, so a sale or a loan is either saved completely or not at all.

| Endpoint | What it does |
|---|---|
| `POST /pos/sales` | Checkout: creates the sale and its lines, reduces stock, records the payment, issues a receipt number |
| `GET /pos/sales`, `GET /pos/sales/{id}` | Sales history and full receipts (customers only see their own) |
| `POST /pos/rentals` | Lend one or more books to a library member |
| `POST /pos/rentals/{id}/return` | Check books back in, restock, charge the late fee |
| `GET /pos/rentals?status=open\|overdue\|returned` | Loans with borrower and book details |
| `GET /pos/dashboard` | Figures for the Today screen |
| `GET /users/me` | The signed-in user and their linked customer profile |

### Rules worth knowing

- Roles: `customer`, `staff`, `super_admin`. Anyone can register, but always as a customer. Staff link a customer's account to their customer profile from the Customers page.
- Only library members can borrow books. The late fee is `LATE_FEE_PER_DAY` (default 200 RWF) per day late, and staff can change or waive it at check-in.
- Voiding a sale, deleting an open loan, or removing a line puts the copies back in stock.
- Deleting something still used by sales or loans (a book, a customer, a category) returns `409` with a clear message instead of crashing.
- Times are shown in Kigali time (UTC+2). Settings live in `backend/.env`; see `.env.example`.

## Tests

```bash
cd backend && pytest -q          # 241 tests
cd frontend && npm run build     # type-check + production build
```

GitHub Actions runs both on every push and pull request to `main`.
