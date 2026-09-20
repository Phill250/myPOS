def test_list_suppliers_success(client, staff_auth_headers):
    response = client.get("/suppliers/", headers=staff_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_supplier_success(client, staff_auth_headers):
    supplier_data = {"company_name": "Acme Books Ltd", "phone_number": "0700123456"}
    create_response = client.post("/suppliers/", json=supplier_data, headers=staff_auth_headers)
    supplier_id = create_response.json()["supplier_id"]

    response = client.get(f"/suppliers/{supplier_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["company_name"] == "Acme Books Ltd"


def test_create_supplier_success(client, staff_auth_headers):
    supplier_data = {"company_name": "Acme Books Ltd", "phone_number": "0700123456"}
    response = client.post("/suppliers/", json=supplier_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["company_name"] == "Acme Books Ltd"
    assert "supplier_id" in body


def test_update_supplier_success(client, staff_auth_headers):
    supplier_data = {"company_name": "Acme Books Ltd", "phone_number": "0700123456"}
    create_response = client.post("/suppliers/", json=supplier_data, headers=staff_auth_headers)
    supplier_id = create_response.json()["supplier_id"]

    response = client.put(
        f"/suppliers/{supplier_id}",
        json={"phone_number": "0799999999"},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["phone_number"] == "0799999999"


def test_delete_supplier_success(client, staff_auth_headers):
    supplier_data = {"company_name": "Acme Books Ltd", "phone_number": "0700123456"}
    create_response = client.post("/suppliers/", json=supplier_data, headers=staff_auth_headers)
    supplier_id = create_response.json()["supplier_id"]

    delete_response = client.delete(f"/suppliers/{supplier_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/suppliers/{supplier_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404


def test_create_supplier_missing_company_name_returns_422(client, staff_auth_headers):
    response = client.post("/suppliers/", json={"phone_number": "0700123456"}, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_supplier_missing_phone_number_returns_422(client, staff_auth_headers):
    response = client.post("/suppliers/", json={"company_name": "Acme Books Ltd"}, headers=staff_auth_headers)
    assert response.status_code == 422


def test_list_suppliers_without_credentials_returns_401(client):
    response = client.get("/suppliers/")
    assert response.status_code == 401


def test_get_supplier_without_credentials_returns_401(client):
    response = client.get("/suppliers/1")
    assert response.status_code == 401


def test_create_supplier_without_credentials_returns_401(client):
    response = client.post("/suppliers/", json={"company_name": "Acme", "phone_number": "0700123456"})
    assert response.status_code == 401


def test_update_supplier_without_credentials_returns_401(client):
    response = client.put("/suppliers/1", json={"phone_number": "0799999999"})
    assert response.status_code == 401


def test_delete_supplier_without_credentials_returns_401(client):
    response = client.delete("/suppliers/1")
    assert response.status_code == 401


def test_list_suppliers_as_customer_returns_403(client, auth_headers):
    response = client.get("/suppliers/", headers=auth_headers)
    assert response.status_code == 403


def test_get_supplier_as_customer_returns_403(client, auth_headers):
    response = client.get("/suppliers/1", headers=auth_headers)
    assert response.status_code == 403


def test_create_supplier_as_customer_returns_403(client, auth_headers):
    response = client.post(
        "/suppliers/", json={"company_name": "Acme", "phone_number": "0700123456"}, headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_supplier_as_customer_returns_403(client, auth_headers):
    response = client.delete("/suppliers/1", headers=auth_headers)
    assert response.status_code == 403


def test_get_nonexistent_supplier_returns_404(client, staff_auth_headers):
    response = client.get("/suppliers/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_supplier_returns_404(client, staff_auth_headers):
    response = client.put(
        "/suppliers/999999", json={"phone_number": "0799999999"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_supplier_returns_404(client, staff_auth_headers):
    response = client.delete("/suppliers/999999", headers=staff_auth_headers)
    assert response.status_code == 404