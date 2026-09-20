def test_list_sales_success(client, staff_auth_headers):
    response = client.get("/sales/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sale_success(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    create_response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    sale_id = create_response.json()["sale_id"]

    response = client.get(f"/sales/{sale_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["total_amount"] == 5000


def test_create_sale_success(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["total_amount"] == 5000
    assert "sale_id" in body


def test_update_sale_success(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    create_response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    sale_id = create_response.json()["sale_id"]

    response = client.put(f"/sales/{sale_id}", json={"total_amount": 7500}, headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["total_amount"] == 7500


def test_update_sale_ignores_customer_id_reassignment(client, staff_auth_headers, staff_user):
    """RetailSaleUpdate deliberately excludes customer_id/user_id — sending them
    should be silently ignored rather than changing who the sale belongs to."""
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    create_response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    sale_id = create_response.json()["sale_id"]

    response = client.put(
        f"/sales/{sale_id}",
        json={"total_amount": 6000, "customer_id": 999, "user_id": 999},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_amount"] == 6000
    assert body["customer_id"] != 999
    assert body["user_id"] != 999


def test_delete_sale_success(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    create_response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    sale_id = create_response.json()["sale_id"]

    delete_response = client.delete(f"/sales/{sale_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/sales/{sale_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_sale_missing_user_id_returns_422(client, staff_auth_headers):
    response = client.post("/sales/", json={"total_amount": 5000}, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_sale_invalid_amount_type_returns_422(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": "not-a-number", "user_id": staff_user["user_id"]}
    response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_sale_nonexistent_user_id_returns_400(client, staff_auth_headers):
    """user_id must reference a real staff member — service-level check,
    not a schema validation error, so this is 400 rather than 422."""
    sale_data = {"total_amount": 5000, "user_id": 999999}
    response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    assert response.status_code == 400


def test_update_sale_invalid_amount_type_returns_422(client, staff_auth_headers, staff_user):
    sale_data = {"total_amount": 5000, "user_id": staff_user["user_id"]}
    create_response = client.post("/sales/", json=sale_data, headers=staff_auth_headers)
    sale_id = create_response.json()["sale_id"]

    response = client.put(
        f"/sales/{sale_id}", json={"total_amount": "bad"}, headers=staff_auth_headers
    )
    assert response.status_code == 422


def test_list_sales_without_credentials_returns_401(client):
    response = client.get("/sales/")
    assert response.status_code == 401


def test_get_sale_without_credentials_returns_401(client):
    response = client.get("/sales/1")
    assert response.status_code == 401


def test_create_sale_without_credentials_returns_401(client):
    response = client.post("/sales/", json={"total_amount": 5000, "user_id": 1})
    assert response.status_code == 401


def test_update_sale_without_credentials_returns_401(client):
    response = client.put("/sales/1", json={"total_amount": 5000})
    assert response.status_code == 401


def test_delete_sale_without_credentials_returns_401(client):
    response = client.delete("/sales/1")
    assert response.status_code == 401


def test_create_sale_as_customer_returns_403(client, auth_headers):
    response = client.post("/sales/", json={"total_amount": 5000, "user_id": 1}, headers=auth_headers)
    assert response.status_code == 403


def test_delete_sale_as_customer_returns_403(client, auth_headers):
    response = client.delete("/sales/1", headers=auth_headers)
    assert response.status_code == 403


def test_get_nonexistent_sale_returns_404(client, staff_auth_headers):
    response = client.get("/sales/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_sale_returns_404(client, staff_auth_headers):
    response = client.put(
        "/sales/999999", json={"total_amount": 1000}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_sale_returns_404(client, staff_auth_headers):
    response = client.delete("/sales/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_customer_sees_only_own_sales(client, staff_auth_headers, staff_user, auth_headers, test_user):
    customer_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "phone_number": "0700000000",
        "email": "testuser@example.com",
        "library_member": False,
        "user_id": test_user["user_id"],
    }
    customer_response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    assert customer_response.status_code == 201
    customer_id = customer_response.json()["customer_id"]

    own_sale = client.post(
        "/sales/",
        json={"total_amount": 3000, "user_id": staff_user["user_id"], "customer_id": customer_id},
        headers=staff_auth_headers,
    )
    own_sale_id = own_sale.json()["sale_id"]

    other_sale = client.post(
        "/sales/",
        json={"total_amount": 9000, "user_id": staff_user["user_id"]},
        headers=staff_auth_headers,
    )
    other_sale_id = other_sale.json()["sale_id"]

    list_response = client.get("/sales/", headers=auth_headers)
    assert list_response.status_code == 200
    returned_ids = [s["sale_id"] for s in list_response.json()]
    assert own_sale_id in returned_ids
    assert other_sale_id not in returned_ids

    get_own = client.get(f"/sales/{own_sale_id}", headers=auth_headers)
    assert get_own.status_code == 200

    get_other = client.get(f"/sales/{other_sale_id}", headers=auth_headers)
    assert get_other.status_code == 403


def test_customer_with_no_profile_sees_empty_list(client, auth_headers):
    """A customer who was never linked to a Customer record has no sales to show."""
    response = client.get("/sales/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []