# Product Service

FastAPI microservice for managing the product catalog in the perfume e-commerce platform.

## Features
- List all products
- Filter products by category
- Get individual product details
- Health check endpoint for monitoring

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /api/products` - List all products
- `GET /api/products?category=perfume` - Filter by category
- `GET /api/products/{id}` - Get specific product

## Deploy to Cloud Run
```bash
gcloud run deploy product-service --source .
```
