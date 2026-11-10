
def test_create_category(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Productos electrónicos",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Electrónica"
    assert data["description"] == "Productos electrónicos"
    assert data["is_active"] is True
    assert "id" in data


def test_get_categories(client):
    client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Productos electrónicos",
        },
    )

    response = client.get("/api/v1/categories")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Electrónica"


def test_get_category_by_id(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Productos electrónicos",
        },
    )

    category_id = create_response.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}")

    assert response.status_code == 200
    assert response.json()["id"] == category_id


def test_update_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Descripción inicial",
        },
    )

    category_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/categories/{category_id}",
        json={
            "description": "Descripción actualizada",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Descripción actualizada"


def test_create_duplicate_category(client):
    payload = {
        "name": "Electrónica",
        "description": "Productos electrónicos",
    }

    first_response = client.post(
        "/api/v1/categories",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/categories",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_create_category_with_invalid_data(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "A",
            "description": "Categoría inválida",
        },
    )

    assert response.status_code == 422


def test_deactivate_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Informática",
            "description": "Productos informáticos",
        },
    )

    assert create_response.status_code == 201

    category_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/categories/{category_id}",
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_get_deactivated_category(client):
    create_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Accesorios",
            "description": "Accesorios tecnológicos",
        },
    )

    category_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/categories/{category_id}",
        json={
            "is_active": False,
        },
    )

    response = client.get(
        f"/api/v1/categories/{category_id}"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
