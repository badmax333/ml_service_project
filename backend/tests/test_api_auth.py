from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_register():
    # Используем уникальный email для каждого запуска
    import time
    unique_email = f"test_{int(time.time())}@example.com"
    
    response = client.post("/auth/register", json={
        "email": unique_email,
        "password": "123456",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == unique_email

def test_register_duplicate_email():
    # Первая регистрация
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "123456"
    })
    # Вторая регистрация с тем же email
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "123456"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login():
    email = "login_test@example.com"
    # Регистрация
    client.post("/auth/register", json={
        "email": email,
        "password": "123456"
    })
    # Логин
    response = client.post("/auth/login", json={
        "email": email,
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()