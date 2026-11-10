
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


def create_product(client):
    category_id = create_category(client)

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "INV-001",
            "name": "Teclado mecánico",
            "description": "Teclado para pruebas de inventario",
            "price": 50000,
            "category_id": category_id,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_get_inventory(client):
    product = create_product(client)

    response = client.get(
        f"/api/v1/inventory/{product['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product["id"]
    assert data["quantity"] == 0
    assert data["min_stock"] == 5


def test_get_inventories(client):
    create_product(client)

    response = client.get("/api/v1/inventory")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_register_inventory_entry(client):
    product = create_product(client)

    response = client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 100,
            "reason": "Reposición de mercadería",
            "reference": "COMPRA-001",
            "notes": "Entrada para pruebas",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movement_type"] == "ENTRY"
    assert data["quantity"] == 100
    assert data["previous_quantity"] == 0
    assert data["new_quantity"] == 100


def test_register_inventory_exit(client):
    product = create_product(client)

    client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 100,
            "reason": "Stock inicial",
        },
    )

    response = client.post(
        "/api/v1/inventory/exits",
        json={
            "product_id": product["id"],
            "quantity": 10,
            "reason": "Venta de producto",
            "reference": "VENTA-001",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movement_type"] == "EXIT"
    assert data["quantity"] == 10
    assert data["previous_quantity"] == 100
    assert data["new_quantity"] == 90


def test_reject_inventory_exit_with_insufficient_stock(client):
    product = create_product(client)

    response = client.post(
        "/api/v1/inventory/exits",
        json={
            "product_id": product["id"],
            "quantity": 10,
            "reason": "Venta sin stock suficiente",
        },
    )

    assert response.status_code == 409

    inventory_response = client.get(
        f"/api/v1/inventory/{product['id']}"
    )

    assert inventory_response.status_code == 200
    assert inventory_response.json()["quantity"] == 0


def test_register_inventory_adjustment(client):
    product = create_product(client)

    client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 100,
            "reason": "Stock inicial",
        },
    )

    response = client.post(
        "/api/v1/inventory/adjustments",
        json={
            "product_id": product["id"],
            "new_quantity": 75,
            "reason": "Conteo físico de inventario",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["movement_type"] == "ADJUSTMENT"
    assert data["previous_quantity"] == 100
    assert data["new_quantity"] == 75
    assert data["quantity"] == 25


def test_inventory_never_becomes_negative(client):
    product = create_product(client)

    client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 5,
            "reason": "Stock inicial",
        },
    )

    response = client.post(
        "/api/v1/inventory/exits",
        json={
            "product_id": product["id"],
            "quantity": 6,
            "reason": "Intento de venta superior al stock",
        },
    )

    assert response.status_code == 409

    inventory_response = client.get(
        f"/api/v1/inventory/{product['id']}"
    )

    assert inventory_response.status_code == 200
    assert inventory_response.json()["quantity"] == 5
    assert inventory_response.json()["quantity"] >= 0
