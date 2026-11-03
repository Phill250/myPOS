"""Single sale-line endpoints. For the normal till flow, use
services/checkout.py instead — it creates the sale, its lines, the payment
and the receipt in one transaction."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.books import Book
from models.retail_sale_items import RetailSaleItem
from models.retail_sales import RetailSale
from repositories.retail_sale_items import sale_item_repository
from schemas.retail_sale_items import RetailSaleItemCreate, RetailSaleItemUpdate


def get_sale_item(db: Session, id: int):
    item = sale_item_repository.get(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale item with id {id} not found",
        )
    return item


def list_sale_items(db: Session):
    return sale_item_repository.get_all(db)


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} does not exist",
        )
    return book


def _take_stock(book: Book, quantity: int):
    if book.retail_stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient retail stock. Only {book.retail_stock} copies left.",
        )
    book.retail_stock -= quantity


def create_sale_item(db: Session, data: RetailSaleItemCreate):
    if not db.get(RetailSale, data.sale_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with id {data.sale_id} does not exist",
        )
    book = _get_book_or_404(db, data.book_id)
    _take_stock(book, data.quantity)

    # stock change and new line are committed together
    item = RetailSaleItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_sale_item(db: Session, sale_item_id: int, data: RetailSaleItemUpdate):
    item = get_sale_item(db, sale_item_id)
    values = data.model_dump(exclude_unset=True)

    new_book_id = values.get("book_id", item.book_id)
    new_quantity = values.get("quantity", item.quantity)

    if new_book_id != item.book_id or new_quantity != item.quantity:
        # give the old copies back, then take the new ones
        old_book = db.get(Book, item.book_id)
        if old_book:
            old_book.retail_stock += item.quantity
        new_book = _get_book_or_404(db, new_book_id)
        try:
            _take_stock(new_book, new_quantity)
        except HTTPException:
            db.rollback()
            raise

    return sale_item_repository.update(db, item, values)


def delete_sale_item(db: Session, sale_item_id: int):
    item = get_sale_item(db, sale_item_id)
    if item.book:
        item.book.retail_stock += item.quantity  # copies go back on the shelf
    return sale_item_repository.delete(db, item)
