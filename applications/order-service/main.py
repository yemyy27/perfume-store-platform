"""
Order Service - Shopping cart and order management
FastAPI microservice that integrates with User and Product services
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uvicorn
import os
import httpx
import jwt

app = FastAPI(
    title="Order Service",
    description="Order and shopping cart management API",
    version="1.0.0"
)

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "https://product-service-392366394996.us-central1.run.app")
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "https://user-service-392366394996.us-central1.run.app")

security = HTTPBearer()

# Mock database
orders_db = []
carts_db = {}

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Pydantic models
class CartItem(BaseModel):
    product_id: int
    quantity: int

class Cart(BaseModel):
    user_email: str
    items: List[CartItem]
    total: float = 0.0

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

class CreateOrder(BaseModel):
    items: List[CartItem]

class Order(BaseModel):
    id: int
    user_email: str
    items: List[OrderItem]
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

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-service"}

# Add item to cart
@app.post("/api/cart/add")
async def add_to_cart(item: CartItem, user_email: str = Depends(verify_token)):
    """Add item to shopping cart"""
    # Verify product exists
    product = await get_product(item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.get("in_stock"):
        raise HTTPException(status_code=400, detail="Product out of stock")
    
    # Initialize cart if doesn't exist
    if user_email not in carts_db:
        carts_db[user_email] = {"items": [], "total": 0.0}
    
    # Check if item already in cart
    cart = carts_db[user_email]
    existing_item = next((i for i in cart["items"] if i["product_id"] == item.product_id), None)
    
    if existing_item:
        existing_item["quantity"] += item.quantity
    else:
        cart["items"].append({"product_id": item.product_id, "quantity": item.quantity})
    
    # Recalculate total
    total = 0.0
    for cart_item in cart["items"]:
        prod = await get_product(cart_item["product_id"])
        if prod:
            total += prod["price"] * cart_item["quantity"]
    
    cart["total"] = total
    
    return {"message": "Item added to cart", "cart": cart}

# Get cart
@app.get("/api/cart")
async def get_cart(user_email: str = Depends(verify_token)):
    """Get current shopping cart"""
    if user_email not in carts_db:
        return {"items": [], "total": 0.0}
    
    return carts_db[user_email]

# Clear cart
@app.delete("/api/cart")
async def clear_cart(user_email: str = Depends(verify_token)):
    """Clear shopping cart"""
    if user_email in carts_db:
        del carts_db[user_email]
    return {"message": "Cart cleared"}

# Create order from cart
@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(user_email: str = Depends(verify_token)):
    """Create order from current cart"""
    if user_email not in carts_db or not carts_db[user_email]["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = carts_db[user_email]
    order_items = []
    total = 0.0
    
    # Build order items with product details
    for cart_item in cart["items"]:
        product = await get_product(cart_item["product_id"])
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {cart_item['product_id']} not found")
        
        if not product.get("in_stock"):
            raise HTTPException(status_code=400, detail=f"Product {product['name']} is out of stock")
        
        subtotal = product["price"] * cart_item["quantity"]
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": cart_item["quantity"],
            "price": product["price"],
            "subtotal": subtotal
        })
        total += subtotal
    
    # Create order
    order = {
        "id": len(orders_db) + 1,
        "user_email": user_email,
        "items": order_items,
        "total": total,
        "status": OrderStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    orders_db.append(order)
    
    # Clear cart
    del carts_db[user_email]
    
    return order

# Get user's orders
@app.get("/api/orders", response_model=List[Order])
async def get_orders(user_email: str = Depends(verify_token)):
    """Get all orders for current user"""
    user_orders = [order for order in orders_db if order["user_email"] == user_email]
    return user_orders

# Get specific order
@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: int, user_email: str = Depends(verify_token)):
    """Get specific order details"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

# Update order status (admin function - simplified for now)
@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: OrderStatus):
    """Update order status"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["status"] = status
    order["updated_at"] = datetime.utcnow()
    
    return {"message": "Order status updated", "order": order}

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Order Service",
        "version": "1.0.0",
        "status": "running",
        "integrations": {
            "product_service": PRODUCT_SERVICE_URL,
            "user_service": USER_SERVICE_URL
        },
        "endpoints": {
            "health": "/health",
            "add_to_cart": "/api/cart/add",
            "view_cart": "/api/cart",
            "create_order": "/api/orders",
            "my_orders": "/api/orders"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
