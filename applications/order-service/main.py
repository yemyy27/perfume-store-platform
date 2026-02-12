"""
Order Service - Shopping cart and order management
FastAPI microservice that integrates with User and Product services
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uvicorn
import os
import httpx
import jwt

from database import (
    init_db, get_db,
    Order as OrderModel,
    OrderItem as OrderItemModel,
    CartItem as CartItemModel,
)
from sqlalchemy.orm import Session

app = FastAPI(
    title="Order Service",
    description="Order and shopping cart management API",
    version="2.0.0"
)

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8003")

security = HTTPBearer()


# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Pydantic models
class CartItemSchema(BaseModel):
    product_id: int
    quantity: int

class OrderItemSchema(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

class OrderSchema(BaseModel):
    id: int
    user_email: str
    items: List[OrderItemSchema]
    total: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


# Helper functions
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract user email"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_product(product_id: int):
    """Fetch product details from Product Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None


@app.on_event("startup")
def on_startup():
    init_db()


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service", "version": "2.0.0"}

# Add item to cart
@app.post("/api/cart/add")
async def add_to_cart(
    item: CartItemSchema,
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Add item to shopping cart"""
    product = await get_product(item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.get("in_stock"):
        raise HTTPException(status_code=400, detail="Product out of stock")

    # Check if item already in cart
    existing = db.query(CartItemModel).filter(
        CartItemModel.user_email == user_email,
        CartItemModel.product_id == item.product_id,
    ).first()

    if existing:
        existing.quantity += item.quantity
    else:
        cart_item = CartItemModel(
            user_email=user_email,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(cart_item)

    db.commit()

    # Calculate total
    cart_items = db.query(CartItemModel).filter(CartItemModel.user_email == user_email).all()
    total = 0.0
    items_out = []
    for ci in cart_items:
        prod = await get_product(ci.product_id)
        if prod:
            total += prod["price"] * ci.quantity
        items_out.append({"product_id": ci.product_id, "quantity": ci.quantity})

    return {"message": "Item added to cart", "cart": {"items": items_out, "total": total}}

# Get cart
@app.get("/api/cart")
async def get_cart(user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current shopping cart"""
    cart_items = db.query(CartItemModel).filter(CartItemModel.user_email == user_email).all()

    if not cart_items:
        return {"items": [], "total": 0.0}

    total = 0.0
    items = []
    for ci in cart_items:
        prod = await get_product(ci.product_id)
        if prod:
            total += prod["price"] * ci.quantity
        items.append({"product_id": ci.product_id, "quantity": ci.quantity})

    return {"items": items, "total": total}

# Clear cart
@app.delete("/api/cart")
async def clear_cart(user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Clear shopping cart"""
    db.query(CartItemModel).filter(CartItemModel.user_email == user_email).delete()
    db.commit()
    return {"message": "Cart cleared"}

# Create order from cart
@app.post("/api/orders", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Create order from current cart"""
    cart_items = db.query(CartItemModel).filter(CartItemModel.user_email == user_email).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total = 0.0

    for ci in cart_items:
        product = await get_product(ci.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {ci.product_id} not found")

        if not product.get("in_stock"):
            raise HTTPException(status_code=400, detail=f"Product {product['name']} is out of stock")

        subtotal = product["price"] * ci.quantity
        order_items.append(OrderItemModel(
            product_id=product["id"],
            product_name=product["name"],
            quantity=ci.quantity,
            price=product["price"],
            subtotal=subtotal,
        ))
        total += subtotal

    # Create order
    order = OrderModel(
        user_email=user_email,
        total=total,
        status=OrderStatus.PENDING.value,
    )
    db.add(order)
    db.flush()  # Get the order ID

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    # Clear cart
    db.query(CartItemModel).filter(CartItemModel.user_email == user_email).delete()

    db.commit()
    db.refresh(order)

    return order.to_dict()

# Get user's orders
@app.get("/api/orders", response_model=List[OrderSchema])
async def get_orders(user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get all orders for current user"""
    orders = db.query(OrderModel).filter(OrderModel.user_email == user_email).all()
    return [o.to_dict() for o in orders]

# Get specific order
@app.get("/api/orders/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get specific order details"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    return order.to_dict()

# Update order status
@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, new_status: OrderStatus, db: Session = Depends(get_db)):
    """Update order status"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = new_status.value
    db.commit()
    db.refresh(order)

    return {"message": "Order status updated", "order": order.to_dict()}

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Order Service",
        "version": "2.0.0",
        "status": "running",
        "database": "PostgreSQL" if "postgresql" in os.environ.get("DATABASE_URL", "") else "SQLite",
        "integrations": {
            "product_service": PRODUCT_SERVICE_URL,
            "user_service": USER_SERVICE_URL
        },
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
