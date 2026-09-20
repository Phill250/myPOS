def test_list_customers_success(client, staff_auth_headers):
    response = client.get("/customers/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_customer_success(client, staff_auth_headers):
    customer_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": True,
    }
    create_response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    customer_id = create_response.json()["customer_id"]

    response = client.get(f"/customers/{customer_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"



def test_create_customer_success(client, staff_auth_headers):
    customer_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": True,
    }
    response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Jane"
    assert "customer_id" in body



def test_update_customer_success(client, staff_auth_headers):
    customer_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": True,
    }
    create_response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    customer_id = create_response.json()["customer_id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={"phone_number": "0799999999"},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["phone_number"] == "0799999999"



def test_delete_customer_success(client, staff_auth_headers):
    customer_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": True,
    }
    create_response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    customer_id = create_response.json()["customer_id"]

    delete_response = client.delete(f"/customers/{customer_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/customers/{customer_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404



def test_create_customer_missing_first_name_returns_422(client, staff_auth_headers):
    customer_data = {
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": True,
    }
    response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_customer_invalid_library_member_type_returns_422(client, staff_auth_headers):
    customer_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "0700000001",
        "email": "jane@example.com",
        "library_member": "not-a-bool",
    }
    response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    assert response.status_code == 422



def test_list_customers_without_credentials_returns_401(client):
    response = client.get("/customers/")
    assert response.status_code == 401


def test_get_customer_without_credentials_returns_401(client):
    response = client.get("/customers/1")
    assert response.status_code == 401


def test_create_customer_without_credentials_returns_401(client):
    response = client.post("/customers/", json={
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    })
    assert response.status_code == 401


def test_update_customer_without_credentials_returns_401(client):
    response = client.put("/customers/1", json={"phone_number": "0799999999"})
    assert response.status_code == 401


def test_delete_customer_without_credentials_returns_401(client):
    response = client.delete("/customers/1")
    assert response.status_code == 401



def test_create_customer_as_customer_returns_403(client, auth_headers):
    response = client.post("/customers/", json={
        "first_name": "Jane", "last_name": "Doe", "phone_number": "0700000001",
        "email": "jane@example.com", "library_member": True,
    }, headers=auth_headers)
    assert response.status_code == 403


def test_delete_customer_as_customer_returns_403(client, auth_headers):
    response = client.delete("/customers/1", headers=auth_headers)
    assert response.status_code == 403


def test_list_customers_as_customer_returns_403(client, auth_headers):
    """Listing ALL customers would leak everyone's contact info — staff/admin only."""
    response = client.get("/customers/", headers=auth_headers)
    assert response.status_code == 403



def test_get_nonexistent_customer_returns_404(client, staff_auth_headers):
    response = client.get("/customers/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_customer_returns_404(client, staff_auth_headers):
    response = client.put(
        "/customers/999999", json={"phone_number": "0799999999"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_customer_returns_404(client, staff_auth_headers):
    response = client.delete("/customers/999999", headers=staff_auth_headers)
    assert response.status_code == 404



def test_customer_can_view_own_linked_profile(client, staff_auth_headers, auth_headers, test_user):
    customer_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "phone_number": "0700000000",
        "email": "testuser@example.com",
        "library_member": False,
        "user_id": test_user["user_id"],
    }
    create_response = client.post("/customers/", json=customer_data, headers=staff_auth_headers)
    customer_id = create_response.json()["customer_id"]

    response = client.get(f"/customers/{customer_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id


def test_customer_cannot_view_someone_elses_profile(client, staff_auth_headers, auth_headers):
    other_customer_data = {
        "first_name": "Other",
        "last_name": "Person",
        "phone_number": "0711111111",
        "email": "other@example.com",
        "library_member": False,
    }
    create_response = client.post("/customers/", json=other_customer_data, headers=staff_auth_headers)
    other_customer_id = create_response.json()["customer_id"]

    response = client.get(f"/customers/{other_customer_id}", headers=auth_headers)
    assert response.status_code == 403