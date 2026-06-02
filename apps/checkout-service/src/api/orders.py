"""
Orders API - Process and track equipment rental orders
Persisted in Redis. Integrates with mock payment service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import json
import os
import httpx

from src.services.redis_client import redis_client
from .quotes import load_quote, QuoteItem

router = APIRouter()

PAYMENT_MOCK_URL = os.getenv("PAYMENT_MOCK_URL", "http://payment-mock:8100")
ORDER_TTL = 60 * 60 * 24 * 90

ORDER_STATUSES = ["pending", "confirmed", "active", "completed", "cancelled"]


class OrderItem(BaseModel):
    equipment_id: str
    equipment_name: str
    quantity: int
    rental_days: int
    unit_price: float
    total_price: float


class Order(BaseModel):
    order_id: str
    quote_id: str
    customer_id: str
    customer_type: str
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    insurance_fee: float
    total: float
    payment_id: Optional[str] = None
    status: str = "pending"
    payment_status: str = "pending"
    delivery_schedule_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


def order_key(order_id: str) -> str:
    return f"order:{order_id}"


def index_key() -> str:
    return "orders:index"


def save_order(order: Order):
    key = order_key(order.order_id)
    data = order.model_dump(mode="json")
    if redis_client.set(key, json.dumps(data), ex=ORDER_TTL):
        redis_client.client.sadd(index_key(), order.order_id)


def load_order(order_id: str) -> Optional[Order]:
    data = redis_client.get(order_key(order_id))
    if data is None:
        return None
    return Order(**json.loads(data))


def list_orders_from_db(customer_id: Optional[str] = None, status_filter: Optional[str] = None) -> List[Order]:
    ids = redis_client.client.smembers(index_key()) if redis_client.client else set()
    result = []
    for oid in ids:
        order = load_order(oid)
        if order:
            if customer_id and order.customer_id != customer_id:
                continue
            if status_filter and order.status != status_filter:
                continue
            result.append(order)
    result.sort(key=lambda o: o.created_at, reverse=True)
    return result


async def fetch_equipment_name(equipment_id: str) -> str:
    """Fetch equipment name from Product Catalog."""
    product_url = os.getenv("PRODUCT_CATALOG_URL", "http://product-catalog:3000")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{product_url}/api/v1/equipment/{equipment_id}",
                timeout=5.0,
            )
            if resp.status_code == 200:
                return resp.json().get("name", equipment_id)
    except (httpx.RequestError, httpx.TimeoutException):
        pass
    return equipment_id


async def authorize_payment(amount: float, customer_id: str) -> tuple[Optional[str], Optional[str]]:
    """Call mock payment service to authorize payment."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{PAYMENT_MOCK_URL}/api/v1/payments/authorize",
                json={
                    "amount": round(amount, 2),
                    "currency": "USD",
                    "card_token": "4242424242424242",
                    "description": f"Order payment for customer {customer_id}",
                    "metadata": {"customer_id": customer_id},
                },
                timeout=10.0,
            )
            if resp.status_code == 201:
                data = resp.json()
                return data["payment_id"], None
            return None, "payment_failed"
    except (httpx.RequestError, httpx.TimeoutException) as e:
        return None, f"payment_service_unavailable: {str(e)}"


async def refund_payment(payment_id: str):
    """Refund a payment via mock payment service."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{PAYMENT_MOCK_URL}/api/v1/payments/refund",
                json={"payment_id": payment_id},
                timeout=10.0,
            )
    except (httpx.RequestError, httpx.TimeoutException):
        pass


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(quote_id: str, customer_id: str):
    """Create an order from an accepted quote."""
    quote = load_quote(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    if quote.status != "accepted":
        raise HTTPException(status_code=400, detail=f"Quote must be accepted before ordering. Current status: {quote.status}")

    if quote.customer_id != customer_id:
        raise HTTPException(status_code=400, detail="Customer ID does not match quote")

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    items = []
    for qi in quote.items:
        name = await fetch_equipment_name(qi.equipment_id)
        items.append(OrderItem(
            equipment_id=qi.equipment_id,
            equipment_name=name,
            quantity=qi.quantity,
            rental_days=qi.rental_days,
            unit_price=qi.unit_price,
            total_price=round(qi.unit_price * qi.quantity * qi.rental_days, 2),
        ))

    order = Order(
        order_id=order_id,
        quote_id=quote_id,
        customer_id=customer_id,
        customer_type=quote.customer_type,
        items=items,
        subtotal=quote.subtotal,
        delivery_fee=quote.delivery_fee,
        insurance_fee=quote.insurance_fee,
        total=quote.total,
        status="pending",
        payment_status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    save_order(order)
    return order


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get order by ID."""
    order = load_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/confirm")
async def confirm_order(order_id: str):
    """Confirm an order and process payment via mock payment service."""
    order = load_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail=f"Order is {order.status}, cannot confirm")

    payment_id, error = await authorize_payment(order.total, order.customer_id)

    if error:
        order.status = "cancelled"
        order.payment_status = "failed"
        order.updated_at = datetime.now()
        save_order(order)
        raise HTTPException(
            status_code=402,
            detail=f"Payment failed: {error}",
        )

    order.status = "confirmed"
    order.payment_status = "paid"
    order.payment_id = payment_id
    order.updated_at = datetime.now()
    save_order(order)

    return {
        "order_id": order_id,
        "status": "confirmed",
        "payment_id": payment_id,
        "payment_status": "paid",
    }


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, reason: Optional[str] = None):
    """Cancel an order and refund payment."""
    order = load_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status: {order.status}")

    if order.payment_id and order.payment_status == "paid":
        await refund_payment(order.payment_id)

    order.status = "cancelled"
    order.payment_status = "refunded"
    order.updated_at = datetime.now()
    save_order(order)

    return {
        "order_id": order_id,
        "status": "cancelled",
        "payment_status": "refunded",
        "reason": reason,
    }


@router.get("/", response_model=List[Order])
async def list_orders(customer_id: Optional[str] = None, status: Optional[str] = None):
    """List orders with optional filters."""
    return list_orders_from_db(customer_id, status)


@router.get("/stats")
async def get_order_stats():
    """Get order statistics."""
    all_orders = list_orders_from_db()

    stats = {
        "total_orders": len(all_orders),
        "by_status": {},
        "by_payment_status": {},
    }

    for order in all_orders:
        if order.status not in stats["by_status"]:
            stats["by_status"][order.status] = 0
        stats["by_status"][order.status] += 1

        if order.payment_status not in stats["by_payment_status"]:
            stats["by_payment_status"][order.payment_status] = 0
        stats["by_payment_status"][order.payment_status] += 1

    return stats
