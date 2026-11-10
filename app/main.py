
from fastapi import FastAPI

from app.api.v1 import (
    category_routes,
    product_routes,
    inventory_routes,
    movement_routes,
    webhook_routes,
)


app = FastAPI(
    title="StockFlow API",
    description=(
        "Inventory Management & Ecommerce Integration API. "
        "REST API for product management, stock control "
        "and ecommerce integrations."
    ),
    version="1.0.0",
)


app.include_router(category_routes.router, prefix="/api/v1")
app.include_router(product_routes.router, prefix="/api/v1")
app.include_router(inventory_routes.router, prefix="/api/v1")
app.include_router(movement_routes.router, prefix="/api/v1")
app.include_router(webhook_routes.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "StockFlow API",
    }
