"""Schemas for the till / library-desk workflow (/pos/*).

The CRUD schemas mirror single tables. These ones describe whole
transactions: a sale with its lines, payment and receipt, or a loan with its
books — which is what the frontend actually works with.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

PaymentMethod = Literal["cash", "mtn_momo", "airtel_money", "card", "bank_transfer"]


# ---------- requests ----------


class SaleLineIn(BaseModel):
    book_id: int
    quantity: int = Field(gt=0)


class SaleCheckout(BaseModel):
    customer_id: int | None = None  # None = walk-in
    items: list[SaleLineIn] = Field(min_length=1)
    payment_method: PaymentMethod = "cash"


class RentalCheckout(BaseModel):
    customer_id: int
    book_ids: list[int] = Field(min_length=1)
    expected_return: date
    fee: int = Field(default=0, ge=0)  # optional borrowing fee in RWF
    payment_method: PaymentMethod = "cash"


class RentalReturn(BaseModel):
    returned_on: date | None = None  # defaults to today
    late_fee: int | None = Field(default=None, ge=0)  # None = calculate it
    payment_method: PaymentMethod = "cash"


# ---------- responses ----------


class PaymentOut(BaseModel):
    payment_id: int
    amount: float
    payment_method: str
    transaction_type: str
    paid_at: datetime | None = None


class SaleLineOut(BaseModel):
    sale_item_id: int
    book_id: int
    title: str
    author: str
    quantity: int
    unit_price: float
    line_total: int


class SaleSummary(BaseModel):
    sale_id: int
    sale_timestamp: datetime
    total_amount: int
    customer_id: int | None
    customer_name: str | None
    cashier: str | None
    item_count: int
    payment_method: str | None
    receipt_number: str | None


class SaleDetail(SaleSummary):
    items: list[SaleLineOut]
    payments: list[PaymentOut]


class RentalBookOut(BaseModel):
    rental_item_id: int
    book_id: int
    title: str
    author: str


class RentalSummary(BaseModel):
    rental_id: int
    rental_timestamp: datetime
    expected_return: date
    actual_return: date | None
    status: Literal["active", "overdue", "returned"]
    days_overdue: int
    customer_id: int
    customer_name: str | None
    customer_phone: str | None
    staff: str | None
    books: list[RentalBookOut]
    receipt_number: str | None


class RentalDetail(RentalSummary):
    payments: list[PaymentOut]
    late_fee_per_day: int
    suggested_late_fee: int


class DayRevenue(BaseModel):
    date: date
    sales_count: int
    revenue: int


class MethodTotal(BaseModel):
    method: str
    amount: int


class LowStockBook(BaseModel):
    book_id: int
    title: str
    author: str
    retail_stock: int
    library_stock: int


class TopBook(BaseModel):
    book_id: int
    title: str
    quantity: int
    revenue: int


class TodayStats(BaseModel):
    sales_count: int
    sales_revenue: int
    items_sold: int
    library_income: int
    loans_out: int
    returns: int


class Dashboard(BaseModel):
    today: TodayStats
    last_7_days: list[DayRevenue]
    payment_methods_today: list[MethodTotal]
    active_loans: int
    overdue_loans: int
    low_stock: list[LowStockBook]
    top_books_30_days: list[TopBook]
    total_titles: int
    total_customers: int
    library_members: int
