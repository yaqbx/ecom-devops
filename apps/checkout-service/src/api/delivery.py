"""
Delivery Scheduling API - Schedule equipment delivery and pickup
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

router = APIRouter()


class DeliveryWindow(BaseModel):
    """Available delivery time window"""
    window_id: str
    date: str
    start_time: str
    end_time: str
    available: bool = True
    price_multiplier: float = 1.0


class DeliveryRequest(BaseModel):
    """Request delivery scheduling"""
    quote_id: str
    equipment_ids: List[str]
    delivery_postal_code: str
    pickup_postal_code: Optional[str] = None
    preferred_date: Optional[str] = None
    customer_type: str = "company"


class DeliverySchedule(BaseModel):
    """Confirmed delivery schedule"""
    schedule_id: str
    quote_id: str
    equipment_ids: List[str]
    delivery_date: str
    delivery_window: str
    delivery_address: str
    pickup_date: Optional[str] = None
    pickup_window: Optional[str] = None
    status: str = "scheduled"  # scheduled, in_transit, delivered, completed
    tracking_number: Optional[str] = None
    special_instructions: Optional[str] = None


# In-memory storage
delivery_schedules = {}
available_windows = [
    DeliveryWindow(
        window_id="DW-001",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        start_time="08:00",
        end_time="12:00",
        available=True,
        price_multiplier=1.0
    ),
    DeliveryWindow(
        window_id="DW-002",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        start_time="13:00",
        end_time="17:00",
        available=True,
        price_multiplier=1.0
    ),
    DeliveryWindow(
        window_id="DW-003",
        date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        start_time="08:00",
        end_time="12:00",
        available=True,
        price_multiplier=0.9  # 10% discount for future dates
    ),
]


@router.get("/windows", response_model=List[DeliveryWindow])
async def get_available_windows(date: Optional[str] = None):
    """Get available delivery windows"""
    if date:
        return [w for w in available_windows if w.date == date and w.available]
    return [w for w in available_windows if w.available]


@router.post("/schedule", response_model=DeliverySchedule)
async def schedule_delivery(request: DeliveryRequest):
    """Schedule delivery for equipment"""
    schedule_id = f"DEL-{uuid.uuid4().hex[:8].upper()}"
    tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"
    
    # Default to tomorrow if no preferred date
    delivery_date = request.preferred_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    schedule = DeliverySchedule(
        schedule_id=schedule_id,
        quote_id=request.quote_id,
        equipment_ids=request.equipment_ids,
        delivery_date=delivery_date,
        delivery_window="08:00-17:00",
        delivery_address=request.delivery_postal_code,
        pickup_date=None,  # Will be set on delivery
        pickup_window=None,
        tracking_number=tracking_number,
        status="scheduled"
    )
    
    delivery_schedules[schedule_id] = schedule
    return schedule


@router.get("/schedule/{schedule_id}", response_model=DeliverySchedule)
async def get_delivery_schedule(schedule_id: str):
    """Get delivery schedule by ID"""
    if schedule_id not in delivery_schedules:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return delivery_schedules[schedule_id]


@router.post("/schedule/{schedule_id}/status")
async def update_delivery_status(schedule_id: str, new_status: str):
    """Update delivery status"""
    if schedule_id not in delivery_schedules:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    valid_statuses = ["scheduled", "in_transit", "delivered", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    schedule = delivery_schedules[schedule_id]
    schedule.status = new_status
    
    return {"schedule_id": schedule_id, "status": new_status}


@router.post("/calculate-distance")
async def calculate_distance(origin: str, destination: str):
    """Calculate distance and estimated delivery cost"""
    # Mock calculation - in production, use Google Maps API or similar
    return {
        "origin": origin,
        "destination": destination,
        "distance_km": 45.5,  # Mock
        "estimated_time_minutes": 65,  # Mock
        "base_fee": 150.0,
        "per_km_rate": 2.5,
        "total_estimate": 263.75
    }
