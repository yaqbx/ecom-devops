"""
Delivery Scheduling API - Schedule equipment delivery and pickup
Persisted in Redis.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import json
import os

from src.services.redis_client import redis_client

router = APIRouter()

DELIVERY_TTL = 60 * 60 * 24 * 90


class DeliveryWindow(BaseModel):
    window_id: str
    date: str
    start_time: str
    end_time: str
    available: bool = True
    price_multiplier: float = 1.0


class DeliveryRequest(BaseModel):
    quote_id: str
    equipment_ids: List[str]
    delivery_postal_code: str
    pickup_postal_code: Optional[str] = None
    preferred_date: Optional[str] = None
    customer_type: str = "company"


class DeliverySchedule(BaseModel):
    schedule_id: str
    quote_id: str
    equipment_ids: List[str]
    delivery_date: str
    delivery_window: str
    delivery_address: str
    pickup_date: Optional[str] = None
    pickup_window: Optional[str] = None
    status: str = "scheduled"
    tracking_number: Optional[str] = None
    special_instructions: Optional[str] = None


def schedule_key(schedule_id: str) -> str:
    return f"delivery:{schedule_id}"


def index_key() -> str:
    return "deliveries:index"


def save_schedule(schedule: DeliverySchedule):
    key = schedule_key(schedule.schedule_id)
    data = schedule.model_dump(mode="json")
    if redis_client.set(key, json.dumps(data), ex=DELIVERY_TTL):
        redis_client.client.sadd(index_key(), schedule.schedule_id)


def load_schedule(schedule_id: str) -> Optional[DeliverySchedule]:
    data = redis_client.get(schedule_key(schedule_id))
    if data is None:
        return None
    return DeliverySchedule(**json.loads(data))


available_windows = [
    DeliveryWindow(
        window_id="DW-001",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        start_time="08:00",
        end_time="12:00",
        available=True,
        price_multiplier=1.0,
    ),
    DeliveryWindow(
        window_id="DW-002",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        start_time="13:00",
        end_time="17:00",
        available=True,
        price_multiplier=1.0,
    ),
    DeliveryWindow(
        window_id="DW-003",
        date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        start_time="08:00",
        end_time="12:00",
        available=True,
        price_multiplier=0.9,
    ),
]


@router.get("/windows", response_model=List[DeliveryWindow])
async def get_available_windows(date: Optional[str] = None):
    """Get available delivery windows."""
    if date:
        return [w for w in available_windows if w.date == date and w.available]
    return [w for w in available_windows if w.available]


@router.post("/schedule", response_model=DeliverySchedule)
async def schedule_delivery(request: DeliveryRequest):
    """Schedule delivery for equipment."""
    schedule_id = f"DEL-{uuid.uuid4().hex[:8].upper()}"
    tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"

    delivery_date = request.preferred_date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    schedule = DeliverySchedule(
        schedule_id=schedule_id,
        quote_id=request.quote_id,
        equipment_ids=request.equipment_ids,
        delivery_date=delivery_date,
        delivery_window="08:00-17:00",
        delivery_address=request.delivery_postal_code,
        tracking_number=tracking_number,
        status="scheduled",
    )

    save_schedule(schedule)
    return schedule


@router.get("/schedule/{schedule_id}", response_model=DeliverySchedule)
async def get_delivery_schedule(schedule_id: str):
    """Get delivery schedule by ID."""
    schedule = load_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/schedule/{schedule_id}/status")
async def update_delivery_status(schedule_id: str, new_status: str):
    """Update delivery status."""
    schedule = load_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    valid_statuses = ["scheduled", "in_transit", "delivered", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    schedule.status = new_status
    save_schedule(schedule)

    return {"schedule_id": schedule_id, "status": new_status}


@router.post("/calculate-distance")
async def calculate_distance(origin: str, destination: str):
    """Calculate distance and estimated delivery cost."""
    return {
        "origin": origin,
        "destination": destination,
        "distance_km": 45.5,
        "estimated_time_minutes": 65,
        "base_fee": 150.0,
        "per_km_rate": 2.5,
        "total_estimate": 263.75,
    }
