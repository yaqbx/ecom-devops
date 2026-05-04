# User Management Service - Heavy Equipment E-Commerce

Django microservice for B2B user management, company profiles, and rental history.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start PostgreSQL + Redis + Django
docker-compose up -d

# Wait for services to start (10 seconds)
sleep 10

# Create superuser
docker-compose exec user-management python manage.py createsuperuser

# View logs
docker-compose logs -f user-management

# Stop
docker-compose down
```

### Option 2: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
cp .env.example .env

# 3. Start PostgreSQL locally
docker run -d -p 5432:5432 -e POSTGRES_DB=user_management -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres:15

# 4. Start Redis
docker run -d -p 6379:6379 redis:7

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

## Test the API

```bash
# Health check
curl http://localhost:8000/health/

# Create user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@construction.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+48 123 456 789",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "customer"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@construction.com",
    "password": "securepassword123"
  }'

# List users (admin only)
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get user stats (admin only)
curl http://localhost:8000/api/v1/users/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/` | Create user |
| POST | `/api/v1/users/login/` | Login |
| GET | `/api/v1/users/me/` | Current user profile |
| GET | `/api/v1/users/` | List users (admin) |
| GET | `/api/v1/users/{id}/` | Get user details |
| PATCH | `/api/v1/users/{id}/` | Update user |
| DELETE | `/api/v1/users/{id}/` | Delete user |
| POST | `/api/v1/users/{id}/change_password/` | Change password |
| PATCH | `/api/v1/users/{id}/update_role/` | Update role (admin) |
| GET | `/api/v1/users/stats/` | User statistics |
| GET | `/health/` | Health check |

## User Roles

| Role | Description |
|------|-------------|
| `admin` | Platform administrator |
| `company_admin` | Company admin - manages company users |
| `company_manager` | Company manager - can rent equipment |
| `company_operator` | Equipment operator |
| `customer` | Individual customer |

## Admin Panel

Access Django admin at `http://localhost:8000/admin/`

## Features

- **Email-based authentication** (no username)
- **B2B support** - Users linked to companies
- **Role-based access control**
- **Account verification workflow**
- **Login security** - Failed attempt tracking, account locking
- **Full CRUD** via REST API
- **Health checks** for Kubernetes
