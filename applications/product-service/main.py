from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="Product Service", version="2.0.0")

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced product database with realistic perfumes
products = [
    {
        "id": 1,
        "name": "Midnight Rose",
        "brand": "Luxury Scents",
        "description": "A luxurious floral scent with notes of rose and jasmine",
        "scent_profile": ["Floral", "Romantic", "Evening"],
        "top_notes": ["Bergamot", "Pink Pepper"],
        "heart_notes": ["Rose", "Jasmine", "Peony"],
        "base_notes": ["Musk", "Vanilla", "Sandalwood"],
        "price": 89.99,
        "original_price": 120.00,
        "category": "women",
        "size_ml": 50,
        "in_stock": True,
        "stock_quantity": 45,
        "rating": 4.8,
        "review_count": 234,
        "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400",
        "is_new": True,
        "is_bestseller": True,
        "gender": "women"
    },
    {
        "id": 2,
        "name": "Ocean Breeze",
        "brand": "Azure Collection",
        "description": "Fresh aquatic cologne with citrus undertones",
        "scent_profile": ["Fresh", "Aquatic", "Daytime"],
        "top_notes": ["Lemon", "Marine Notes", "Mint"],
        "heart_notes": ["Lavender", "Geranium"],
        "base_notes": ["Cedar", "Amber", "Musk"],
        "price": 75.50,
        "original_price": 95.00,
        "category": "men",
        "size_ml": 100,
        "in_stock": True,
        "stock_quantity": 32,
        "rating": 4.6,
        "review_count": 189,
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
        "is_new": False,
        "is_bestseller": True,
        "gender": "men"
    },
    {
        "id": 3,
        "name": "Vanilla Dreams",
        "brand": "Sweet Essence",
        "description": "Warm and sweet vanilla-based fragrance",
        "scent_profile": ["Sweet", "Warm", "Cozy"],
        "top_notes": ["Vanilla", "Caramel"],
        "heart_notes": ["Tonka Bean", "Almond"],
        "base_notes": ["Vanilla", "Benzoin", "Praline"],
        "price": 65.00,
        "original_price": 65.00,
        "category": "women",
        "size_ml": 75,
        "in_stock": False,
        "stock_quantity": 0,
        "rating": 4.9,
        "review_count": 445,
        "image_url": "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=400",
        "is_new": False,
        "is_bestseller": True,
        "gender": "women"
    },
    {
        "id": 4,
        "name": "Noir Intensity",
        "brand": "Elite Pour Homme",
        "description": "Bold and mysterious cologne for confident men",
        "scent_profile": ["Woody", "Spicy", "Evening"],
        "top_notes": ["Black Pepper", "Cardamom", "Bergamot"],
        "heart_notes": ["Leather", "Iris", "Patchouli"],
        "base_notes": ["Oud", "Vetiver", "Amber"],
        "price": 125.00,
        "original_price": 125.00,
        "category": "men",
        "size_ml": 100,
        "in_stock": True,
        "stock_quantity": 18,
        "rating": 4.7,
        "review_count": 156,
        "image_url": "https://images.unsplash.com/photo-1585838434261-763133d12f5c?w=400",
        "is_new": True,
        "is_bestseller": False,
        "gender": "men"
    },
    {
        "id": 5,
        "name": "Citrus Bliss",
        "brand": "Fresh Collection",
        "description": "Energizing citrus blend perfect for any occasion",
        "scent_profile": ["Citrus", "Fresh", "Energizing"],
        "top_notes": ["Grapefruit", "Orange", "Lemon"],
        "heart_notes": ["Neroli", "Orange Blossom"],
        "base_notes": ["White Musk", "Vetiver"],
        "price": 55.00,
        "original_price": 75.00,
        "category": "unisex",
        "size_ml": 50,
        "in_stock": True,
        "stock_quantity": 67,
        "rating": 4.5,
        "review_count": 98,
        "image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
        "is_new": False,
        "is_bestseller": False,
        "gender": "unisex"
    },
    {
        "id": 6,
        "name": "Amber Nights",
        "brand": "Oriental Mystique",
        "description": "Rich oriental fragrance with warm amber tones",
        "scent_profile": ["Oriental", "Warm", "Sensual"],
        "top_notes": ["Saffron", "Cinnamon"],
        "heart_notes": ["Amber", "Rose", "Jasmine"],
        "base_notes": ["Oud", "Sandalwood", "Patchouli"],
        "price": 98.00,
        "original_price": 98.00,
        "category": "unisex",
        "size_ml": 75,
        "in_stock": True,
        "stock_quantity": 25,
        "rating": 4.8,
        "review_count": 312,
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
        "is_new": True,
        "is_bestseller": True,
        "gender": "unisex"
    }
]

class Product(BaseModel):
    id: int
    name: str
    brand: str
    description: str
    scent_profile: List[str]
    top_notes: List[str]
    heart_notes: List[str]
    base_notes: List[str]
    price: float
    original_price: float
    category: str
    size_ml: int
    in_stock: bool
    stock_quantity: int
    rating: float
    review_count: int
    image_url: str
    is_new: bool
    is_bestseller: bool
    gender: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service", "version": "2.0.0"}

@app.get("/api/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|rating|new)$")
):
    """Get products with advanced filtering and sorting"""
    filtered = products.copy()
    
    # Apply filters
    if category:
        filtered = [p for p in filtered if p["category"] == category]
    if gender:
        filtered = [p for p in filtered if p["gender"] == gender]
    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]
    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]
    if in_stock is not None:
        filtered = [p for p in filtered if p["in_stock"] == in_stock]
    
    # Apply sorting
    if sort_by == "price_asc":
        filtered.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        filtered.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        filtered.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "new":
        filtered.sort(key=lambda x: x["is_new"], reverse=True)
    
    return filtered

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get single product details"""
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/products/featured/bestsellers", response_model=List[Product])
async def get_bestsellers(limit: int = 4):
    """Get bestselling products"""
    bestsellers = [p for p in products if p["is_bestseller"]]
    return bestsellers[:limit]

@app.get("/api/products/featured/new", response_model=List[Product])
async def get_new_arrivals(limit: int = 4):
    """Get new arrival products"""
    new_products = [p for p in products if p["is_new"]]
    return new_products[:limit]

@app.get("/api/brands")
async def get_brands():
    """Get all unique brands"""
    brands = list(set(p["brand"] for p in products))
    return {"brands": sorted(brands)}

@app.get("/")
async def root():
    return {
        "service": "Product Service",
        "version": "2.0.0",
        "products_count": len(products),
        "features": ["filtering", "sorting", "search", "bestsellers", "new_arrivals"]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
