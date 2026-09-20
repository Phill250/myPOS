def _make_book(client, staff_auth_headers):
    category_id = client.post(
        "/categories/", json={"category_name": "Fiction"}, headers=staff_auth_headers
    ).json()["category_id"]
    supplier_id = client.post(
        "/suppliers/", json={"company_name": "Acme", "phone_number": "0700000000"}, headers=staff_auth_headers
    ).json()["supplier_id"]
    book_id = client.post("/books/", json={
        "title": "Test Book", "author": "Test Author",
        "category_id": category_id, "supplier_id": supplier_id, "sale_price": 9.99,
        "library_stock": 5,
    }, headers=staff_auth_headers).json()["book_id"]
    return book_id


def _make_rental(client, staff_auth_headers, staff_user):
    customer_id = client.post("/customers/", json={
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }, headers=staff_auth_headers).json()["customer_id"]
    rental_id = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": customer_id, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers).json()["rental_id"]
    return rental_id



def test_list_rental_items_success(client, staff_auth_headers):
    response = client.get("/library-rental-items/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_rental_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    rental_id = _make_rental(client, staff_auth_headers, staff_user)

    create_response = client.post(
        "/library-rental-items/",
        json={"rental_id": rental_id, "book_id": book_id},
        headers=staff_auth_headers,
    )
    item_id = create_response.json()["rental_item_id"]

    response = client.get(f"/library-rental-items/{item_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["book_id"] == book_id



def test_create_rental_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    rental_id = _make_rental(client, staff_auth_headers, staff_user)

    response = client.post(
        "/library-rental-items/",
        json={"rental_id": rental_id, "book_id": book_id},
        headers=staff_auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["rental_id"] == rental_id
    assert body["book_id"] == book_id
    assert "rental_item_id" in body



def test_update_rental_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    rental_id = _make_rental(client, staff_auth_headers, staff_user)
    other_book_id = _make_book(client, staff_auth_headers)

    item_id = client.post(
        "/library-rental-items/", json={"rental_id": rental_id, "book_id": book_id}, headers=staff_auth_headers
    ).json()["rental_item_id"]

    response = client.put(
        f"/library-rental-items/{item_id}", json={"book_id": other_book_id}, headers=staff_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["book_id"] == other_book_id



def test_delete_rental_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    rental_id = _make_rental(client, staff_auth_headers, staff_user)

    item_id = client.post(
        "/library-rental-items/", json={"rental_id": rental_id, "book_id": book_id}, headers=staff_auth_headers
    ).json()["rental_item_id"]

    delete_response = client.delete(f"/library-rental-items/{item_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/library-rental-items/{item_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404



def test_create_rental_item_missing_book_id_returns_422(client, staff_auth_headers, staff_user):
    rental_id = _make_rental(client, staff_auth_headers, staff_user)
    response = client.post(
        "/library-rental-items/", json={"rental_id": rental_id}, headers=staff_auth_headers
    )
    assert response.status_code == 422


def test_create_rental_item_invalid_type_returns_422(client, staff_auth_headers):
    response = client.post(
        "/library-rental-items/",
        json={"rental_id": "not-an-int", "book_id": 1},
        headers=staff_auth_headers,
    )
    assert response.status_code == 422


def test_list_rental_items_without_credentials_returns_401(client):
    response = client.get("/library-rental-items/")
    assert response.status_code == 401


def test_create_rental_item_without_credentials_returns_401(client):
    response = client.post("/library-rental-items/", json={"rental_id": 1, "book_id": 1})
    assert response.status_code == 401


def test_delete_rental_item_without_credentials_returns_401(client):
    response = client.delete("/library-rental-items/1")
    assert response.status_code == 401



def test_create_rental_item_as_customer_returns_403(client, auth_headers):
    response = client.post(
        "/library-rental-items/", json={"rental_id": 1, "book_id": 1}, headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_rental_item_as_customer_returns_403(client, auth_headers):
    response = client.delete("/library-rental-items/1", headers=auth_headers)
    assert response.status_code == 403



def test_get_nonexistent_rental_item_returns_404(client, staff_auth_headers):
    response = client.get("/library-rental-items/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_rental_item_returns_404(client, staff_auth_headers):
    response = client.put(
        "/library-rental-items/999999", json={"book_id": 1}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_rental_item_returns_404(client, staff_auth_headers):
    response = client.delete("/library-rental-items/999999", headers=staff_auth_headers)
    assert response.status_code == 404