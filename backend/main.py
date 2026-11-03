from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from core.config import CORS_ORIGINS
from database import Base, engine
from models import (  # noqa: F401  (imported so every table is registered)
    books,
    categories,
    customers,
    library_rental_items,
    library_rentals,
    payments,
    receipts,
    retail_sale_items,
    retail_sales,
    suppliers,
    users,
)
from routers import (
    books,
    categories,
    customers,
    library_rental_items,
    library_rentals,
    payments,
    pos,
    receipts,
    retail_sale_items,
    retail_sales,
    suppliers,
    users,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Charisma Library POS API",
    version="2",
    description="Book sales and library lending for Charisma Library, Kigali.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    """e.g. deleting a book that still appears on old sales. Return a clear
    409 instead of a 500 traceback."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "This record is still used by other records "
            "(for example sales or loans), so the change was refused."
        },
    )


app.include_router(users.router)
app.include_router(pos.router)
app.include_router(books.router)
app.include_router(categories.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(retail_sales.router)
app.include_router(retail_sale_items.router)
app.include_router(library_rentals.router)
app.include_router(library_rental_items.router)
app.include_router(payments.router)
app.include_router(receipts.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Charisma Library POS API", "docs": "/docs"}
