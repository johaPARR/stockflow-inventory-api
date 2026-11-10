
def create_category(client, name):
    response = client.post(
        "/api/v1/categories",
        json={
            "name": name,
            "description": "Categoría para pruebas webhook",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_product(client, sku):
    category_id = create_category(client, f"Categoría {sku}")

    response = client.post(
        "/api/v1/products",
        json={
            "sku": sku,
            "name": f"Producto {sku}",
            "description": "Producto para pruebas webhook",
            "price": 50000,
            "category_id": category_id,
        },
    )

    assert response.status_code == 201
    return response.json()


def add_stock(client, product_id, quantity):
    response = client.post(
        "/api/v1/inventory/entries",
        json={
            "product_id": product_id,
            "quantity": quantity,
            "reason": "Stock inicial para pruebas webhook",
        },
    )

    assert response.status_code == 201
    return response.json()


def get_stock(client, product_id):
    response = client.get(
        f"/api/v1/inventory/{product_id}"
    )

    assert response.status_code == 200
    return response.json()["quantity"]


def test_confirmed_order_decreases_stock(client):
    product = create_product(client, "WEB-001")
    add_stock(client, product["id"], 100)

    response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json={
            "order_id": "ORDER-001",
            "items": [
                {
                    "sku": "WEB-001",
                    "quantity": 15,
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["order_id"] == "ORDER-001"
    assert data["status"] == "processed"
    assert data["processed_items"] == 1
    assert len(data["movements"]) == 1

    movement = data["movements"][0]

    assert movement["movement_type"] == "EXIT"
    assert movement["quantity"] == 15
    assert movement["previous_quantity"] == 100
    assert movement["new_quantity"] == 85

    assert get_stock(client, product["id"]) == 85


def test_confirmed_order_cannot_be_processed_twice(client):
    product = create_product(client, "WEB-002")
    add_stock(client, product["id"], 50)

    order = {
        "order_id": "ORDER-002",
        "items": [
            {
                "sku": "WEB-002",
                "quantity": 10,
            }
        ],
    }

    first_response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json=order,
    )

    assert first_response.status_code == 201
    assert get_stock(client, product["id"]) == 40

    second_response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json=order,
    )

    assert second_response.status_code == 409
    assert get_stock(client, product["id"]) == 40


def test_confirmed_order_rejects_unknown_sku(client):
    response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json={
            "order_id": "ORDER-003",
            "items": [
                {
                    "sku": "UNKNOWN-001",
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 404


def test_confirmed_order_rolls_back_when_stock_is_insufficient(client):
    first_product = create_product(client, "WEB-004")
    second_product = create_product(client, "WEB-005")

    add_stock(client, first_product["id"], 100)
    add_stock(client, second_product["id"], 5)

    response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json={
            "order_id": "ORDER-004",
            "items": [
                {
                    "sku": "WEB-004",
                    "quantity": 10,
                },
                {
                    "sku": "WEB-005",
                    "quantity": 20,
                },
            ],
        },
    )

    assert response.status_code == 409

    # No debe haber descuentos parciales.
    assert get_stock(client, first_product["id"]) == 100
    assert get_stock(client, second_product["id"]) == 5


def test_confirmed_order_rejects_duplicate_skus(client):
    response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json={
            "order_id": "ORDER-005",
            "items": [
                {
                    "sku": "WEB-006",
                    "quantity": 2,
                },
                {
                    "sku": "WEB-006",
                    "quantity": 3,
                },
            ],
        },
    )

    assert response.status_code == 422


def test_confirmed_order_rejects_inactive_product(client):
    product = create_product(client, "WEB-007")
    add_stock(client, product["id"], 20)

    deactivate_response = client.patch(
        f"/api/v1/products/{product['id']}",
        json={
            "is_active": False,
        },
    )

    assert deactivate_response.status_code == 200

    response = client.post(
        "/api/v1/webhooks/orders/confirmed",
        json={
            "order_id": "ORDER-006",
            "items": [
                {
                    "sku": "WEB-007",
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 409
    assert get_stock(client, product["id"]) == 20

