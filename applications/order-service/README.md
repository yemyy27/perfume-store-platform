# Order Service

Order management and shopping cart microservice that integrates with Product and User services.

## Features
- Shopping cart management
- Order creation and tracking
- Integration with Product Service
- JWT authentication
- Order status tracking

## API Endpoints

### Protected (requires JWT token)
- `POST /api/cart/add` - Add item to cart
- `GET /api/cart` - View cart
- `DELETE /api/cart` - Clear cart
- `POST /api/orders` - Create order from cart
- `GET /api/orders` - Get user's orders
- `GET /api/orders/{id}` - Get specific order

### Public
- `GET /health` - Health check
- `PATCH /api/orders/{id}/status` - Update order status
