
def test_register_success(client):
    response = client.post("/users/register", json={
        "username": "newcustomer", "password": "somepassword",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "newcustomer"
    assert body["role"] == "customer"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_always_forces_customer_role(client):
    """Even if role is smuggled into the request body, it must be ignored —
    UserCreate has no role field at all."""
    response = client.post("/users/register", json={
        "username": "sneaky", "password": "somepassword", "role": "super_admin",
    })
    assert response.status_code == 201
    assert response.json()["role"] == "customer"


def test_register_duplicate_username_returns_400(client, test_user):
    response = client.post("/users/register", json={
        "username": test_user["username"], "password": "anotherpassword",
    })
    assert response.status_code == 400


def test_register_missing_password_returns_422(client):
    response = client.post("/users/register", json={"username": "nopassword"})
    assert response.status_code == 422


def test_register_missing_username_returns_422(client):
    response = client.post("/users/register", json={"password": "somepassword"})
    assert response.status_code == 422




def test_login_success(client, test_user):
    response = client.post("/users/login", data={
        "username": test_user["username"], "password": test_user["password"],
    })
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client, test_user):
    response = client.post("/users/login", data={
        "username": test_user["username"], "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_username_returns_401(client):
    response = client.post("/users/login", data={
        "username": "doesnotexist", "password": "whatever",
    })
    assert response.status_code == 401




def test_list_users_success(client, admin_auth_headers):
    response = client.get("/users/", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_success(client, admin_auth_headers, test_user):
    response = client.get(f"/users/{test_user['user_id']}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]


def test_create_user_as_admin_success(client, admin_auth_headers):
    response = client.post("/users/", json={
        "username": "newstaff", "password": "somepassword", "role": "staff", "is_active": True,
    }, headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "newstaff"
    assert body["role"] == "staff"


def test_update_user_success(client, admin_auth_headers, test_user):
    response = client.put(
        f"/users/{test_user['user_id']}", json={"is_active": False}, headers=admin_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_user_success(client, admin_auth_headers, test_user):
    delete_response = client.delete(f"/users/{test_user['user_id']}", headers=admin_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{test_user['user_id']}", headers=admin_auth_headers)
    assert get_response.status_code == 404



def test_create_user_missing_role_returns_422(client, admin_auth_headers):
    response = client.post("/users/", json={
        "username": "newstaff", "password": "somepassword", "is_active": True,
    }, headers=admin_auth_headers)
    assert response.status_code == 422


def test_create_user_invalid_is_active_type_returns_422(client, admin_auth_headers):
    response = client.post("/users/", json={
        "username": "newstaff", "password": "somepassword", "role": "staff",
        "is_active": ["not", "a", "bool"],
    }, headers=admin_auth_headers)
    assert response.status_code == 422



def test_list_users_without_credentials_returns_401(client):
    response = client.get("/users/")
    assert response.status_code == 401


def test_get_user_without_credentials_returns_401(client):
    response = client.get("/users/1")
    assert response.status_code == 401


def test_create_user_without_credentials_returns_401(client):
    response = client.post("/users/", json={
        "username": "x", "password": "y", "role": "staff", "is_active": True,
    })
    assert response.status_code == 401


def test_update_user_without_credentials_returns_401(client):
    response = client.put("/users/1", json={"is_active": False})
    assert response.status_code == 401


def test_delete_user_without_credentials_returns_401(client):
    response = client.delete("/users/1")
    assert response.status_code == 401



def test_list_users_as_staff_returns_403(client, staff_auth_headers):
    """Only super_admin — not staff — can list all users."""
    response = client.get("/users/", headers=staff_auth_headers)
    assert response.status_code == 403


def test_list_users_as_customer_returns_403(client, auth_headers):
    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 403


def test_create_user_as_staff_returns_403(client, staff_auth_headers):
    response = client.post("/users/", json={
        "username": "x", "password": "y", "role": "staff", "is_active": True,
    }, headers=staff_auth_headers)
    assert response.status_code == 403


def test_create_user_as_customer_returns_403(client, auth_headers):
    response = client.post("/users/", json={
        "username": "x", "password": "y", "role": "staff", "is_active": True,
    }, headers=auth_headers)
    assert response.status_code == 403


def test_delete_user_as_staff_returns_403(client, staff_auth_headers, test_user):
    response = client.delete(f"/users/{test_user['user_id']}", headers=staff_auth_headers)
    assert response.status_code == 403


def test_update_user_as_customer_returns_403(client, auth_headers, test_user):
    response = client.put(
        f"/users/{test_user['user_id']}", json={"is_active": False}, headers=auth_headers
    )
    assert response.status_code == 403



def test_get_user_as_staff_allowed(client, staff_auth_headers, test_user):
    """GET /{user_id} only requires get_current_user, not super_admin."""
    response = client.get(f"/users/{test_user['user_id']}", headers=staff_auth_headers)
    assert response.status_code == 200



def test_get_nonexistent_user_returns_404(client, admin_auth_headers):
    response = client.get("/users/999999", headers=admin_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_user_returns_404(client, admin_auth_headers):
    response = client.put(
        "/users/999999", json={"is_active": False}, headers=admin_auth_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_user_returns_404(client, admin_auth_headers):
    response = client.delete("/users/999999", headers=admin_auth_headers)
    assert response.status_code == 404