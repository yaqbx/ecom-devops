"""
Checkout Service - Heavy Equipment E-Commerce
Handles quotes, delivery scheduling, and high-value transactions
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import redis
import json
import os

from .api import quotes, delivery, orders

__version__ = "1.0.0"

app = FastAPI(
    title="Heavy Equipment Checkout Service",
    description="B2B checkout service for equipment quotes, delivery scheduling, and transactions",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .services.redis_client import redis_client as shared_redis
shared_redis.initialize(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(delivery.router, prefix="/api/v1/delivery", tags=["Delivery"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])


@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "checkout-service",
        "version": __version__,
        "description": "Heavy Equipment B2B Checkout Service",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "quotes": "/api/v1/quotes",
            "delivery": "/api/v1/delivery",
            "orders": "/api/v1/orders"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    try:
        shared_redis.client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "checkout-service",
        "version": __version__,
        "checks": {
            "redis": redis_status,
            "memory": "ok"
        }
    }


@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        shared_redis.client.ping()
        return {"ready": True, "status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"alive": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )
