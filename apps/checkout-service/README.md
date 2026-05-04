# Checkout Service - Heavy Equipment E-Commerce

FastAPI microservice for B2B checkout, quotes, delivery scheduling, and order management.

## Features

- **Quotes API**: Generate equipment rental quotes with pricing
- **Delivery Scheduling**: Schedule equipment delivery and pickup
- **Order Management**: Track and manage rental orders
- **Redis Caching**: Fast quote and session storage

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn (development)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or run with gunicorn (production-like)
gunicorn src.main:app -k uvicorn.workers.UvicornWorker -w 4
```

### Docker

```bash
# Build image
docker build -t checkout-service .

# Run container
docker run -p 8000:8000 checkout-service
```

## API Endpoints

### Root
- `GET /` - Service information
- `GET /docs` - Interactive API documentation (Swagger)
- `GET /redoc` - Alternative documentation (ReDoc)

### Health
- `GET /health` - Health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### Quotes
- `POST /api/v1/quotes/` - Create a new quote
- `GET /api/v1/quotes/` - List quotes (filter by customer_id, status)
- `GET /api/v1/quotes/{quote_id}` - Get quote details
- `POST /api/v1/quotes/{quote_id}/accept` - Accept quote
- `POST /api/v1/quotes/{quote_id}/reject` - Reject quote

### Delivery
- `GET /api/v1/delivery/windows` - Get available delivery windows
- `POST /api/v1/delivery/schedule` - Schedule delivery
- `GET /api/v1/delivery/schedule/{schedule_id}` - Get schedule
- `POST /api/v1/delivery/schedule/{schedule_id}/status` - Update status
- `POST /api/v1/delivery/calculate-distance` - Calculate delivery cost

### Orders
- `POST /api/v1/orders/` - Create order from quote
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{order_id}` - Get order details
- `POST /api/v1/orders/{order_id}/confirm` - Confirm order
- `POST /api/v1/orders/{order_id}/cancel` - Cancel order
- `GET /api/v1/orders/stats` - Order statistics

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Create a quote
curl -X POST http://localhost:8000/api/v1/quotes/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "customer_type": "company",
    "items": [
      {
        "equipment_id": "EXC-CAT-320",
        "quantity": 2,
        "rental_days": 7,
        "unit_price": 450.00
      }
    ],
    "delivery_required": true,
    "delivery_address": "Construction Site A, Warsaw"
  }'

# Get available delivery windows
curl http://localhost:8000/api/v1/delivery/windows

# Schedule delivery
curl -X POST http://localhost:8000/api/v1/delivery/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "quote_id": "QT-12345678",
    "equipment_ids": ["EXC-CAT-320"],
    "delivery_postal_code": "00-001",
    "preferred_date": "2024-05-01"
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `WORKERS` | 4 | Number of worker processes |
| `REDIS_HOST` | redis | Redis server host |
| `REDIS_PORT` | 6379 | Redis server port |
| `REDIS_DB` | 0 | Redis database number |
| `SECRET_KEY` | - | JWT secret key |
| `ALGORITHM` | HS256 | JWT algorithm |

## Project Structure

```
checkout-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API routers
│   │   ├── quotes.py
│   │   ├── delivery.py
│   │   └── orders.py
│   ├── services/            # Business logic
│   │   └── redis_client.py
│   └── schemas/             # Pydantic models
├── requirements.txt
├── Dockerfile
└── README.md
```

## Architecture

- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation with type hints
- **Redis**: Caching and session storage
- **Gunicorn + Uvicorn**: Production ASGI server
- **Multi-stage Docker**: Optimized image size
