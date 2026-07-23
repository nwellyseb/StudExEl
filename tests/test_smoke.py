def test_home_page_loads(client):

    response = client.get("/")

    assert response.status_code == 200
    assert b"StudExEl" in response.data


def test_marketplace_page_loads(client):

    response = client.get("/marketplace")

    assert response.status_code == 200
    assert b"Marketplace" in response.data


def test_dashboard_requires_login(client):

    response = client.get(
        "/dashboard"
    )

    assert response.status_code == 302
    assert response.headers[
        "Location"
    ].endswith("/login")


def test_sell_page_requires_login(client):

    response = client.get(
        "/sell"
    )

    assert response.status_code == 302
    assert response.headers[
        "Location"
    ].endswith("/login")


def test_health_check_returns_ok(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.get_json() == {
        "status": "ok",
    }
