"""
Mock Payment Service - Simulates payment processing for testing
No real payment provider integration. Returns realistic responses.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import random

__version__ = "1.0.0"

app = FastAPI(
    title="Mock Payment Service",
    description="Simulated payment processing for development/testing",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PAYMENT_METHODS = ["credit_card", "debit_card", "bank_transfer", "invoice"]

# Cards that trigger specific responses
DECLINE_CARDS = ["4111111111111111", "4000000000000002"]
INSUFFICIENT_FUNDS_CARDS = ["4000000000000005"]
EXPIRED_CARDS = ["4000000000000069"]

payments_db = {}


class AuthorizeRequest(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "USD"
    card_token: str
    description: Optional[str] = None
    metadata: Optional[dict] = None


class CaptureRequest(BaseModel):
    auth_id: str
    amount: Optional[float] = None


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str  # authorized, captured, refunded, failed
    amount: float
    currency: str
    card_last_four: str
    payment_method: str
    authorized_at: Optional[datetime] = None
    captured_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


def mask_card(card_token: str) -> str:
    return f"****{card_token[-4:]}" if len(card_token) >= 4 else "****"


@app.get("/")
async def root():
    return {
        "service": "payment-mock",
        "version": __version__,
        "endpoints": {
            "health": "/health",
            "authorize": "POST /api/v1/payments/authorize",
            "capture": "POST /api/v1/payments/capture",
            "refund": "POST /api/v1/payments/refund",
            "get_payment": "GET /api/v1/payments/{id}",
            "list_payments": "GET /api/v1/payments",
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "payment-mock",
        "version": __version__,
    }


@app.post("/api/v1/payments/authorize", response_model=PaymentResponse, status_code=201)
async def authorize_payment(request: AuthorizeRequest):
    """Authorize a payment. Simulates card validation and fraud checks."""
    card_last_four = mask_card(request.card_token)
    payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"

    # Simulate random failure ~5% of the time
    if random.random() < 0.05:
        payment = PaymentResponse(
            payment_id=payment_id,
            status="failed",
            amount=request.amount,
            currency=request.currency,
            card_last_four=card_last_four,
            payment_method="credit_card",
            error="bank_declined",
            metadata=request.metadata,
        )
        payments_db[payment_id] = payment
        return payment

    # Specific card-based failures for testing
    clean_card = request.card_token.replace(" ", "").replace("-", "")
    if clean_card in DECLINE_CARDS:
        payment = PaymentResponse(
            payment_id=payment_id,
            status="failed",
            amount=request.amount,
            currency=request.currency,
            card_last_four=card_last_four,
            payment_method="credit_card",
            error="card_declined",
            metadata=request.metadata,
        )
        payments_db[payment_id] = payment
        raise HTTPException(status_code=402, detail="Card declined")

    if clean_card in INSUFFICIENT_FUNDS_CARDS:
        payment = PaymentResponse(
            payment_id=payment_id,
            status="failed",
            amount=request.amount,
            currency=request.currency,
            card_last_four=card_last_four,
            payment_method="credit_card",
            error="insufficient_funds",
            metadata=request.metadata,
        )
        payments_db[payment_id] = payment
        raise HTTPException(status_code=402, detail="Insufficient funds")

    if clean_card in EXPIRED_CARDS:
        payment = PaymentResponse(
            payment_id=payment_id,
            status="failed",
            amount=request.amount,
            currency=request.currency,
            card_last_four=card_last_four,
            payment_method="credit_card",
            error="card_expired",
            metadata=request.metadata,
        )
        payments_db[payment_id] = payment
        raise HTTPException(status_code=402, detail="Card expired")

    # Success
    payment = PaymentResponse(
        payment_id=payment_id,
        status="authorized",
        amount=request.amount,
        currency=request.currency,
        card_last_four=card_last_four,
        payment_method="credit_card",
        authorized_at=datetime.now(),
        metadata=request.metadata,
    )
    payments_db[payment_id] = payment
    return payment


@app.post("/api/v1/payments/capture", response_model=PaymentResponse)
async def capture_payment(request: CaptureRequest):
    """Capture a previously authorized payment."""
    if request.auth_id not in payments_db:
        raise HTTPException(status_code=404, detail="Authorization not found")

    payment = payments_db[request.auth_id]

    if payment.status != "authorized":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot capture payment with status: {payment.status}"
        )

    payment.status = "captured"
    payment.captured_at = datetime.now()
    if request.amount:
        payment.amount = request.amount

    return payment


@app.post("/api/v1/payments/refund", response_model=PaymentResponse)
async def refund_payment(request: RefundRequest):
    """Refund a captured payment."""
    if request.payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payments_db[request.payment_id]

    if payment.status not in ["captured", "authorized"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot refund payment with status: {payment.status}"
        )

    payment.status = "refunded"
    payment.refunded_at = datetime.now()

    return payment


@app.get("/api/v1/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment details by ID."""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments_db[payment_id]


@app.get("/api/v1/payments", response_model=List[PaymentResponse])
async def list_payments(status_filter: Optional[str] = None):
    """List all payments with optional status filter."""
    result = list(payments_db.values())
    if status_filter:
        result = [p for p in result if p.status == status_filter]
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8100)),
        reload=True,
    )
