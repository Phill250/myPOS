"""Workflow endpoints used by the frontend: checkout at the till, lending and
returning library books, transaction history and the dashboard."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_role
from schemas.pos import (
    Dashboard,
    RentalCheckout,
    RentalDetail,
    RentalReturn,
    RentalSummary,
    SaleCheckout,
    SaleDetail,
    SaleSummary,
)
from services import pos as pos_service

router = APIRouter(prefix="/pos", tags=["pos"])

staff_only = require_role("staff", "super_admin")


# ---- sales ----


@router.post("/sales", response_model=SaleDetail, status_code=status.HTTP_201_CREATED)
def checkout_sale(
    data: SaleCheckout,
    db: Session = Depends(get_db),
    cashier=Depends(staff_only),
):
    """Sell books in one step: sale + lines + stock + payment + receipt."""
    return pos_service.checkout_sale(db, data, cashier)


@router.get("/sales", response_model=list[SaleSummary])
def list_sales(
    limit: int = Query(200, ge=1, le=1000),
    customer_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Newest first. Customers only ever see their own purchases."""
    return pos_service.list_sales(db, user, limit, customer_id)


@router.get("/sales/{sale_id}", response_model=SaleDetail)
def get_sale(
    sale_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return pos_service.get_sale_detail(db, sale_id, user)


# ---- library loans ----


@router.post(
    "/rentals", response_model=RentalDetail, status_code=status.HTTP_201_CREATED
)
def checkout_rental(
    data: RentalCheckout,
    db: Session = Depends(get_db),
    staff=Depends(staff_only),
):
    """Lend one or more books to a library member in one step."""
    return pos_service.checkout_rental(db, data, staff)


@router.get("/rentals", response_model=list[RentalSummary])
def list_rentals(
    status_filter: Literal["all", "open", "active", "overdue", "returned"] = Query(
        "all", alias="status"
    ),
    limit: int = Query(300, ge=1, le=1000),
    customer_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return pos_service.list_rentals(db, user, status_filter, limit, customer_id)


@router.get("/rentals/{rental_id}", response_model=RentalDetail)
def get_rental(
    rental_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return pos_service.get_rental_detail(db, rental_id, user)


@router.post("/rentals/{rental_id}/return", response_model=RentalDetail)
def return_rental(
    rental_id: int,
    data: RentalReturn,
    db: Session = Depends(get_db),
    staff=Depends(staff_only),
):
    """Check books back in. Late fee is calculated unless you pass one."""
    return pos_service.return_rental(db, rental_id, data, staff)


# ---- dashboard ----


@router.get("/dashboard", response_model=Dashboard, dependencies=[Depends(staff_only)])
def dashboard(db: Session = Depends(get_db)):
    return pos_service.dashboard(db)
