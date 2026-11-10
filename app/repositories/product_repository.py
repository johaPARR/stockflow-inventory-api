from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate


def create_product(
    db: Session,
    product_data: ProductCreate,
) -> Product:
    product = Product(**product_data.model_dump())

    db.add(product)
    db.flush()

    return product


def get_product_by_id(
    db: Session,
    product_id: int,
) -> Product | None:
    return db.get(Product, product_id)


def get_product_by_sku(
    db: Session,
    sku: str,
) -> Product | None:
    statement = select(Product).where(Product.sku == sku)

    return db.scalar(statement)


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Product]:
    statement = (
        select(Product)
        .order_by(Product.id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def update_product(
    db: Session,
    product: Product,
    product_data: ProductUpdate,
) -> Product:
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.flush()

    return product