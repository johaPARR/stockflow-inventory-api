
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_movement import (
    InventoryMovement,
    MovementType,
)
from app.models.product import Product
from app.models.processed_webhook import ProcessedWebhook
from app.schemas.webhook_schema import ConfirmedOrderCreate


class OrderAlreadyProcessedError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class InactiveProductError(Exception):
    pass


class InventoryNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


def process_confirmed_order(
    db: Session,
    order_data: ConfirmedOrderCreate,
) -> list[InventoryMovement]:

    try:
        processed_order = ProcessedWebhook(
            order_id=order_data.order_id,
        )
        db.add(processed_order)
        db.flush()

        skus = [item.sku for item in order_data.items]

        products = db.scalars(
            select(Product).where(Product.sku.in_(skus))
        ).all()

        products_by_sku = {
            product.sku: product for product in products
        }

        for item in order_data.items:
            product = products_by_sku.get(item.sku)

            if product is None:
                raise ProductNotFoundError(
                    f"No existe el producto con SKU {item.sku}"
                )

            if not product.is_active:
                raise InactiveProductError(
                    f"El producto {item.sku} está inactivo"
                )

        product_ids = [
            products_by_sku[item.sku].id
            for item in order_data.items
        ]

        inventories = db.scalars(
            select(Inventory)
            .where(Inventory.product_id.in_(product_ids))
            .order_by(Inventory.product_id)
            .with_for_update()
        ).all()

        inventories_by_product = {
            inventory.product_id: inventory
            for inventory in inventories
        }

        for item in order_data.items:
            product = products_by_sku[item.sku]

            if product.id not in inventories_by_product:
                raise InventoryNotFoundError(
                    f"No existe inventario para el SKU {item.sku}"
                )

        for item in order_data.items:
            product = products_by_sku[item.sku]
            inventory = inventories_by_product[product.id]

            if inventory.quantity < item.quantity:
                raise InsufficientStockError(
                    f"Stock insuficiente para el SKU {item.sku}. "
                    f"Disponible: {inventory.quantity}. "
                    f"Solicitado: {item.quantity}."
                )

        movements = []

        for item in order_data.items:
            product = products_by_sku[item.sku]
            inventory = inventories_by_product[product.id]

            previous_quantity = inventory.quantity
            new_quantity = previous_quantity - item.quantity

            inventory.quantity = new_quantity

            movement = InventoryMovement(
                product_id=product.id,
                movement_type=MovementType.EXIT,
                quantity=item.quantity,
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reason="Orden ecommerce confirmada",
                reference=order_data.order_id,
                notes="Descuento automático mediante webhook",
            )

            db.add(movement)
            movements.append(movement)

        db.commit()

        for movement in movements:
            db.refresh(movement)

        return movements

    except IntegrityError as exc:
        db.rollback()
        raise OrderAlreadyProcessedError(
            "Esta orden ya fue procesada"
        ) from exc

    except Exception:
        db.rollback()
        raise
