from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str

class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_name: str
    instructor: str
    start_time: datetime
    end_time: datetime

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_name: str
    payment_status: str = "pending"
    user_id: int = Field(foreign_key="user.id")
    schedule_id: int = Field(foreign_key="schedule.id")