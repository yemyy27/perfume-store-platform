.PHONY: dev dev-docker dev-down test-api clean help

# Default target
help:
	@echo "Perfume Store Platform - Local Development Commands"
	@echo ""
	@echo "  make dev          Start all services locally (Python, no Docker)"
	@echo "  make dev-docker   Start all services via Docker Compose"
	@echo "  make test-api     Run API smoke tests against local services"
	@echo "  make clean        Remove virtual environment and cached files"
	@echo ""

# Start all services with Python directly
dev:
	./scripts/local-dev.sh

# Start all services via Docker Compose (requires Docker)
dev-docker:
	cd infrastructure/docker && docker compose up -d --build
	@echo ""
	@echo "  Frontend:         http://localhost:8080"
	@echo "  Product Service:  http://localhost:8001  (docs: http://localhost:8001/docs)"
	@echo "  Order Service:    http://localhost:8002  (docs: http://localhost:8002/docs)"
	@echo "  User Service:     http://localhost:8003  (docs: http://localhost:8003/docs)"

# Stop Docker services
dev-down:
	cd infrastructure/docker && docker compose down

# Run smoke tests against local stack
test-api:
	@echo "=== Health Checks ==="
	@curl -sf http://localhost:8001/health && echo " <- product-service OK" || echo " <- product-service FAILED"
	@curl -sf http://localhost:8002/health && echo " <- order-service OK" || echo " <- order-service FAILED"
	@curl -sf http://localhost:8003/health && echo " <- user-service OK" || echo " <- user-service FAILED"
	@curl -sf -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q 200 && echo "200 <- frontend OK" || echo " <- frontend FAILED"
	@echo ""
	@echo "=== Product Endpoints ==="
	@curl -sf http://localhost:8001/api/products | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} products loaded')" || echo "FAILED"
	@curl -sf http://localhost:8001/api/products/1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Product: {d[\"name\"]} - \$${d[\"price\"]}')" || echo "FAILED"
	@echo ""
	@echo "=== User Registration & Login ==="
	@curl -sf -X POST http://localhost:8003/api/auth/register \
		-H "Content-Type: application/json" \
		-d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}' \
		| python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Registered: {d[\"email\"]}')" || echo "Registration failed (user may already exist)"
	@echo ""
	@TOKEN=$$(curl -sf -X POST http://localhost:8003/api/auth/login \
		-H "Content-Type: application/json" \
		-d '{"email":"test@example.com","password":"testpass123"}' \
		| python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])") && \
		echo "Login OK - token obtained" && \
		echo "" && \
		echo "=== Cart & Order Flow ===" && \
		curl -sf -X POST http://localhost:8002/api/cart/add \
			-H "Content-Type: application/json" \
			-H "Authorization: Bearer $$TOKEN" \
			-d '{"product_id":1,"quantity":2}' \
			| python3 -c "import sys,json; print(f'Added to cart: {json.load(sys.stdin)[\"message\"]}')" && \
		curl -sf http://localhost:8002/api/cart \
			-H "Authorization: Bearer $$TOKEN" \
			| python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Cart total: \$${d[\"total\"]}')" && \
		curl -sf -X POST http://localhost:8002/api/orders \
			-H "Content-Type: application/json" \
			-H "Authorization: Bearer $$TOKEN" \
			| python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Order #{d[\"id\"]} created - \$${d[\"total\"]} - Status: {d[\"status\"]}')" \
		|| echo "Cart/Order flow FAILED"
	@echo ""
	@echo "=== All tests complete ==="

# Remove venv and cached files
clean:
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
