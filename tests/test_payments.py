def _make_sale(client, staff_auth_headers, staff_user):
    return client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]


def test_list_payments_success(client, staff_auth_headers):
    response = client.get("/payments/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_payment_success(client, staff_auth_headers, staff_user):
    sale_id = _make_sale(client, staff_auth_headers, staff_user)
    create_response = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale", "sale_id": sale_id,
    }, headers=staff_auth_headers)
    payment_id = create_response.json()["payment_id"]

    response = client.get(f"/payments/{payment_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == 5000


def test_create_payment_for_sale_success(client, staff_auth_headers, staff_user):
    sale_id = _make_sale(client, staff_auth_headers, staff_user)
    response = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale", "sale_id": sale_id,
    }, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == sale_id
    assert "payment_id" in body


def test_create_payment_for_rental_success(client, staff_auth_headers, staff_user):
    customer_id = client.post("/customers/", json={
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }, headers=staff_auth_headers).json()["customer_id"]
    rental_id = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": customer_id, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers).json()["rental_id"]

    response = client.post("/payments/", json={
        "amount": 1000, "payment_method": "mobile_money", "transaction_type": "rental_fee", "rental_id": rental_id,
    }, headers=staff_auth_headers)
    assert response.status_code == 201
    assert response.json()["rental_id"] == rental_id


def test_update_payment_success(client, staff_auth_headers, staff_user):
    sale_id = _make_sale(client, staff_auth_headers, staff_user)
    payment_id = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale", "sale_id": sale_id,
    }, headers=staff_auth_headers).json()["payment_id"]

    response = client.put(
        f"/payments/{payment_id}", json={"payment_method": "card"}, headers=staff_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["payment_method"] == "card"


def test_delete_payment_success(client, staff_auth_headers, staff_user):
    sale_id = _make_sale(client, staff_auth_headers, staff_user)
    payment_id = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale", "sale_id": sale_id,
    }, headers=staff_auth_headers).json()["payment_id"]

    delete_response = client.delete(f"/payments/{payment_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/payments/{payment_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_payment_missing_amount_returns_422(client, staff_auth_headers):
    response = client.post("/payments/", json={
        "payment_method": "cash", "transaction_type": "sale",
    }, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_payment_invalid_amount_type_returns_422(client, staff_auth_headers):
    response = client.post("/payments/", json={
        "amount": "a lot", "payment_method": "cash", "transaction_type": "sale",
    }, headers=staff_auth_headers)
    assert response.status_code == 422


def test_list_payments_without_credentials_returns_401(client):
    response = client.get("/payments/")
    assert response.status_code == 401


def test_get_payment_without_credentials_returns_401(client):
    response = client.get("/payments/1")
    assert response.status_code == 401


def test_create_payment_without_credentials_returns_401(client):
    response = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale",
    })
    assert response.status_code == 401


def test_update_payment_without_credentials_returns_401(client):
    response = client.put("/payments/1", json={"payment_method": "card"})
    assert response.status_code == 401


def test_delete_payment_without_credentials_returns_401(client):
    response = client.delete("/payments/1")
    assert response.status_code == 401


def test_list_payments_as_customer_returns_403(client, auth_headers):
    response = client.get("/payments/", headers=auth_headers)
    assert response.status_code == 403


def test_get_payment_as_customer_returns_403(client, auth_headers):
    response = client.get("/payments/1", headers=auth_headers)
    assert response.status_code == 403


def test_create_payment_as_customer_returns_403(client, auth_headers):
    response = client.post("/payments/", json={
        "amount": 5000, "payment_method": "cash", "transaction_type": "sale",
    }, headers=auth_headers)
    assert response.status_code == 403


def test_delete_payment_as_customer_returns_403(client, auth_headers):
    response = client.delete("/payments/1", headers=auth_headers)
    assert response.status_code == 403


def test_get_nonexistent_payment_returns_404(client, staff_auth_headers):
    response = client.get("/payments/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_payment_returns_404(client, staff_auth_headers):
    response = client.put(
        "/payments/999999", json={"payment_method": "card"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_payment_returns_404(client, staff_auth_headers):
    response = client.delete("/payments/999999", headers=staff_auth_headers)
    assert response.status_code == 404