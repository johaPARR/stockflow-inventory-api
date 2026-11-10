
def create_category(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Productos electrónicos",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client, category_id):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "ELEC-001",
            "name": "Auriculares Bluetooth",
            "description": "Auriculares inalámbricos",
            "price": 45000,
            "category_id": category_id,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_product(client):
    category_id = create_category(client)

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "ELEC-001",
            "name": "Auriculares Bluetooth",
            "description": "Auriculares inalámbricos",
            "price": 45000,
            "category_id": category_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sku"] == "ELEC-001"
    assert data["name"] == "Auriculares Bluetooth"
    assert float(data["price"]) == 45000
    assert data["category_id"] == category_id
    assert data["is_active"] is True
    assert "id" in data


def test_get_products(client):
    category_id = create_category(client)
    create_product(client, category_id)

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["sku"] == "ELEC-001"


def test_get_product_by_id(client):
    category_id = create_category(client)
    product = create_product(client, category_id)

    response = client.get(
        f"/api/v1/products/{product['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == product["id"]
    assert response.json()["sku"] == "ELEC-001"


def test_update_product(client):
    category_id = create_category(client)
    product = create_product(client, category_id)

    response = client.patch(
        f"/api/v1/products/{product['id']}",
        json={
            "description": "Descripción actualizada",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Descripción actualizada"


def test_create_duplicate_product_sku(client):
    category_id = create_category(client)

    first_product = create_product(client, category_id)

    second_response = client.post(
        "/api/v1/products",
        json={
            "sku": "ELEC-001",
            "name": "Otro producto",
            "description": "Producto duplicado",
            "price": 30000,
            "category_id": category_id,
        },
    )

    assert first_product["sku"] == "ELEC-001"
    assert second_response.status_code == 409


def test_create_product_with_invalid_data(client):
    category_id = create_category(client)

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "A",
            "name": "X",
            "description": "Producto inválido",
            "price": -100,
            "category_id": category_id,
        },
    )

    assert response.status_code == 422


def test_create_product_with_inactive_category(client):
    category_id = create_category(client)

    deactivate_response = client.patch(
        f"/api/v1/categories/{category_id}",
        json={
            "is_active": False,
        },
    )

    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "ELEC-002",
            "name": "Teclado inalámbrico",
            "description": "Producto para probar categorías inactivas",
            "price": 35000,
            "category_id": category_id,
        },
    )

    assert response.status_code == 409
