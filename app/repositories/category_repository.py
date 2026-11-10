from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


def create_category(
    db: Session,
    category_data: CategoryCreate,
) -> Category:
    category = Category(**category_data.model_dump())

    db.add(category)
    db.flush()

    return category


def get_category_by_id(
    db: Session,
    category_id: int,
) -> Category | None:
    return db.get(Category, category_id)


def get_category_by_name(
    db: Session,
    name: str,
) -> Category | None:
    statement = select(Category).where(Category.name == name)

    return db.scalar(statement)


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Category]:
    statement = (
        select(Category)
        .order_by(Category.id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def update_category(
    db: Session,
    category: Category,
    category_data: CategoryUpdate,
) -> Category:
    update_data = category_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(category, field, value)

    db.flush()

    return category