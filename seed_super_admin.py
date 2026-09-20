from models import receipts, suppliers, payments, library_rental_items, library_rentals, categories, books, customers, users, retail_sales, retail_sale_items
from database import Session
from services import auth_services
from schemas.users import UserCreateByAdmin

def main():
    db = Session()
    try:
        username = input("Super admin username: ").strip()
        password = input("Super admin password: ").strip()

        data = UserCreateByAdmin(
            username=username,
            password=password,
            role="super_admin",
            is_active=True,
        )
        user = auth_services.create_user_as_admin(db, data)
        print(f"Created super_admin '{user.username}' (user_id={user.user_id})")
    finally:
        db.close()

if __name__ == "__main__":
    main()