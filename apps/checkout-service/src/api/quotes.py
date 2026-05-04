"""
Quotes API - Generate and manage equipment quotes
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

router = APIRouter()


class QuoteItem(BaseModel):
    equipment_id: str
    quantity: int = 1
    rental_days: int = 1
    unit_price: float


class QuoteRequest(BaseModel):
    customer_id: str
    customer_type: str = "company"  # company, individual
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
    status: str = "pending"  # pending, accepted, rejected, expired
    created_at: datetime
    delivery_required: bool = False
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


# In-memory storage (replace with Redis/DB in production)
quotes_db = {}


@router.post("/", response_model=Quote, status_code=status.HTTP_201_CREATED)
async def create_quote(request: QuoteRequest):
    """Generate a new equipment quote"""
    quote_id = f"QT-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate totals
    subtotal = sum(item.unit_price * item.quantity * item.rental_days for item in request.items)
    
    # Delivery fee (10% of subtotal if required)
    delivery_fee = subtotal * 0.10 if request.delivery_required else 0.0
    
    # Insurance (5% for heavy equipment)
    insurance_fee = subtotal * 0.05
    
    # Total
    total = subtotal + delivery_fee + insurance_fee
    
    # Valid for 7 days
    valid_until = datetime.now() + timedelta(days=7)
    
    quote = Quote(
        quote_id=quote_id,
        customer_id=request.customer_id,
        customer_type=request.customer_type,
        items=request.items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        insurance_fee=insurance_fee,
        total=total,
        valid_until=valid_until,
        delivery_required=request.delivery_required,
        delivery_address=request.delivery_address,
        notes=request.notes,
        created_at=datetime.now()
    )
    
    # Store quote
    quotes_db[quote_id] = quote
    
    return quote


@router.get("/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    """Retrieve a quote by ID"""
    if quote_id not in quotes_db:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return quotes_db[quote_id]


@router.post("/{quote_id}/accept")
async def accept_quote(quote_id: str):
    """Accept a quote (convert to order)"""
    if quote_id not in quotes_db:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote = quotes_db[quote_id]
    
    # Check if quote is still valid
    if datetime.now() > quote.valid_until:
        quote.status = "expired"
        raise HTTPException(status_code=400, detail="Quote has expired")
    
    if quote.status != "pending":
        raise HTTPException(status_code=400, detail=f"Quote is {quote.status}, cannot accept")
    
    quote.status = "accepted"
    
    # Here you would trigger order creation in a real system
    return {"message": "Quote accepted", "quote_id": quote_id, "status": "accepted"}


@router.post("/{quote_id}/reject")
async def reject_quote(quote_id: str):
    """Reject a quote"""
    if quote_id not in quotes_db:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote = quotes_db[quote_id]
    quote.status = "rejected"
    
    return {"message": "Quote rejected", "quote_id": quote_id}


@router.get("/", response_model=List[Quote])
async def list_quotes(customer_id: Optional[str] = None, status: Optional[str] = None):
    """List quotes with optional filters"""
    result = list(quotes_db.values())
    
    if customer_id:
        result = [q for q in result if q.customer_id == customer_id]
    
    if status:
        result = [q for q in result if q.status == status]
    
    return result
