def test_list_receipts_success(client, staff_auth_headers):
    response = client.get("/receipts/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_receipt_success(client, staff_auth_headers, staff_user):
    sale_id = client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]

    receipt_data = {"receipt_number": "RCPT-001", "sale_id": sale_id}
    create_response = client.post("/receipts/", json=receipt_data, headers=staff_auth_headers)
    receipt_id = create_response.json()["receipt_id"]

    response = client.get(f"/receipts/{receipt_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["receipt_number"] == "RCPT-001"


def test_create_receipt_for_sale_success(client, staff_auth_headers, staff_user):
    sale_id = client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]

    receipt_data = {"receipt_number": "RCPT-002", "sale_id": sale_id}
    response = client.post("/receipts/", json=receipt_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == sale_id
    assert "receipt_id" in body


def test_create_receipt_for_rental_success(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_id = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": customer_id, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers).json()["rental_id"]

    receipt_data = {"receipt_number": "RCPT-003", "rental_id": rental_id}
    response = client.post("/receipts/", json=receipt_data, headers=staff_auth_headers)
    assert response.status_code == 201
    assert response.json()["rental_id"] == rental_id


def test_update_receipt_number_success(client, staff_auth_headers, staff_user):
    sale_id = client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]
    receipt_id = client.post(
        "/receipts/", json={"receipt_number": "RCPT-004", "sale_id": sale_id}, headers=staff_auth_headers
    ).json()["receipt_id"]

    response = client.put(
        f"/receipts/{receipt_id}", json={"receipt_number": "RCPT-004-FIXED"}, headers=staff_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["receipt_number"] == "RCPT-004-FIXED"


def test_update_receipt_ignores_sale_id_reassignment(client, staff_auth_headers, staff_user):
    sale_id = client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]
    receipt_id = client.post(
        "/receipts/", json={"receipt_number": "RCPT-005", "sale_id": sale_id}, headers=staff_auth_headers
    ).json()["receipt_id"]

    response = client.put(
        f"/receipts/{receipt_id}", json={"sale_id": 999999}, headers=staff_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["sale_id"] == sale_id  # unchanged


def test_delete_receipt_success(client, staff_auth_headers, staff_user):
    sale_id = client.post(
        "/sales/", json={"total_amount": 5000, "user_id": staff_user["user_id"]}, headers=staff_auth_headers
    ).json()["sale_id"]
    receipt_id = client.post(
        "/receipts/", json={"receipt_number": "RCPT-006", "sale_id": sale_id}, headers=staff_auth_headers
    ).json()["receipt_id"]

    delete_response = client.delete(f"/receipts/{receipt_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/receipts/{receipt_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_receipt_missing_receipt_number_returns_422(client, staff_auth_headers):
    response = client.post("/receipts/", json={"sale_id": 1}, headers=staff_auth_headers)
    assert response.status_code == 422


def test_list_receipts_without_credentials_returns_401(client):
    response = client.get("/receipts/")
    assert response.status_code == 401


def test_get_receipt_without_credentials_returns_401(client):
    response = client.get("/receipts/1")
    assert response.status_code == 401


def test_create_receipt_without_credentials_returns_401(client):
    response = client.post("/receipts/", json={"receipt_number": "X", "sale_id": 1})
    assert response.status_code == 401


def test_update_receipt_without_credentials_returns_401(client):
    response = client.put("/receipts/1", json={"receipt_number": "X"})
    assert response.status_code == 401


def test_delete_receipt_without_credentials_returns_401(client):
    response = client.delete("/receipts/1")
    assert response.status_code == 401


def test_create_receipt_as_customer_returns_403(client, auth_headers):
    response = client.post(
        "/receipts/", json={"receipt_number": "X", "sale_id": 1}, headers=auth_headers
    )
    assert response.status_code == 403


def test_list_receipts_as_customer_returns_own_only_or_empty(client, auth_headers):
    """Customers can view receipts, but only ones tied to their own transactions."""
    response = client.get("/receipts/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_nonexistent_receipt_returns_404(client, staff_auth_headers):
    response = client.get("/receipts/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_receipt_returns_404(client, staff_auth_headers):
    response = client.put(
        "/receipts/999999", json={"receipt_number": "X"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_receipt_returns_404(client, staff_auth_headers):
    response = client.delete("/receipts/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_customer_sees_only_own_receipt_via_sale(
    client, staff_auth_headers, staff_user, auth_headers, test_user
):
    customer_data = {
        "first_name": "Test", "last_name": "Customer", "phone_number": "0700000000",
        "email": "testuser@example.com", "library_member": False,
        "user_id": test_user["user_id"],
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    own_sale_id = client.post("/sales/", json={
        "total_amount": 3000, "user_id": staff_user["user_id"], "customer_id": customer_id,
    }, headers=staff_auth_headers).json()["sale_id"]
    own_receipt = client.post(
        "/receipts/", json={"receipt_number": "OWN-001", "sale_id": own_sale_id}, headers=staff_auth_headers
    )
    own_receipt_id = own_receipt.json()["receipt_id"]

    other_sale_id = client.post("/sales/", json={
        "total_amount": 9000, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers).json()["sale_id"]
    other_receipt = client.post(
        "/receipts/", json={"receipt_number": "OTHER-001", "sale_id": other_sale_id}, headers=staff_auth_headers
    )
    other_receipt_id = other_receipt.json()["receipt_id"]

    list_response = client.get("/receipts/", headers=auth_headers)
    assert list_response.status_code == 200
    returned_ids = [r["receipt_id"] for r in list_response.json()]
    assert own_receipt_id in returned_ids
    assert other_receipt_id not in returned_ids

    get_own = client.get(f"/receipts/{own_receipt_id}", headers=auth_headers)
    assert get_own.status_code == 200

    get_other = client.get(f"/receipts/{other_receipt_id}", headers=auth_headers)
    assert get_other.status_code == 403