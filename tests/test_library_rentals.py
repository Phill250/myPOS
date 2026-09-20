def test_list_rentals_success(client, staff_auth_headers):
    response = client.get("/library-rentals/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_rental_success(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_data = {
        "expected_return": "2026-12-01",
        "customer_id": customer_id,
        "user_id": staff_user["user_id"],
    }
    create_response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    rental_id = create_response.json()["rental_id"]

    response = client.get(f"/library-rentals/{rental_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id


def test_create_rental_success(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_data = {
        "expected_return": "2026-12-01",
        "customer_id": customer_id,
        "user_id": staff_user["user_id"],
    }
    response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer_id
    assert "rental_id" in body


def test_update_rental_mark_returned(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_data = {
        "expected_return": "2026-12-01",
        "customer_id": customer_id,
        "user_id": staff_user["user_id"],
    }
    create_response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    rental_id = create_response.json()["rental_id"]

    response = client.put(
        f"/library-rentals/{rental_id}",
        json={"actual_return": "2026-11-20"},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["actual_return"] == "2026-11-20"


def test_update_rental_ignores_customer_id_reassignment(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_data = {
        "expected_return": "2026-12-01",
        "customer_id": customer_id,
        "user_id": staff_user["user_id"],
    }
    create_response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    rental_id = create_response.json()["rental_id"]

    response = client.put(
        f"/library-rentals/{rental_id}",
        json={"expected_return": "2026-12-15", "customer_id": 999, "user_id": 999},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["expected_return"] == "2026-12-15"
    assert body["customer_id"] != 999
    assert body["user_id"] != 999


def test_delete_rental_success(client, staff_auth_headers, staff_user):
    customer_data = {
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    rental_data = {
        "expected_return": "2026-12-01",
        "customer_id": customer_id,
        "user_id": staff_user["user_id"],
    }
    create_response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    rental_id = create_response.json()["rental_id"]

    delete_response = client.delete(f"/library-rentals/{rental_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/library-rentals/{rental_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_rental_missing_customer_id_returns_422(client, staff_auth_headers, staff_user):
    rental_data = {"expected_return": "2026-12-01", "user_id": staff_user["user_id"]}
    response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_rental_invalid_date_format_returns_422(client, staff_auth_headers, staff_user):
    rental_data = {
        "expected_return": "not-a-date",
        "customer_id": 1,
        "user_id": staff_user["user_id"],
    }
    response = client.post("/library-rentals/", json=rental_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_list_rentals_without_credentials_returns_401(client):
    response = client.get("/library-rentals/")
    assert response.status_code == 401


def test_get_rental_without_credentials_returns_401(client):
    response = client.get("/library-rentals/1")
    assert response.status_code == 401


def test_create_rental_without_credentials_returns_401(client):
    response = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": 1, "user_id": 1,
    })
    assert response.status_code == 401


def test_update_rental_without_credentials_returns_401(client):
    response = client.put("/library-rentals/1", json={"actual_return": "2026-12-01"})
    assert response.status_code == 401


def test_delete_rental_without_credentials_returns_401(client):
    response = client.delete("/library-rentals/1")
    assert response.status_code == 401


def test_create_rental_as_customer_returns_403(client, auth_headers):
    response = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": 1, "user_id": 1,
    }, headers=auth_headers)
    assert response.status_code == 403


def test_delete_rental_as_customer_returns_403(client, auth_headers):
    response = client.delete("/library-rentals/1", headers=auth_headers)
    assert response.status_code == 403


def test_get_nonexistent_rental_returns_404(client, staff_auth_headers):
    response = client.get("/library-rentals/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_rental_returns_404(client, staff_auth_headers):
    response = client.put(
        "/library-rentals/999999", json={"actual_return": "2026-12-01"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_rental_returns_404(client, staff_auth_headers):
    response = client.delete("/library-rentals/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_customer_sees_only_own_rentals(client, staff_auth_headers, staff_user, auth_headers, test_user):
    customer_data = {
        "first_name": "Test", "last_name": "Customer", "phone_number": "0700000000",
        "email": "testuser@example.com", "library_member": True,
        "user_id": test_user["user_id"],
    }
    customer_id = client.post("/customers/", json=customer_data, headers=staff_auth_headers).json()["customer_id"]

    other_customer_data = {
        "first_name": "Other", "last_name": "Person", "phone_number": "0711111111",
        "email": "other@example.com", "library_member": True,
    }
    other_customer_id = client.post(
        "/customers/", json=other_customer_data, headers=staff_auth_headers
    ).json()["customer_id"]

    own_rental = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": customer_id, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers)
    own_rental_id = own_rental.json()["rental_id"]

    other_rental = client.post("/library-rentals/", json={
        "expected_return": "2026-12-01", "customer_id": other_customer_id, "user_id": staff_user["user_id"],
    }, headers=staff_auth_headers)
    other_rental_id = other_rental.json()["rental_id"]

    list_response = client.get("/library-rentals/", headers=auth_headers)
    assert list_response.status_code == 200
    returned_ids = [r["rental_id"] for r in list_response.json()]
    assert own_rental_id in returned_ids
    assert other_rental_id not in returned_ids

    get_own = client.get(f"/library-rentals/{own_rental_id}", headers=auth_headers)
    assert get_own.status_code == 200

    get_other = client.get(f"/library-rentals/{other_rental_id}", headers=auth_headers)
    assert get_other.status_code == 403


def test_customer_with_no_profile_sees_empty_rental_list(client, auth_headers):
    response = client.get("/library-rentals/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []