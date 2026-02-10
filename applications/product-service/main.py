"""
Product Service - Manages product catalog
FastAPI microservice for the perfume e-commerce platform
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

app = FastAPI(
    title="Product Service",
    description="Product catalog management API",
    version="1.0.0"
)

# Mock data (we'll connect to database later)
products = [
    {
        "id": 1,
        "name": "Midnight Rose",
        "description": "A luxurious floral scent with notes of rose and jasmine",
        "price": 89.99,
        "category": "perfume",
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Ocean Breeze",
        "description": "Fresh aquatic cologne with citrus undertones",
        "price": 75.50,
        "category": "cologne",
        "in_stock": True
    },
    {
        "id": 3,
        "name": "Vanilla Dreams",
        "description": "Warm and sweet vanilla-based fragrance",
        "price": 65.00,
        "category": "perfume",
        "in_stock": False
    }
]

# Pydantic models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    in_stock: bool

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "product-service"}

# Get all products
@app.get("/api/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Get all products, optionally filtered by category"""
    if category:
        filtered = [p for p in products if p["category"] == category]
        return filtered
    return products

# Get single product
@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID"""
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Product Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "products": "/api/products",
            "product_detail": "/api/products/{id}"
        }
    }

if __name__ == "__main__":
    # Cloud Run provides PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
