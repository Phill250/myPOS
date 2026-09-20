
def test_list_categories_success(client, auth_headers):
    response = client.get("/categories/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_category_success(client, staff_auth_headers):
    category_data = {"category_name": "Fiction", "description": "Novels and stories"}
    create_response = client.post("/categories/", json=category_data, headers=staff_auth_headers)
    category_id = create_response.json()["category_id"]

    response = client.get(f"/categories/{category_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["category_name"] == "Fiction"



def test_create_category_success(client, staff_auth_headers):
    category_data = {"category_name": "Fiction", "description": "Novels and stories"}
    response = client.post("/categories/", json=category_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["category_name"] == "Fiction"
    assert "category_id" in body


def test_create_category_without_description_success(client, staff_auth_headers):
   
    response = client.post("/categories/", json={"category_name": "Poetry"}, headers=staff_auth_headers)
    assert response.status_code == 201



def test_update_category_success(client, staff_auth_headers):
    category_data = {"category_name": "Fiction", "description": "Novels and stories"}
    create_response = client.post("/categories/", json=category_data, headers=staff_auth_headers)
    category_id = create_response.json()["category_id"]

    response = client.put(
        f"/categories/{category_id}",
        json={"category_name": "Fiction & Fantasy"},
        headers=staff_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["category_name"] == "Fiction & Fantasy"



def test_delete_category_success(client, staff_auth_headers):
    category_data = {"category_name": "Fiction", "description": "Novels and stories"}
    create_response = client.post("/categories/", json=category_data, headers=staff_auth_headers)
    category_id = create_response.json()["category_id"]

    delete_response = client.delete(f"/categories/{category_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/categories/{category_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404



def test_create_category_missing_name_returns_422(client, staff_auth_headers):
    response = client.post("/categories/", json={"description": "No name given"}, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_category_invalid_name_type_returns_422(client, staff_auth_headers):
    response = client.post("/categories/", json={"category_name": 12345}, headers=staff_auth_headers)
    assert response.status_code == 422



def test_list_categories_without_credentials_returns_401(client):
    response = client.get("/categories/")
    assert response.status_code == 401


def test_get_category_without_credentials_returns_401(client):
    response = client.get("/categories/1")
    assert response.status_code == 401


def test_create_category_without_credentials_returns_401(client):
    response = client.post("/categories/", json={"category_name": "Fiction"})
    assert response.status_code == 401


def test_update_category_without_credentials_returns_401(client):
    response = client.put("/categories/1", json={"category_name": "New Name"})
    assert response.status_code == 401


def test_delete_category_without_credentials_returns_401(client):
    response = client.delete("/categories/1")
    assert response.status_code == 401



def test_create_category_as_customer_returns_403(client, auth_headers):
    response = client.post("/categories/", json={"category_name": "Fiction"}, headers=auth_headers)
    assert response.status_code == 403


def test_delete_category_as_customer_returns_403(client, auth_headers):
    response = client.delete("/categories/1", headers=auth_headers)
    assert response.status_code == 403



def test_get_nonexistent_category_returns_404(client, staff_auth_headers):
    response = client.get("/categories/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_category_returns_404(client, staff_auth_headers):
    response = client.put(
        "/categories/999999", json={"category_name": "Doesn't matter"}, headers=staff_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_category_returns_404(client, staff_auth_headers):
    response = client.delete("/categories/999999", headers=staff_auth_headers)
    assert response.status_code == 404