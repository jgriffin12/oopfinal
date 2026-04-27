from app.main import create_app


def test_login_route_exists():
    """
    Verify that the /login route is registered and returns JSON.
    """
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "password123"})
    assert response.status_code == 200
    assert response.is_json is True


def test_verify_mfa_route_exists():
    """
    Verify that the /verify-mfa route is registered.
    """
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/verify-mfa",
        json={
            "username": "alice",
            "code": "123456"})
    assert response.status_code == 200
    assert response.is_json is True


def test_admin_health_route_exists():
    """
    Verify that the admin blueprint is active.
    """
    app = create_app()
    client = app.test_client()

    response = client.get("/admin/health")
    assert response.status_code == 200
    assert response.is_json is True
