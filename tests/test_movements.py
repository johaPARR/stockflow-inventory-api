
def create_product(client):
    category_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Electrónica",
            "description": "Productos electrónicos",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "MOV-001",
            "name": "Mouse inalámbrico",
            "description": "Producto para pruebas de movimientos",
            "price": 25000,
            "category_id": category_id,
        },
    )

    assert product_response.status_code == 201
    return product_response.json()


def test_get_movements(client):
    product = create_product(client)

    client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 50,
            "reason": "Stock inicial",
            "reference": "COMPRA-001",
        },
    )

    client.post(
        "/api/v1/inventory/exits",
        json={
            "product_id": product["id"],
            "quantity": 5,
            "reason": "Venta de producto",
            "reference": "VENTA-001",
        },
    )

    response = client.get("/api/v1/movements")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {movement["movement_type"] for movement in data} == {"ENTRY", "EXIT"}


def test_get_movements_by_product(client):
    product = create_product(client)

    client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product["id"],
            "quantity": 50,
            "reason": "Stock inicial",
        },
    )

    client.post(
        "/api/v1/inventory/exits",
        json={
            "product_id": product["id"],
            "quantity": 10,
            "reason": "Venta de producto",
        },
    )

    response = client.get(
        f"/api/v1/movements/product/{product['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    for movement in data:
        assert movement["product_id"] == product["id"]
