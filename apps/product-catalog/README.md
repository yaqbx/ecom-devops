# Product Catalog Service - Heavy Equipment E-Commerce

Node.js microservice for managing heavy equipment catalog (excavators, bulldozers, cranes, etc.)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start MongoDB + API
docker-compose up -d

# View logs
docker-compose logs -f product-catalog

# Stop
docker-compose down
```

### Option 2: Local Development

```bash
# 1. Install dependencies
npm install

# 2. Copy environment file
cp .env.example .env

# 3. Start MongoDB locally (or use Docker)
docker run -d -p 27017:27017 --name mongodb mongo:7

# 4. Start the app
npm run dev
```

## Test the API

Once running, test these endpoints:

```bash
# Health check
curl http://localhost:3000/health

# List categories
curl http://localhost:3000/api/v1/categories

# Search equipment
curl "http://localhost:3000/api/v1/search?category=excavators&minPrice=100"

# Get all equipment
curl http://localhost:3000/api/v1/equipment

# Create sample equipment
curl -X POST http://localhost:3000/api/v1/equipment \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "EXC-CAT-320-001",
    "name": "Caterpillar 320 Hydraulic Excavator",
    "description": "20-ton hydraulic excavator with advanced hydraulics",
    "category": "excavators",
    "manufacturer": "Caterpillar",
    "model": "320",
    "year": 2023,
    "condition": "new",
    "specifications": {
      "weight": 20000,
      "height": 3050,
      "width": 2990,
      "length": 9460,
      "power": 128,
      "fuelType": "diesel",
      "maxLiftCapacity": 5000
    },
    "pricing": {
      "dailyRate": 450,
      "weeklyRate": 2500,
      "monthlyRate": 8500,
      "currency": "USD"
    },
    "availability": [{
      "status": "available",
      "location": {
        "city": "Warsaw",
        "region": "Masovia"
      }
    }],
    "images": [{"url": "https://example.com/cat320.jpg", "isPrimary": true}]
  }'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/categories` | List equipment categories |
| GET | `/api/v1/equipment` | List all equipment (with filters) |
| POST | `/api/v1/equipment` | Create new equipment |
| GET | `/api/v1/equipment/:id` | Get equipment by ID |
| GET | `/api/v1/equipment/:id/availability` | Check availability |
| PUT | `/api/v1/equipment/:id` | Update equipment |
| DELETE | `/api/v1/equipment/:id` | Delete equipment |
| GET | `/api/v1/search?q=excavator` | Search with text + filters |

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3000 | Server port |
| `MONGODB_URI` | mongodb://localhost... | MongoDB connection |
| `ALLOWED_ORIGINS` | http://localhost:3000 | CORS origins |

## Architecture

- **Node.js 20** with Express
- **MongoDB** for flexible equipment schema
- **Helmet** for security headers
- **Rate limiting** (100 req/15min)
- **Winston** logging to files
- **Multi-stage Docker** build
- **Kubernetes probes** (health, ready, live)
