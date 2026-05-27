# Database Per Service — Why 3 Databases for 3 Microservices

## The Rule

Each microservice owns its own data. No sharing databases.

## Why Not One Big Database?

| Shared DB | Database per Service |
|-----------|---------------------|
| Single table change can break all 3 services | Change one service's DB, others don't care |
| One service's slow query drowns the DB pool | Each service gets its own connection pool |
| Two services writing to same table = bugs | Each service controls its own schema |
| DB is a single point of failure | One DB goes down, the others still work |

## Our Mapping

| Microservice | Database | Why |
|-------------|----------|-----|
| Product Catalog (Node.js) | MongoDB | Flexible document schema — products have different attributes (size, color, specs) |
| User Management (Django) | PostgreSQL | Relational data — users, orders, addresses need strict tables and ACID |
| Checkout Service (FastAPI) | Redis | Fast cache for carts and sessions — no disk writes needed |

## In Production

Same 3 services, same 3 databases — but managed by AWS:
- MongoDB → DocumentDB or MongoDB Atlas
- PostgreSQL → RDS for PostgreSQL
- Redis → ElastiCache for Redis

No code changes needed. Just update the connection string.

## Key Takeaway

3 services → 3 databases is not overengineering. It is standard microservices architecture. Each database was picked for its service's specific data pattern. You could run everything on Postgres, but you would lose the independence that makes microservices valuable.
