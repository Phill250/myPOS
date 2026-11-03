"""Till and library-desk workflows.

Each public function here is ONE database transaction: either everything
(sale + lines + stock + payment + receipt) is saved, or nothing is. That is
what stops a half-finished sale from eating stock when something fails.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from core.config import (
    LATE_FEE_PER_DAY,
    LOW_STOCK_THRESHOLD,
    RECEIPT_PREFIX,
    UTC_OFFSET_HOURS,
)
from models.books import Book
from models.customers import Customer
from models.library_rental_items import LibraryRentalItem
from models.library_rentals import LibraryRental
from models.payments import Payment
from models.receipts import Receipt
from models.retail_sale_items import RetailSaleItem
from models.retail_sales import RetailSale
from schemas.pos import RentalCheckout, RentalReturn, SaleCheckout

LOCAL_TZ = timezone(timedelta(hours=UTC_OFFSET_HOURS))


# ---------- small helpers ----------


def today_local() -> date:
    return datetime.now(LOCAL_TZ).date()


def to_local(dt: datetime) -> datetime:
    if dt.tzinfo is None:  # SQLite hands back naive UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ)


def _bad_request(detail: str):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _not_found(detail: str):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _forbidden(detail: str):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _full_name(customer: Customer | None) -> str | None:
    if customer is None:
        return None
    return f"{customer.first_name} {customer.last_name}".strip()


def _receipt_number(kind: str, record_id: int) -> str:
    return f"{RECEIPT_PREFIX}-{kind}-{today_local():%Y%m%d}-{record_id:05d}"


def _linked_customer_id(user) -> int | None:
    profile = getattr(user, "customer_profile", None)
    return profile.customer_id if profile else None


def _payment_out(p: Payment) -> dict:
    return {
        "payment_id": p.payment_id,
        "amount": p.amount,
        "payment_method": p.payment_method,
        "transaction_type": p.transaction_type,
        "paid_at": p.paid_at,
    }


# ---------- retail sales ----------


def _sale_query(db: Session):
    return db.query(RetailSale).options(
        selectinload(RetailSale.items).selectinload(RetailSaleItem.book),
        selectinload(RetailSale.payments),
        selectinload(RetailSale.receipts),
        selectinload(RetailSale.customer),
        selectinload(RetailSale.user),
    )


def _sale_summary(sale: RetailSale) -> dict:
    payment = sale.payments[0] if sale.payments else None
    receipt = sale.receipts[0] if sale.receipts else None
    return {
        "sale_id": sale.sale_id,
        "sale_timestamp": sale.sale_timestamp,
        "total_amount": sale.total_amount,
        "customer_id": sale.customer_id,
        "customer_name": _full_name(sale.customer),
        "cashier": sale.user.username if sale.user else None,
        "item_count": sum(i.quantity for i in sale.items),
        "payment_method": payment.payment_method if payment else None,
        "receipt_number": receipt.receipt_number if receipt else None,
    }


def _sale_detail(sale: RetailSale) -> dict:
    data = _sale_summary(sale)
    data["items"] = [
        {
            "sale_item_id": i.sale_item_id,
            "book_id": i.book_id,
            "title": i.book.title if i.book else "(deleted book)",
            "author": i.book.author if i.book else "",
            "quantity": i.quantity,
            "unit_price": i.price_snapshot,
            "line_total": round(i.price_snapshot * i.quantity),
        }
        for i in sale.items
    ]
    data["payments"] = [_payment_out(p) for p in sale.payments]
    return data


def checkout_sale(db: Session, data: SaleCheckout, cashier) -> dict:
    if data.customer_id is not None and not db.get(Customer, data.customer_id):
        raise _not_found(f"Customer with id {data.customer_id} not found")

    # merge duplicate lines (same book scanned twice)
    wanted: dict[int, int] = defaultdict(int)
    for line in data.items:
        wanted[line.book_id] += line.quantity

    try:
        sale = RetailSale(
            total_amount=0, customer_id=data.customer_id, user_id=cashier.user_id
        )
        db.add(sale)

        total = 0
        for book_id, qty in wanted.items():
            # lock the row on PostgreSQL so two tills can't sell the last copy
            book = (
                db.query(Book).filter(Book.book_id == book_id).with_for_update().first()
            )
            if not book:
                raise _not_found(f"Book with id {book_id} not found")
            if book.retail_stock < qty:
                raise _bad_request(
                    f"Not enough stock for '{book.title}': "
                    f"{book.retail_stock} left, {qty} requested"
                )
            unit_price = float(book.sale_price)
            book.retail_stock -= qty
            total += round(unit_price * qty)
            sale.items.append(
                RetailSaleItem(book_id=book_id, quantity=qty, price_snapshot=unit_price)
            )

        sale.total_amount = total
        db.flush()  # gives us sale.sale_id

        sale.payments.append(
            Payment(
                amount=total,
                payment_method=data.payment_method,
                transaction_type="sale",
            )
        )
        sale.receipts.append(Receipt(receipt_number=_receipt_number("S", sale.sale_id)))
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_sale_detail(db, sale.sale_id, cashier)


def list_sales(db: Session, user, limit: int = 200, customer_id: int | None = None):
    query = _sale_query(db)
    if user.role == "customer":
        own = _linked_customer_id(user)
        if own is None:
            return []
        query = query.filter(RetailSale.customer_id == own)
    elif customer_id is not None:
        query = query.filter(RetailSale.customer_id == customer_id)
    sales = query.order_by(RetailSale.sale_id.desc()).limit(limit).all()
    return [_sale_summary(s) for s in sales]


def get_sale_detail(db: Session, sale_id: int, user) -> dict:
    sale = _sale_query(db).filter(RetailSale.sale_id == sale_id).first()
    if not sale:
        raise _not_found(f"Sale with id {sale_id} not found")
    if user.role == "customer" and sale.customer_id != _linked_customer_id(user):
        raise _forbidden("Not your sale")
    return _sale_detail(sale)


# ---------- library loans ----------


def _rental_query(db: Session):
    return db.query(LibraryRental).options(
        selectinload(LibraryRental.items).selectinload(LibraryRentalItem.book),
        selectinload(LibraryRental.payments),
        selectinload(LibraryRental.receipts),
        selectinload(LibraryRental.customer),
        selectinload(LibraryRental.user),
    )


def _days_overdue(rental: LibraryRental, on: date | None = None) -> int:
    end = rental.actual_return or on or today_local()
    return max(0, (end - rental.expected_return).days)


def _rental_status(rental: LibraryRental) -> str:
    if rental.actual_return is not None:
        return "returned"
    return "overdue" if today_local() > rental.expected_return else "active"


def _rental_summary(rental: LibraryRental) -> dict:
    receipt = rental.receipts[0] if rental.receipts else None
    return {
        "rental_id": rental.rental_id,
        "rental_timestamp": rental.rental_timestamp,
        "expected_return": rental.expected_return,
        "actual_return": rental.actual_return,
        "status": _rental_status(rental),
        "days_overdue": _days_overdue(rental),
        "customer_id": rental.customer_id,
        "customer_name": _full_name(rental.customer),
        "customer_phone": rental.customer.phone_number if rental.customer else None,
        "staff": rental.user.username if rental.user else None,
        "books": [
            {
                "rental_item_id": i.rental_item_id,
                "book_id": i.book_id,
                "title": i.book.title if i.book else "(deleted book)",
                "author": i.book.author if i.book else "",
            }
            for i in rental.items
        ],
        "receipt_number": receipt.receipt_number if receipt else None,
    }


def _rental_detail(rental: LibraryRental) -> dict:
    data = _rental_summary(rental)
    data["payments"] = [_payment_out(p) for p in rental.payments]
    data["late_fee_per_day"] = LATE_FEE_PER_DAY
    data["suggested_late_fee"] = (
        0 if rental.actual_return else _days_overdue(rental) * LATE_FEE_PER_DAY
    )
    return data


def checkout_rental(db: Session, data: RentalCheckout, staff) -> dict:
    customer = db.get(Customer, data.customer_id)
    if not customer:
        raise _not_found(f"Customer with id {data.customer_id} not found")
    if not customer.library_member:
        raise _bad_request(
            f"{_full_name(customer)} is not a library member. "
            "Make them a member before lending books."
        )
    if data.expected_return < today_local():
        raise _bad_request("The return date cannot be in the past")
    if len(set(data.book_ids)) != len(data.book_ids):
        raise _bad_request("The same book is listed twice on this loan")

    try:
        rental = LibraryRental(
            expected_return=data.expected_return,
            customer_id=customer.customer_id,
            user_id=staff.user_id,
        )
        db.add(rental)
        for book_id in data.book_ids:
            book = (
                db.query(Book).filter(Book.book_id == book_id).with_for_update().first()
            )
            if not book:
                raise _not_found(f"Book with id {book_id} not found")
            if book.library_stock < 1:
                raise _bad_request(f"'{book.title}' has no copies left on the shelf")
            book.library_stock -= 1
            rental.items.append(LibraryRentalItem(book_id=book_id))

        db.flush()
        if data.fee > 0:
            rental.payments.append(
                Payment(
                    amount=data.fee,
                    payment_method=data.payment_method,
                    transaction_type="rental_fee",
                )
            )
        rental.receipts.append(
            Receipt(receipt_number=_receipt_number("L", rental.rental_id))
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_rental_detail(db, rental.rental_id, staff)


def return_rental(db: Session, rental_id: int, data: RentalReturn, staff) -> dict:
    rental = _rental_query(db).filter(LibraryRental.rental_id == rental_id).first()
    if not rental:
        raise _not_found(f"Rental with id {rental_id} not found")
    if rental.actual_return is not None:
        raise _bad_request(f"This loan was already returned on {rental.actual_return}")

    returned_on = data.returned_on or today_local()
    if returned_on < to_local(rental.rental_timestamp).date():
        raise _bad_request("Return date is before the loan started")

    late_fee = data.late_fee
    if late_fee is None:
        late_fee = _days_overdue(rental, returned_on) * LATE_FEE_PER_DAY

    try:
        rental.actual_return = returned_on
        for item in rental.items:
            if item.book:
                item.book.library_stock += 1
        if late_fee > 0:
            rental.payments.append(
                Payment(
                    amount=late_fee,
                    payment_method=data.payment_method,
                    transaction_type="late_fee",
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_rental_detail(db, rental_id, staff)


def list_rentals(
    db: Session,
    user,
    status_filter: str = "all",
    limit: int = 300,
    customer_id: int | None = None,
):
    query = _rental_query(db)
    if user.role == "customer":
        own = _linked_customer_id(user)
        if own is None:
            return []
        query = query.filter(LibraryRental.customer_id == own)
    elif customer_id is not None:
        query = query.filter(LibraryRental.customer_id == customer_id)

    today = today_local()
    if status_filter == "returned":
        query = query.filter(LibraryRental.actual_return.isnot(None))
    elif status_filter in ("open", "active", "overdue"):
        query = query.filter(LibraryRental.actual_return.is_(None))
        if status_filter == "overdue":
            query = query.filter(LibraryRental.expected_return < today)
        elif status_filter == "active":
            query = query.filter(LibraryRental.expected_return >= today)

    rentals = query.order_by(LibraryRental.rental_id.desc()).limit(limit).all()
    return [_rental_summary(r) for r in rentals]


def get_rental_detail(db: Session, rental_id: int, user) -> dict:
    rental = _rental_query(db).filter(LibraryRental.rental_id == rental_id).first()
    if not rental:
        raise _not_found(f"Rental with id {rental_id} not found")
    if user.role == "customer" and rental.customer_id != _linked_customer_id(user):
        raise _forbidden("Not your rental")
    return _rental_detail(rental)


# ---------- dashboard ----------


def dashboard(db: Session) -> dict:
    today = today_local()
    week_start = today - timedelta(days=6)
    month_start = today - timedelta(days=29)
    # fetch a slightly wider window in UTC, then bucket by local date in Python
    since_utc = datetime.combine(
        month_start - timedelta(days=1), datetime.min.time()
    )

    sales = (
        db.query(RetailSale)
        .options(
            selectinload(RetailSale.items).selectinload(RetailSaleItem.book),
            selectinload(RetailSale.payments),
        )
        .filter(RetailSale.sale_timestamp >= since_utc)
        .all()
    )

    by_day = {week_start + timedelta(days=n): [0, 0] for n in range(7)}
    today_stats = {
        "sales_count": 0,
        "sales_revenue": 0,
        "items_sold": 0,
        "library_income": 0,
        "loans_out": 0,
        "returns": 0,
    }
    methods: dict[str, int] = defaultdict(int)
    top: dict[int, dict] = {}

    for sale in sales:
        day = to_local(sale.sale_timestamp).date()
        if day < month_start:
            continue
        if day in by_day:
            by_day[day][0] += 1
            by_day[day][1] += sale.total_amount
        if day == today:
            today_stats["sales_count"] += 1
            today_stats["sales_revenue"] += sale.total_amount
            today_stats["items_sold"] += sum(i.quantity for i in sale.items)
        for item in sale.items:
            entry = top.setdefault(
                item.book_id,
                {
                    "book_id": item.book_id,
                    "title": item.book.title if item.book else "(deleted book)",
                    "quantity": 0,
                    "revenue": 0,
                },
            )
            entry["quantity"] += item.quantity
            entry["revenue"] += round(item.price_snapshot * item.quantity)

    payments = db.query(Payment).filter(Payment.paid_at >= since_utc).all()
    for p in payments:
        if p.paid_at is None or to_local(p.paid_at).date() != today:
            continue
        methods[p.payment_method] += round(p.amount)
        if p.rental_id is not None:
            today_stats["library_income"] += round(p.amount)

    open_rentals = (
        db.query(LibraryRental).filter(LibraryRental.actual_return.is_(None)).all()
    )
    overdue = sum(1 for r in open_rentals if r.expected_return < today)
    today_stats["returns"] = (
        db.query(func.count(LibraryRental.rental_id))
        .filter(LibraryRental.actual_return == today)
        .scalar()
    )
    recent_rentals = (
        db.query(LibraryRental).filter(LibraryRental.rental_timestamp >= since_utc).all()
    )
    today_stats["loans_out"] = sum(
        1 for r in recent_rentals if to_local(r.rental_timestamp).date() == today
    )

    low_stock = (
        db.query(Book)
        .filter(Book.retail_stock <= LOW_STOCK_THRESHOLD)
        .order_by(Book.retail_stock.asc(), Book.title.asc())
        .limit(10)
        .all()
    )

    return {
        "today": today_stats,
        "last_7_days": [
            {"date": d, "sales_count": v[0], "revenue": v[1]} for d, v in by_day.items()
        ],
        "payment_methods_today": [
            {"method": m, "amount": a}
            for m, a in sorted(methods.items(), key=lambda kv: -kv[1])
        ],
        "active_loans": len(open_rentals) - overdue,
        "overdue_loans": overdue,
        "low_stock": [
            {
                "book_id": b.book_id,
                "title": b.title,
                "author": b.author,
                "retail_stock": b.retail_stock,
                "library_stock": b.library_stock,
            }
            for b in low_stock
        ],
        "top_books_30_days": sorted(top.values(), key=lambda t: -t["quantity"])[:5],
        "total_titles": db.query(func.count(Book.book_id)).scalar(),
        "total_customers": db.query(func.count(Customer.customer_id)).scalar(),
        "library_members": db.query(func.count(Customer.customer_id))
        .filter(Customer.library_member.is_(True))
        .scalar(),
    }
