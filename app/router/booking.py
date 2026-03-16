from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models.engine import get_db
from app.models.database import Booking
from app.schemas.gym import BookingRequest, BookingResponse

booking_router = APIRouter(prefix="/booking", tags=["booking"])

@booking_router.post("/", response_model=BookingResponse)
def create_booking(booking: BookingRequest, db: Session = Depends(get_db)):
    new_booking = Booking(**booking.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@booking_router.get("/", response_model=List[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()