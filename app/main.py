from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    description="Inventory Management & Ecommerce Integration API",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "StockFlow API",
    }
