"""Fill an empty database with realistic sample data so the frontend has
something to show.

    python seed_demo_data.py

Creates (only if they don't exist yet):
  - users:    admin / admin123 (super_admin), cashier / cashier123 (staff),
              aline / aline123 (customer, linked to a customer profile)
  - categories, suppliers, ~16 books, a few customers
  - a handful of sales over the last week and some library loans

Safe to run twice — it skips anything already there. Do NOT run against the
real shop database once it is live; it is for development and demos.
"""

import random
from datetime import timedelta

from database import Base, Session, engine
from models.books import Book
from models.categories import Category
from models.customers import Customer
from models.suppliers import Supplier
from models.users import User
from schemas.pos import RentalCheckout, SaleCheckout, SaleLineIn
from schemas.users import UserCreateByAdmin
from services import auth_services, pos

import main  # noqa: F401  (registers every model on Base)

CATEGORIES = [
    ("Fiction", "Novels and short stories"),
    ("Christian Living", "Faith, devotionals and Bible study"),
    ("Children", "Picture books and early readers"),
    ("Business", "Entrepreneurship, leadership and money"),
    ("African Literature", "Writers from across the continent"),
    ("Education", "Textbooks and revision guides"),
]

SUPPLIERS = [
    ("Kigali Book Distributors", "0788 300 100"),
    ("East African Publishers", "0722 410 220"),
    ("Imprimerie Nouvelle", "0788 512 990"),
]

# title, author, price (RWF), category index, supplier index, retail, library
BOOKS = [
    ("Things Fall Apart", "Chinua Achebe", 9500, 4, 1, 8, 3),
    ("Half of a Yellow Sun", "Chimamanda Ngozi Adichie", 14000, 4, 1, 5, 2),
    ("Our Lady of the Nile", "Scholastique Mukasonga", 12500, 4, 0, 4, 2),
    ("Petals of Blood", "Ngũgĩ wa Thiong'o", 11000, 4, 1, 2, 1),
    ("Purpose Driven Life", "Rick Warren", 13500, 1, 0, 12, 4),
    ("Mere Christianity", "C. S. Lewis", 10500, 1, 0, 6, 2),
    ("Jesus Calling", "Sarah Young", 16000, 1, 2, 3, 1),
    ("The Very Hungry Caterpillar", "Eric Carle", 7000, 2, 2, 10, 2),
    ("Anansi Stories", "Traditional", 5500, 2, 2, 1, 3),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", 12000, 3, 0, 9, 2),
    ("The Lean Startup", "Eric Ries", 15500, 3, 1, 2, 1),
    ("Atomic Habits", "James Clear", 17000, 3, 0, 7, 3),
    ("Animal Farm", "George Orwell", 6500, 0, 1, 11, 3),
    ("The Alchemist", "Paulo Coelho", 9000, 0, 0, 6, 2),
    ("Primary Mathematics P6", "REB", 4500, 5, 2, 25, 5),
    ("English Grammar in Use", "Raymond Murphy", 21000, 5, 1, 0, 2),
]

CUSTOMERS = [
    ("Aline", "Uwase", "0788 111 222", "aline@example.com", True),
    ("Eric", "Habimana", "0788 333 444", None, True),
    ("Grace", "Mukamana", "0722 555 666", "grace@example.com", False),
    ("Jean Paul", "Niyonzima", "0788 777 888", None, True),
    ("Diane", "Ingabire", "0733 999 000", "diane@example.com", False),
]


def ensure_user(db, username, password, role):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    return auth_services.create_user_as_admin(
        db,
        UserCreateByAdmin(username=username, password=password, role=role, is_active=True),
    )


def main_seed():
    Base.metadata.create_all(bind=engine)
    db = Session()
    random.seed(7)
    try:
        ensure_user(db, "admin", "admin123", "super_admin")
        cashier = ensure_user(db, "cashier", "cashier123", "staff")
        aline_user = ensure_user(db, "aline", "aline123", "customer")

        if db.query(Book).count() > 0:
            print("Books already exist — skipping catalog, sales and loans.")
            return

        cats = [Category(category_name=n, description=d) for n, d in CATEGORIES]
        sups = [Supplier(company_name=n, phone_number=p) for n, p in SUPPLIERS]
        db.add_all(cats + sups)
        db.flush()

        books = []
        for title, author, price, ci, si, retail, library in BOOKS:
            books.append(
                Book(
                    title=title,
                    author=author,
                    sale_price=price,
                    category_id=cats[ci].category_id,
                    supplier_id=sups[si].supplier_id,
                    retail_stock=retail,
                    library_stock=library,
                )
            )
        db.add_all(books)

        customers = [
            Customer(
                first_name=f,
                last_name=l,
                phone_number=p,
                email=e,
                library_member=m,
            )
            for f, l, p, e, m in CUSTOMERS
        ]
        customers[0].user_id = aline_user.user_id
        db.add_all(customers)
        db.commit()

        # a week of sales
        sellable = [b for b in books if b.retail_stock > 3]
        for _ in range(14):
            picks = random.sample(sellable, k=random.randint(1, 3))
            sale = pos.checkout_sale(
                db,
                SaleCheckout(
                    customer_id=random.choice([None, None] + [c.customer_id for c in customers]),
                    items=[SaleLineIn(book_id=b.book_id, quantity=1) for b in picks],
                    payment_method=random.choice(["cash", "cash", "mtn_momo", "airtel_money", "card"]),
                ),
                cashier,
            )
            # spread them over the past week
            from models.retail_sales import RetailSale

            row = db.get(RetailSale, sale["sale_id"])
            row.sale_timestamp = row.sale_timestamp - timedelta(
                days=random.randint(0, 6), hours=random.randint(0, 6)
            )
            for p in row.payments:
                p.paid_at = row.sale_timestamp
            db.commit()

        # library loans: one overdue, two active
        members = [c for c in customers if c.library_member]
        today = pos.today_local()
        loans = [
            (members[0], [books[0], books[12]], 14),
            (members[1], [books[4]], 7),
            (members[2], [books[8]], 1),
        ]
        for member, loan_books, days in loans:
            pos.checkout_rental(
                db,
                RentalCheckout(
                    customer_id=member.customer_id,
                    book_ids=[b.book_id for b in loan_books],
                    expected_return=today + timedelta(days=days),
                    fee=500,
                ),
                cashier,
            )

        # make the last loan overdue by moving its dates back
        from models.library_rentals import LibraryRental

        late = db.query(LibraryRental).order_by(LibraryRental.rental_id.desc()).first()
        late.expected_return = today - timedelta(days=4)
        late.rental_timestamp = late.rental_timestamp - timedelta(days=18)
        db.commit()

        print("Demo data created.")
        print("  admin / admin123      (super admin)")
        print("  cashier / cashier123  (staff)")
        print("  aline / aline123      (customer)")
    finally:
        db.close()


if __name__ == "__main__":
    main_seed()
