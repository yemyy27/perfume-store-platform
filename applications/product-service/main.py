from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uvicorn
import os

from database import init_db, get_db, Product as ProductModel
from sqlalchemy.orm import Session

app = FastAPI(title="Product Service", version="3.0.0")

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Seed data for initial products
SEED_PRODUCTS = [
    {
        "name": "Midnight Rose", "brand": "Luxury Scents",
        "description": "A luxurious floral scent with notes of rose and jasmine",
        "scent_profile": ["Floral", "Romantic", "Evening"],
        "top_notes": ["Bergamot", "Pink Pepper"],
        "heart_notes": ["Rose", "Jasmine", "Peony"],
        "base_notes": ["Musk", "Vanilla", "Sandalwood"],
        "price": 89.99, "original_price": 120.00, "category": "women",
        "size_ml": 50, "in_stock": True, "stock_quantity": 45,
        "rating": 4.8, "review_count": 234,
        "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400",
        "is_new": True, "is_bestseller": True, "gender": "women"
    },
    {
        "name": "Ocean Breeze", "brand": "Azure Collection",
        "description": "Fresh aquatic cologne with citrus undertones",
        "scent_profile": ["Fresh", "Aquatic", "Daytime"],
        "top_notes": ["Lemon", "Marine Notes", "Mint"],
        "heart_notes": ["Lavender", "Geranium"],
        "base_notes": ["Cedar", "Amber", "Musk"],
        "price": 75.50, "original_price": 95.00, "category": "men",
        "size_ml": 100, "in_stock": True, "stock_quantity": 32,
        "rating": 4.6, "review_count": 189,
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
        "is_new": False, "is_bestseller": True, "gender": "men"
    },
    {
        "name": "Vanilla Dreams", "brand": "Sweet Essence",
        "description": "Warm and sweet vanilla-based fragrance",
        "scent_profile": ["Sweet", "Warm", "Cozy"],
        "top_notes": ["Vanilla", "Caramel"],
        "heart_notes": ["Tonka Bean", "Almond"],
        "base_notes": ["Vanilla", "Benzoin", "Praline"],
        "price": 65.00, "original_price": 65.00, "category": "women",
        "size_ml": 75, "in_stock": False, "stock_quantity": 0,
        "rating": 4.9, "review_count": 445,
        "image_url": "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=400",
        "is_new": False, "is_bestseller": True, "gender": "women"
    },
    {
        "name": "Noir Intensity", "brand": "Elite Pour Homme",
        "description": "Bold and mysterious cologne for confident men",
        "scent_profile": ["Woody", "Spicy", "Evening"],
        "top_notes": ["Black Pepper", "Cardamom", "Bergamot"],
        "heart_notes": ["Leather", "Iris", "Patchouli"],
        "base_notes": ["Oud", "Vetiver", "Amber"],
        "price": 125.00, "original_price": 125.00, "category": "men",
        "size_ml": 100, "in_stock": True, "stock_quantity": 18,
        "rating": 4.7, "review_count": 156,
        "image_url": "https://images.unsplash.com/photo-1585838434261-763133d12f5c?w=400",
        "is_new": True, "is_bestseller": False, "gender": "men"
    },
    {
        "name": "Citrus Bliss", "brand": "Fresh Collection",
        "description": "Energizing citrus blend perfect for any occasion",
        "scent_profile": ["Citrus", "Fresh", "Energizing"],
        "top_notes": ["Grapefruit", "Orange", "Lemon"],
        "heart_notes": ["Neroli", "Orange Blossom"],
        "base_notes": ["White Musk", "Vetiver"],
        "price": 55.00, "original_price": 75.00, "category": "unisex",
        "size_ml": 50, "in_stock": True, "stock_quantity": 67,
        "rating": 4.5, "review_count": 98,
        "image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
        "is_new": False, "is_bestseller": False, "gender": "unisex"
    },
    {
        "name": "Amber Nights", "brand": "Oriental Mystique",
        "description": "Rich oriental fragrance with warm amber tones",
        "scent_profile": ["Oriental", "Warm", "Sensual"],
        "top_notes": ["Saffron", "Cinnamon"],
        "heart_notes": ["Amber", "Rose", "Jasmine"],
        "base_notes": ["Oud", "Sandalwood", "Patchouli"],
        "price": 98.00, "original_price": 98.00, "category": "unisex",
        "size_ml": 75, "in_stock": True, "stock_quantity": 25,
        "rating": 4.8, "review_count": 312,
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
        "is_new": True, "is_bestseller": True, "gender": "unisex"
    },
]


@app.on_event("startup")
def on_startup():
    init_db()
    # Seed products if table is empty
    db = next(get_db())
    try:
        if db.query(ProductModel).count() == 0:
            for p in SEED_PRODUCTS:
                product = ProductModel(
                    name=p["name"], brand=p["brand"], description=p["description"],
                    scent_profile=json.dumps(p["scent_profile"]),
                    top_notes=json.dumps(p["top_notes"]),
                    heart_notes=json.dumps(p["heart_notes"]),
                    base_notes=json.dumps(p["base_notes"]),
                    price=p["price"], original_price=p["original_price"],
                    category=p["category"], size_ml=p["size_ml"],
                    in_stock=p["in_stock"], stock_quantity=p["stock_quantity"],
                    rating=p["rating"], review_count=p["review_count"],
                    image_url=p["image_url"], is_new=p["is_new"],
                    is_bestseller=p["is_bestseller"], gender=p["gender"],
                )
                db.add(product)
            db.commit()
            print(f"Seeded {len(SEED_PRODUCTS)} products into database")
    finally:
        db.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service", "version": "3.0.0"}


@app.get("/api/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|rating|new)$"),
    db: Session = Depends(get_db),
):
    """Get products with advanced filtering and sorting"""
    query = db.query(ProductModel)

    if category:
        query = query.filter(ProductModel.category == category)
    if gender:
        query = query.filter(ProductModel.gender == gender)
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    if in_stock is not None:
        query = query.filter(ProductModel.in_stock == in_stock)

    if sort_by == "price_asc":
        query = query.order_by(ProductModel.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(ProductModel.price.desc())
    elif sort_by == "rating":
        query = query.order_by(ProductModel.rating.desc())
    elif sort_by == "new":
        query = query.order_by(ProductModel.is_new.desc())

    products = query.all()
    return [p.to_dict() for p in products]


@app.get("/api/products/featured/bestsellers", response_model=List[Product])
async def get_bestsellers(limit: int = 4, db: Session = Depends(get_db)):
    """Get bestselling products"""
    products = db.query(ProductModel).filter(ProductModel.is_bestseller == True).limit(limit).all()
    return [p.to_dict() for p in products]


@app.get("/api/products/featured/new", response_model=List[Product])
async def get_new_arrivals(limit: int = 4, db: Session = Depends(get_db)):
    """Get new arrival products"""
    products = db.query(ProductModel).filter(ProductModel.is_new == True).limit(limit).all()
    return [p.to_dict() for p in products]


@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product details"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict()


@app.get("/api/brands")
async def get_brands(db: Session = Depends(get_db)):
    """Get all unique brands"""
    brands = [row[0] for row in db.query(ProductModel.brand).distinct().all()]
    return {"brands": sorted(brands)}


@app.get("/")
async def root(db: Session = Depends(get_db)):
    count = db.query(ProductModel).count()
    return {
        "service": "Product Service",
        "version": "3.0.0",
        "products_count": count,
        "features": ["filtering", "sorting", "search", "bestsellers", "new_arrivals"],
        "database": "PostgreSQL" if "postgresql" in os.environ.get("DATABASE_URL", "") else "SQLite",
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
