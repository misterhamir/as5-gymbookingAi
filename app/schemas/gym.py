from typing import List
from pydantic import BaseModel
from datetime import datetime

class ScheduleRequest(BaseModel):
    class_name: str
    instructor: str
    start_time: datetime
    end_time: datetime

class BookingRequest(BaseModel):
    booking_name: str
    user_id: int
    schedule_id: int

class ScheduleResponse(BaseModel):
    id: int
    class_name: str
    instructor: str
    start_time: datetime
    end_time: datetime

class BookingResponse(BaseModel):
    id: int
    booking_name: str
    payment_status: str
    user_id: int
    schedule_id: int

class allScheduleResponse(BaseModel):
    schedules: List[ScheduleResponse]

class allBookingResponse(BaseModel):
    bookings: List[BookingResponse]

class UserRequest(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str