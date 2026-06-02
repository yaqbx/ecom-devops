"""
Quotes API - Generate and manage equipment quotes
Persisted in Redis. Fetches real pricing from Product Catalog service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import json
import os
import httpx

from src.services.redis_client import redis_client

router = APIRouter()

PRODUCT_CATALOG_URL = os.getenv("PRODUCT_CATALOG_URL", "http://product-catalog:3000")
USER_MANAGEMENT_URL = os.getenv("USER_MANAGEMENT_URL", "http://user-management:8000")

QUOTE_TTL = 60 * 60 * 24 * 30  # 30 days


class QuoteItem(BaseModel):
    equipment_id: str
    quantity: int = 1
    rental_days: int = 1
    unit_price: float


class QuoteRequest(BaseModel):
    customer_id: str
    customer_type: str = "company"
    items: List[QuoteItem]
    delivery_required: bool = False
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class Quote(BaseModel):
    quote_id: str
    customer_id: str
    customer_type: str
    items: List[QuoteItem]
    subtotal: float
    delivery_fee: float = 0.0
    insurance_fee: float = 0.0
    total: float
    valid_until: datetime
    status: str = "pending"
    created_at: datetime
    delivery_required: bool = False
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


def quote_key(quote_id: str) -> str:
    return f"quote:{quote_id}"


def index_key() -> str:
    return "quotes:index"


async def fetch_equipment_price(equipment_id: str) -> float:
    """Fetch real daily rate from Product Catalog service."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{PRODUCT_CATALOG_URL}/api/v1/equipment/{equipment_id}",
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("pricing", {}).get("dailyRate", 0)
            return 0
    except (httpx.RequestError, httpx.TimeoutException):
        return 0


async def validate_customer(customer_id: str) -> bool:
    """Check if customer exists in User Management service."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{USER_MANAGEMENT_URL}/api/v1/users/{customer_id}/",
                timeout=5.0
            )
            return resp.status_code == 200
    except (httpx.RequestError, httpx.TimeoutException):
        return True


def save_quote(quote: Quote):
    """Save quote to Redis."""
    key = quote_key(quote.quote_id)
    data = quote.model_dump(mode="json")
    if redis_client.set(key, json.dumps(data), ex=QUOTE_TTL):
        redis_client.client.sadd(index_key(), quote.quote_id)


def load_quote(quote_id: str) -> Optional[Quote]:
    """Load quote from Redis."""
    data = redis_client.get(quote_key(quote_id))
    if data is None:
        return None
    return Quote(**json.loads(data))


def list_quotes_from_db(customer_id: Optional[str] = None, status_filter: Optional[str] = None) -> List[Quote]:
    """List quotes from Redis index."""
    ids = redis_client.client.smembers(index_key()) if redis_client.client else set()
    result = []
    for qid in ids:
        quote = load_quote(qid)
        if quote:
            if customer_id and quote.customer_id != customer_id:
                continue
            if status_filter and quote.status != status_filter:
                continue
            result.append(quote)
    result.sort(key=lambda q: q.created_at, reverse=True)
    return result


@router.post("/", response_model=Quote, status_code=status.HTTP_201_CREATED)
async def create_quote(request: QuoteRequest):
    """Generate a new equipment quote with real pricing from Product Catalog."""
    quote_id = f"QT-{uuid.uuid4().hex[:8].upper()}"

    customer_valid = await validate_customer(request.customer_id)

    items = []
    subtotal = 0.0
    for item in request.items:
        real_price = await fetch_equipment_price(item.equipment_id)
        unit_price = real_price if real_price > 0 else item.unit_price

        items.append(QuoteItem(
            equipment_id=item.equipment_id,
            quantity=item.quantity,
            rental_days=item.rental_days,
            unit_price=unit_price,
        ))
        subtotal += unit_price * item.quantity * item.rental_days

    delivery_fee = round(subtotal * 0.10, 2) if request.delivery_required else 0.0
    insurance_fee = round(subtotal * 0.05, 2)
    total = round(subtotal + delivery_fee + insurance_fee, 2)
    valid_until = datetime.now() + timedelta(days=7)

    quote = Quote(
        quote_id=quote_id,
        customer_id=request.customer_id,
        customer_type=request.customer_type,
        items=items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        insurance_fee=insurance_fee,
        total=total,
        valid_until=valid_until,
        delivery_required=request.delivery_required,
        delivery_address=request.delivery_address,
        notes=request.notes,
        created_at=datetime.now(),
    )

    save_quote(quote)

    return quote


@router.get("/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    """Retrieve a quote by ID."""
    quote = load_quote(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    if datetime.now() > quote.valid_until and quote.status == "pending":
        quote.status = "expired"
        save_quote(quote)

    return quote


@router.post("/{quote_id}/accept")
async def accept_quote(quote_id: str):
    """Accept a quote."""
    quote = load_quote(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    if datetime.now() > quote.valid_until:
        quote.status = "expired"
        save_quote(quote)
        raise HTTPException(status_code=400, detail="Quote has expired")

    if quote.status != "pending":
        raise HTTPException(status_code=400, detail=f"Quote is {quote.status}, cannot accept")

    quote.status = "accepted"
    save_quote(quote)

    return {"message": "Quote accepted", "quote_id": quote_id, "status": "accepted"}


@router.post("/{quote_id}/reject")
async def reject_quote(quote_id: str):
    """Reject a quote."""
    quote = load_quote(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    quote.status = "rejected"
    save_quote(quote)

    return {"message": "Quote rejected", "quote_id": quote_id}


@router.get("/", response_model=List[Quote])
async def list_quotes(customer_id: Optional[str] = None, status: Optional[str] = None):
    """List quotes with optional filters."""
    return list_quotes_from_db(customer_id, status)
