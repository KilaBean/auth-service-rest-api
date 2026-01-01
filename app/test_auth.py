def test_register_user(client):
    # 1. Try to register a user
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123"
        }
    )
    # 2. Check that the server said "OK" (200)
    assert response.status_code == 200
    # 3. Check that the email is in the response
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"

def test_duplicate_register(client):
    # 1. Register first user
    # NOTE: Changed "Pass123" to "Pass1234" to meet the 8-char requirement
    client.post("/auth/register", json={"email": "dup@example.com", "password": "Pass1234"})

    # 2. Try to register the same email again
    response = client.post("/auth/register", json={"email": "dup@example.com", "password": "Pass1234"})

    # 3. Should fail with 400 (because email is taken)
    assert response.status_code == 400

def test_login_and_protected_route(client):
    # 1. Setup: Register a user
    client.post("/auth/register", json={"email": "auth@example.com", "password": "AuthPass123"})
    
    # 2. Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "auth@example.com",
            "password": "AuthPass123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Access protected route WITHOUT token (should fail)
    response = client.get("/users/me")
    assert response.status_code == 401 # Unauthorized
    
    # 4. Access protected route WITH token (should succeed)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "auth@example.com"

def test_weak_password_rejection(client):
    response = client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "123"}
    )
    # Our Pydantic schema should reject passwords < 8 chars or without letters
    assert response.status_code == 422 