import pytest
from app import app, users, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    users.clear()
    with app.test_client() as client:
        yield client


# ---- FE-9: registration ----
def test_register_success(client):
    resp = client.post("/api/register", json={
        "username": "alice", "password": "Passw0rd1"
    })
    assert resp.status_code == 201
    assert "alice" in users


def test_register_weak_password_rejected(client):
    # FE-10: weak password should be rejected
    resp = client.post("/api/register", json={
        "username": "bob", "password": "weak"
    })
    assert resp.status_code == 400
    assert "Password" in resp.get_json()["error"]


def test_register_duplicate_username(client):
    client.post("/api/register", json={"username": "alice", "password": "Passw0rd1"})
    resp = client.post("/api/register", json={"username": "alice", "password": "Passw0rd2"})
    assert resp.status_code == 409


# ---- FE-11 / FE-6: login/logout ----
def test_login_missing_fields(client):
    # FE-6: incomplete credentials error message
    resp = client.post("/api/login", json={"username": "alice"})
    assert resp.status_code == 400
    assert "both" in resp.get_json()["error"]


def test_login_wrong_password(client):
    client.post("/api/register", json={"username": "alice", "password": "Passw0rd1"})
    resp = client.post("/api/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_login_logout_success(client):
    client.post("/api/register", json={"username": "alice", "password": "Passw0rd1"})
    login_resp = client.post("/api/login", json={"username": "alice", "password": "Passw0rd1"})
    assert login_resp.status_code == 200

    logout_resp = client.post("/api/logout")
    assert logout_resp.status_code == 200


# ---- FE-7: inventory ----
def test_inventory_requires_login(client):
    resp = client.get("/api/inventory")
    assert resp.status_code == 401


def test_inventory_view_after_login(client):
    client.post("/api/register", json={"username": "alice", "password": "Passw0rd1"})
    client.post("/api/login", json={"username": "alice", "password": "Passw0rd1"})
    resp = client.get("/api/inventory")
    assert resp.status_code == 200
    assert resp.get_json() == inventory


# ---- FE-12: low stock ----
def test_low_stock_after_login(client):
    client.post("/api/register", json={"username": "alice", "password": "Passw0rd1"})
    client.post("/api/login", json={"username": "alice", "password": "Passw0rd1"})
    resp = client.get("/api/inventory/low-stock")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["threshold"] == 5
    # widget-b has quantity 3 in the seed data, so it should appear
    assert "widget-b" in data["low_stock_items"]
