import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


os.environ["DATABASE_URL"] = "sqlite://"

from database import Base, get_db
from main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    
    
@pytest.fixture
def test_user(client):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    
    response = client.post("/users/register", json=user_data)
    user_data["user_id"] = response.json().get("user_id")
    return user_data

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/users/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_user(client):
    """Creates a staff-role user directly in the DB, bypassing the API,
    since /users/register always forces role='customer' and /users/ (admin
    create) is itself locked behind an existing super_admin — so tests need
    a side-door the same way seed_super_admin.py does for real deployments."""
    from database import Base
    from services import auth_services
    from schemas.users import UserCreateByAdmin

    db = TestingSessionLocal()
    try:
        data = UserCreateByAdmin(
            username="teststaff",
            password="staffpassword",
            role="staff",
            is_active=True,
        )
        created = auth_services.create_user_as_admin(db, data)
        user_id = created.user_id
    finally:
        db.close()

    return {"username": "teststaff", "password": "staffpassword", "user_id": user_id}


@pytest.fixture
def staff_auth_headers(client, staff_user):
    response = client.post(
        "/users/login",
        data={"username": staff_user["username"], "password": staff_user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(client):
    """Creates a super_admin-role user directly in the DB, bypassing the API,
    the same way seed_super_admin.py bootstraps the very first admin."""
    from services import auth_services
    from schemas.users import UserCreateByAdmin

    db = TestingSessionLocal()
    try:
        data = UserCreateByAdmin(
            username="testadmin",
            password="adminpassword",
            role="super_admin",
            is_active=True,
        )
        created = auth_services.create_user_as_admin(db, data)
        user_id = created.user_id
    finally:
        db.close()

    return {"username": "testadmin", "password": "adminpassword", "user_id": user_id}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    response = client.post(
        "/users/login",
        data={"username": admin_user["username"], "password": admin_user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}