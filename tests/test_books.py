
def test_list_books_success(client, auth_headers):
    response = client.get("/books/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_book_success(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    create_response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    book_id = create_response.json()["book_id"]

    response = client.get(f"/books/{book_id}", headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"



def test_create_book_success(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }

    response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Test Book"
    assert "book_id" in body



def test_update_book_success(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    create_response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    book_id = create_response.json()["book_id"]

    updated_book = {
        "title": "Purple cow",
        "author": "Updated Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 19.99,
    }
    response = client.put(f"/books/{book_id}", json=updated_book, headers=staff_auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Purple cow"



def test_delete_book_success(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    create_response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    book_id = create_response.json()["book_id"]

    delete_response = client.delete(f"/books/{book_id}", headers=staff_auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/books/{book_id}", headers=staff_auth_headers)
    assert get_response.status_code == 404



def test_create_book_missing_title_returns_422(client, staff_auth_headers):
    product_data = {
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_book_invalid_price_type_returns_422(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": "not-a-number",
    }
    response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_create_book_missing_required_fk_returns_422(client, staff_auth_headers):
   
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "sale_price": 9.99,
    }
    response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    assert response.status_code == 422


def test_update_book_invalid_price_type_returns_422(client, staff_auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    create_response = client.post("/books/", json=product_data, headers=staff_auth_headers)
    book_id = create_response.json()["book_id"]

    bad_update = {"sale_price": "not-a-number"}
    response = client.put(f"/books/{book_id}", json=bad_update, headers=staff_auth_headers)
    assert response.status_code == 422



def test_list_books_without_credentials_returns_401(client):
    response = client.get("/books/")
    assert response.status_code == 401


def test_get_book_without_credentials_returns_401(client):
    response = client.get("/books/1")
    assert response.status_code == 401


def test_create_book_without_credentials_returns_401(client):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    response = client.post("/books/", json=product_data)
    assert response.status_code == 401


def test_update_book_without_credentials_returns_401(client):
    response = client.put("/books/1", json={"title": "New Title"})
    assert response.status_code == 401


def test_delete_book_without_credentials_returns_401(client):
    response = client.delete("/books/1")
    assert response.status_code == 401



def test_create_book_as_customer_returns_403(client, auth_headers):
    product_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category_id": 1,
        "supplier_id": 1,
        "sale_price": 9.99,
    }
    response = client.post("/books/", json=product_data, headers=auth_headers)
    assert response.status_code == 403


def test_delete_book_as_customer_returns_403(client, auth_headers):
    response = client.delete("/books/1", headers=auth_headers)
    assert response.status_code == 403



def test_get_nonexistent_book_returns_404(client, staff_auth_headers):
    response = client.get("/books/999999", headers=staff_auth_headers)
    assert response.status_code == 404


def test_update_nonexistent_book_returns_404(client, staff_auth_headers):
    response = client.put(
        "/books/999999",
        json={"title": "Doesn't matter"},
        headers=staff_auth_headers,
    )
    assert response.status_code == 404


def test_delete_nonexistent_book_returns_404(client, staff_auth_headers):
    response = client.delete("/books/999999", headers=staff_auth_headers)
    assert response.status_code == 404