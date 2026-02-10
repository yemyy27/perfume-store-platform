# User Service

FastAPI microservice for user authentication and management with JWT tokens.

## Features
- User registration with password hashing
- JWT-based authentication
- Secure password storage with bcrypt
- Token-based authorization
- User profile management

## API Endpoints

### Public Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Protected Endpoints (requires JWT token)
- `GET /api/users/me` - Get current user profile

### Other
- `GET /health` - Health check
- `GET /api/users` - List all users

## Usage Example

### Register
```bash
curl -X POST https://your-service-url/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST https://your-service-url/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Get Profile (with token)
```bash
curl -X GET https://your-service-url/api/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
