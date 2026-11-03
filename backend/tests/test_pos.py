"""Tests for the /pos workflow endpoints and the backend bug fixes."""

from datetime import timedelta

from services.pos import today_local


# ---------- helpers ----------


def _setup_catalog(client, headers, retail_stock=5, library_stock=2, price=4500):
    category_id = client.post(
        "/categories/", json={"category_name": "Fiction"}, headers=headers
    ).json()["category_id"]
    supplier_id = client.post(
        "/suppliers/",
        json={"company_name": "Kigali Books Ltd", "phone_number": "0788000000"},
        headers=headers,
    ).json()["supplier_id"]

    def make_book(title, **overrides):
        body = {
            "title": title,
            "author": "Some Author",
            "sale_price": price,
            "category_id": category_id,
            "supplier_id": supplier_id,
            "retail_stock": retail_stock,
            "library_stock": library_stock,
        }
        body.update(overrides)
        return client.post("/books/", json=body, headers=headers).json()["book_id"]

    return make_book


def _make_customer(client, headers, member=True, user_id=None):
    body = {
        "first_name": "Aline",
        "last_name": "Uwase",
        "phone_number": "0788123456",
        "email": None,
        "library_member": member,
    }
    if user_id is not None:
        body["user_id"] = user_id
    return client.post("/customers/", json=body, headers=headers).json()["customer_id"]


def _book(client, headers, book_id):
    return client.get(f"/books/{book_id}", headers=headers).json()


# ---------- sale checkout ----------


