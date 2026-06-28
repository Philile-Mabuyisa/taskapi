# tests/test_tasks.py
# These are automated tests — run with: pytest
# Tests prove your code works AND show employers you know how to write them

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# Use a separate in-memory SQLite DB for tests so we don't mess up real data
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Replace the real DB with the test DB
app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def register_and_login(username="testuser", password="secret123"):
    """Register a user and return their auth token"""
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password
    })
    response = client.post("/auth/login", data={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ─── AUTH TESTS ───────────────────────────────────────────────────────────────

def test_register_user():
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@test.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert "hashed_password" not in response.json()  # never expose password


def test_register_duplicate_username():
    client.post("/auth/register", json={
        "username": "dupeuser",
        "email": "dupe@test.com",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "username": "dupeuser",
        "email": "other@test.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_login_returns_token():
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@test.com",
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


# ─── TASK TESTS ───────────────────────────────────────────────────────────────

def test_create_task():
    token = register_and_login("taskuser1", "password123")
    response = client.post("/tasks/", json={
        "title": "Buy groceries",
        "priority": "high"
    }, headers=auth_headers(token))
    assert response.status_code == 201
    assert response.json()["title"] == "Buy groceries"
    assert response.json()["status"] == "todo"


def test_get_tasks():
    token = register_and_login("taskuser2", "password123")
    client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers(token))
    client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers(token))
    response = client.get("/tasks/", headers=auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_task_status():
    token = register_and_login("taskuser3", "password123")
    create = client.post("/tasks/", json={"title": "Finish report"}, headers=auth_headers(token))
    task_id = create.json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"status": "done"}, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_delete_task():
    token = register_and_login("taskuser4", "password123")
    create = client.post("/tasks/", json={"title": "Delete me"}, headers=auth_headers(token))
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers(token))
    assert response.status_code == 204


def test_cannot_access_other_users_task():
    """Security test — user A cannot see user B's tasks"""
    token_a = register_and_login("usera", "password123")
    token_b = register_and_login("userb", "password123")
    create = client.post("/tasks/", json={"title": "Secret task"}, headers=auth_headers(token_a))
    task_id = create.json()["id"]
    response = client.get(f"/tasks/{task_id}", headers=auth_headers(token_b))
    assert response.status_code == 404


def test_task_summary():
    token = register_and_login("summaryuser", "password123")
    client.post("/tasks/", json={"title": "T1", "status": "todo"}, headers=auth_headers(token))
    client.post("/tasks/", json={"title": "T2", "status": "done"}, headers=auth_headers(token))
    response = client.get("/tasks/summary", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["done"] == 1


def test_requires_auth():
    """Any task route without a token should return 401"""
    response = client.get("/tasks/")
    assert response.status_code == 401
