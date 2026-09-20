from fastapi import FastAPI

from models import receipts, suppliers, payments, library_rental_items, library_rentals, categories, books, customers, users, retail_sales, retail_sale_items
from routers import receipts, suppliers, payments, library_rental_items, library_rentals, books, categories, customers, users, retail_sale_items, retail_sales

from database import engine, Base
#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind = engine)

app = FastAPI(title = "POS API", version = "1")

app.include_router(books.router)
app.include_router(categories.router)
app.include_router(customers.router)
app.include_router(users.router)
app.include_router(retail_sale_items.router)
app.include_router(retail_sales.router)
app.include_router(library_rentals.router)
app.include_router(library_rental_items.router)
app.include_router(payments.router)
app.include_router(suppliers.router)
app.include_router(receipts.router)


@app.get("/")
def root():
    return {"message": "Welcome to the POS API"}