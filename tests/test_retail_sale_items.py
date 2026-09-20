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
        "retail_stock": 10,
    }, headers=staff_auth_headers).json()["book_id"]
    return book_id


def _make_sale(client, staff_auth_headers, staff_user):
    return client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]


def test_list_sale_items_success(client, staff_auth_headers):
    response = client.get("/sale-items/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sale_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    create_response = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "quantity": 2, "price_snapshot": 9.99,
    }, headers=staff_auth_headers)
    item_id = create_response.json()["sale_item_id"]

    response = client.get(f"/sale-items/{item_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["quantity"] == 2


def test_create_sale_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    response = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "quantity": 2, "price_snapshot": 9.99,
    }, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == sale_id
    assert body["quantity"] == 2
    assert "sale_item_id" in body


def test_update_sale_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    item_id = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "quantity": 1, "price_snapshot": 9.99,
    }, headers=staff_auth_headers).json()["sale_item_id"]

    response = client.put(
        f"/sale-items/{item_id}", json={"quantity": 3}, headers=staff_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 3


def test_delete_sale_item_success(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    item_id = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "quantity": 1, "price_snapshot": 9.99,
    }, headers=staff_auth_headers).json()["sale_item_id"]

    delete_response = client.delete(f"/sale-items/{item_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/sale-items/{item_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_sale_item_missing_quantity_returns_422(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    response = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "price_snapshot": 9.99,
    }, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_sale_item_invalid_quantity_type_returns_422(client, staff_auth_headers, staff_user):
    book_id = _make_book(client, staff_auth_headers)
    sale_id = _make_sale(client, staff_auth_headers, staff_user)

    response = client.post("/sale-items/", json={
        "sale_id": sale_id, "book_id": book_id, "quantity": "two", "price_snapshot": 9.99,
    }, headers=staff_auth_headers)
    assert response.status_code == 422


def test_list_sale_items_without_credentials_returns_401(client):
    response = client.get("/sale-items/")
    assert response.status_code == 401


def test_create_sale_item_without_credentials_returns_401(client):
    response = client.post("/sale-items/", json={
        "sale_id": 1, "book_id": 1, "quantity": 1, "price_snapshot": 9.99,
    })
    assert response.status_code == 401


def test_delete_sale_item_without_credentials_returns_401(client):
    response = client.delete("/sale-items/1")
    assert response.status_code == 401


def test_create_sale_item_as_customer_returns_403(client, auth_headers):
    response = client.post("/sale-items/", json={
        "sale_id": 1, "book_id": 1, "quantity": 1, "price_snapshot": 9.99,
    }, headers=auth_headers)
    assert response.status_code == 403


def test_delete_sale_item_as_customer_returns_403(client, auth_headers):
    response = client.delete("/sale-items/1", headers=auth_headers)
    assert response.status_code == 403


def test_get_nonexistent_sale_item_returns_404(client, staff_auth_headers):
    response = client.get("/sale-items/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_sale_item_returns_404(client, staff_auth_headers):
    response = client.put(
        "/sale-items/999999", json={"quantity": 5}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_sale_item_returns_404(client, staff_auth_headers):
    response = client.delete("/sale-items/999999", headers=staff_auth_headers)
    assert response.status_code == 404