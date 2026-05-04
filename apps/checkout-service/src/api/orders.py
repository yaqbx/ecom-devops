"""
Orders API - Process and track equipment rental orders
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()


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
    status: str = "pending"  # pending, confirmed, active, completed, cancelled
    payment_status: str = "pending"  # pending, paid, refunded, failed
    delivery_schedule_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# In-memory storage
orders_db = {}


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(quote_id: str, customer_id: str):
    """Create an order from an accepted quote"""
    # In production, fetch quote from quotes service
    # For now, mock order creation
    
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    order = Order(
        order_id=order_id,
        quote_id=quote_id,
        customer_id=customer_id,
        customer_type="company",
        items=[],  # Would fetch from quote
        subtotal=0.0,
        delivery_fee=0.0,
        insurance_fee=0.0,
        total=0.0,
        status="pending",
        payment_status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    orders_db[order_id] = order
    return order


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get order by ID"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]


@router.post("/{order_id}/confirm")
async def confirm_order(order_id: str):
    """Confirm an order (after payment)"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail=f"Order is {order.status}, cannot confirm")
    
    order.status = "confirmed"
    order.payment_status = "paid"
    order.updated_at = datetime.now()
    
    return {"order_id": order_id, "status": "confirmed"}


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, reason: Optional[str] = None):
    """Cancel an order"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status: {order.status}")
    
    order.status = "cancelled"
    order.payment_status = "refunded"
    order.updated_at = datetime.now()
    
    return {
        "order_id": order_id,
        "status": "cancelled",
        "reason": reason
    }


@router.get("/", response_model=List[Order])
async def list_orders(
    customer_id: Optional[str] = None,
    status: Optional[str] = None
):
    """List orders with optional filters"""
    result = list(orders_db.values())
    
    if customer_id:
        result = [o for o in result if o.customer_id == customer_id]
    
    if status:
        result = [o for o in result if o.status == status]
    
    return result


@router.get("/stats")
async def get_order_stats():
    """Get order statistics"""
    all_orders = list(orders_db.values())
    
    stats = {
        "total_orders": len(all_orders),
        "by_status": {},
        "by_payment_status": {}
    }
    
    for order in all_orders:
        # Count by status
        if order.status not in stats["by_status"]:
            stats["by_status"][order.status] = 0
        stats["by_status"][order.status] += 1
        
        # Count by payment status
        if order.payment_status not in stats["by_payment_status"]:
            stats["by_payment_status"][order.payment_status] = 0
        stats["by_payment_status"][order.payment_status] += 1
    
    return stats