def test_checkout_sale_creates_everything_in_one_go(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Book A")
    b = make_book("Book B", sale_price=2000)

    response = client.post(
        "/pos/sales",
        json={
            "items": [{"book_id": a, "quantity": 2}, {"book_id": b, "quantity": 1}],
            "payment_method": "mtn_momo",
        },
        headers=staff_auth_headers,
    )
    assert response.status_code == 201, response.text
    sale = response.json()
    assert sale["total_amount"] == 2 * 4500 + 2000
    assert sale["item_count"] == 3
    assert sale["cashier"] == "teststaff"
    assert sale["payment_method"] == "mtn_momo"
    assert sale["receipt_number"].startswith("CL-S-")
    assert len(sale["payments"]) == 1
    assert sale["payments"][0]["amount"] == sale["total_amount"]

    assert _book(client, staff_auth_headers, a)["retail_stock"] == 3
    assert _book(client, staff_auth_headers, b)["retail_stock"] == 4


def test_checkout_sale_merges_duplicate_lines(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Book A")
    response = client.post(
        "/pos/sales",
        json={"items": [{"book_id": a, "quantity": 1}, {"book_id": a, "quantity": 2}]},
        headers=staff_auth_headers,
    )
    assert response.status_code == 201
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["quantity"] == 3


def test_checkout_sale_is_all_or_nothing(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    plenty = make_book("Plenty", retail_stock=10)
    scarce = make_book("Scarce", retail_stock=1)

    response = client.post(
        "/pos/sales",
        json={
            "items": [
                {"book_id": plenty, "quantity": 3},
                {"book_id": scarce, "quantity": 2},
            ]
        },
        headers=staff_auth_headers,
    )
    assert response.status_code == 400
    assert "Scarce" in response.json()["detail"]
    # the first line must NOT have consumed stock
    assert _book(client, staff_auth_headers, plenty)["retail_stock"] == 10
    assert client.get("/pos/sales", headers=staff_auth_headers).json() == []


def test_checkout_sale_validation(client, staff_auth_headers):
    assert (
        client.post("/pos/sales", json={"items": []}, headers=staff_auth_headers).status_code
        == 422
    )
    assert (
        client.post(
            "/pos/sales",
            json={"items": [{"book_id": 1, "quantity": 0}]},
            headers=staff_auth_headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/pos/sales",
            json={"items": [{"book_id": 999, "quantity": 1}]},
            headers=staff_auth_headers,
        ).status_code
        == 404
    )


def test_customer_cannot_checkout(client, auth_headers):
    response = client.post(
        "/pos/sales", json={"items": [{"book_id": 1, "quantity": 1}]}, headers=auth_headers
    )
    assert response.status_code == 403


def test_customer_sees_only_own_sales(client, staff_auth_headers, auth_headers, test_user):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Book A")
    mine = _make_customer(client, staff_auth_headers, user_id=test_user["user_id"])
    other = _make_customer(client, staff_auth_headers)

    own_sale = client.post(
        "/pos/sales",
        json={"customer_id": mine, "items": [{"book_id": a, "quantity": 1}]},
        headers=staff_auth_headers,
    ).json()
    other_sale = client.post(
        "/pos/sales",
        json={"customer_id": other, "items": [{"book_id": a, "quantity": 1}]},
        headers=staff_auth_headers,
    ).json()

    listed = client.get("/pos/sales", headers=auth_headers).json()
    assert [s["sale_id"] for s in listed] == [own_sale["sale_id"]]
    assert client.get(f"/pos/sales/{own_sale['sale_id']}", headers=auth_headers).status_code == 200
    assert (
        client.get(f"/pos/sales/{other_sale['sale_id']}", headers=auth_headers).status_code
        == 403
    )


def test_voiding_sale_restores_stock(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Book A")
    sale = client.post(
        "/pos/sales",
        json={"items": [{"book_id": a, "quantity": 2}]},
        headers=staff_auth_headers,
    ).json()
    assert _book(client, staff_auth_headers, a)["retail_stock"] == 3
    assert client.delete(f"/sales/{sale['sale_id']}", headers=staff_auth_headers).status_code == 204
    assert _book(client, staff_auth_headers, a)["retail_stock"] == 5


# ---------- library loans ----------


def test_rental_checkout_and_return_with_late_fee(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers, library_stock=2)
    a = make_book("Loan A")
    b = make_book("Loan B")
    member = _make_customer(client, staff_auth_headers, member=True)
    today = today_local()

    response = client.post(
        "/pos/rentals",
        json={
            "customer_id": member,
            "book_ids": [a, b],
            "expected_return": str(today),
            "fee": 500,
        },
        headers=staff_auth_headers,
    )
    assert response.status_code == 201, response.text
    rental = response.json()
    assert rental["status"] == "active"
    assert len(rental["books"]) == 2
    assert rental["receipt_number"].startswith("CL-L-")
    assert rental["payments"][0]["transaction_type"] == "rental_fee"
    assert _book(client, staff_auth_headers, a)["library_stock"] == 1

    returned = client.post(
        f"/pos/rentals/{rental['rental_id']}/return",
        json={"returned_on": str(today + timedelta(days=3))},
        headers=staff_auth_headers,
    )
    assert returned.status_code == 200, returned.text
    body = returned.json()
    assert body["status"] == "returned"
    assert body["days_overdue"] == 3
    late = [p for p in body["payments"] if p["transaction_type"] == "late_fee"]
    assert late and late[0]["amount"] == 3 * 200
    assert _book(client, staff_auth_headers, a)["library_stock"] == 2

    again = client.post(
        f"/pos/rentals/{rental['rental_id']}/return", json={}, headers=staff_auth_headers
    )
    assert again.status_code == 400


def test_rental_requires_membership_and_stock(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers, library_stock=0)
    a = make_book("No copies")
    walk_in = _make_customer(client, staff_auth_headers, member=False)
    member = _make_customer(client, staff_auth_headers, member=True)
    due = str(today_local() + timedelta(days=14))

    r1 = client.post(
        "/pos/rentals",
        json={"customer_id": walk_in, "book_ids": [a], "expected_return": due},
        headers=staff_auth_headers,
    )
    assert r1.status_code == 400 and "member" in r1.json()["detail"]

    r2 = client.post(
        "/pos/rentals",
        json={"customer_id": member, "book_ids": [a], "expected_return": due},
        headers=staff_auth_headers,
    )
    assert r2.status_code == 400 and "copies" in r2.json()["detail"]


def test_rental_past_due_date_rejected(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Loan A")
    member = _make_customer(client, staff_auth_headers)
    response = client.post(
        "/pos/rentals",
        json={
            "customer_id": member,
            "book_ids": [a],
            "expected_return": str(today_local() - timedelta(days=1)),
        },
        headers=staff_auth_headers,
    )
    assert response.status_code == 400


def test_rental_status_filters(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Loan A")
    member = _make_customer(client, staff_auth_headers)
    client.post(
        "/pos/rentals",
        json={
            "customer_id": member,
            "book_ids": [a],
            "expected_return": str(today_local() + timedelta(days=7)),
        },
        headers=staff_auth_headers,
    )
    assert len(client.get("/pos/rentals?status=open", headers=staff_auth_headers).json()) == 1
    assert len(client.get("/pos/rentals?status=active", headers=staff_auth_headers).json()) == 1
    assert client.get("/pos/rentals?status=overdue", headers=staff_auth_headers).json() == []
    assert client.get("/pos/rentals?status=returned", headers=staff_auth_headers).json() == []


def test_deleting_open_rental_restores_stock(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers, library_stock=1)
    a = make_book("Loan A")
    member = _make_customer(client, staff_auth_headers)
    rental = client.post(
        "/pos/rentals",
        json={
            "customer_id": member,
            "book_ids": [a],
            "expected_return": str(today_local() + timedelta(days=7)),
        },
        headers=staff_auth_headers,
    ).json()
    assert _book(client, staff_auth_headers, a)["library_stock"] == 0
    client.delete(f"/library-rentals/{rental['rental_id']}", headers=staff_auth_headers)
    assert _book(client, staff_auth_headers, a)["library_stock"] == 1


# ---------- dashboard ----------


def test_dashboard_numbers(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers, retail_stock=4)
    a = make_book("Bestseller")
    client.post(
        "/pos/sales",
        json={"items": [{"book_id": a, "quantity": 2}], "payment_method": "cash"},
        headers=staff_auth_headers,
    )
    response = client.get("/pos/dashboard", headers=staff_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["today"]["sales_count"] == 1
    assert data["today"]["sales_revenue"] == 9000
    assert data["today"]["items_sold"] == 2
    assert data["last_7_days"][-1]["revenue"] == 9000
    assert data["payment_methods_today"] == [{"method": "cash", "amount": 9000}]
    assert data["top_books_30_days"][0]["title"] == "Bestseller"
    assert data["low_stock"][0]["retail_stock"] == 2  # 4 - 2 <= threshold 3


def test_dashboard_is_staff_only(client, auth_headers):
    assert client.get("/pos/dashboard", headers=auth_headers).status_code == 403


# ---------- user/auth fixes ----------


def test_me_returns_user_and_profile(client, staff_auth_headers, auth_headers, test_user):
    me = client.get("/users/me", headers=auth_headers).json()
    assert me["username"] == test_user["username"]
    assert me["customer_profile"] is None

    _make_customer(client, staff_auth_headers, user_id=test_user["user_id"])
    me = client.get("/users/me", headers=auth_headers).json()
    assert me["customer_profile"]["first_name"] == "Aline"


def test_admin_password_change_actually_works(client, admin_auth_headers, test_user):
    response = client.put(
        f"/users/{test_user['user_id']}",
        json={"password": "brand-new-pass"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    old = client.post(
        "/users/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    new = client.post(
        "/users/login",
        data={"username": test_user["username"], "password": "brand-new-pass"},
    )
    assert old.status_code == 401
    assert new.status_code == 200


def test_deactivated_user_cannot_log_in_or_use_token(
    client, admin_auth_headers, auth_headers, test_user
):
    client.put(
        f"/users/{test_user['user_id']}",
        json={"is_active": False},
        headers=admin_auth_headers,
    )
    login = client.post(
        "/users/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert login.status_code == 403
    assert client.get("/users/me", headers=auth_headers).status_code == 401


def test_invalid_role_rejected(client, admin_auth_headers):
    response = client.post(
        "/users/",
        json={"username": "x", "password": "y", "role": "boss", "is_active": True},
        headers=admin_auth_headers,
    )
    assert response.status_code == 422


def test_customer_cannot_look_up_other_users(client, auth_headers, staff_user, test_user):
    assert client.get(f"/users/{staff_user['user_id']}", headers=auth_headers).status_code == 403
    assert client.get(f"/users/{test_user['user_id']}", headers=auth_headers).status_code == 200


def test_admin_cannot_delete_self(client, admin_auth_headers, admin_user):
    response = client.delete(f"/users/{admin_user['user_id']}", headers=admin_auth_headers)
    assert response.status_code == 400


def test_negative_stock_rejected(client, staff_auth_headers):
    make_book = _setup_catalog(client, staff_auth_headers)
    a = make_book("Book A")
    response = client.put(
        f"/books/{a}", json={"retail_stock": -1}, headers=staff_auth_headers
    )
    assert response.status_code == 422


def test_staff_can_look_up_username(client, staff_auth_headers, auth_headers, test_user):
    ok = client.get(f"/users/lookup?username={test_user['username']}", headers=staff_auth_headers)
    assert ok.status_code == 200 and ok.json()["user_id"] == test_user["user_id"]
    assert client.get("/users/lookup?username=nobody", headers=staff_auth_headers).status_code == 404
    assert client.get("/users/lookup?username=x", headers=auth_headers).status_code == 403
