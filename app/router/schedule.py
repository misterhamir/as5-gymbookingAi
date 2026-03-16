from fastapi import APIRouter, Depends
from typing import List
from sqlmodel import Session
from app.models.engine import get_db
from app.models.database import Schedule
from app.schemas.gym import ScheduleRequest, ScheduleResponse

schedule_router = APIRouter(prefix="/schedule", tags=["schedule"])

@schedule_router.post("/", response_model=ScheduleResponse)
def create_schedule(schedule: ScheduleRequest, db: Session = Depends(get_db)):
    new_schedule = Schedule(**schedule.dict())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

@schedule_router.get("/", response_model=List[ScheduleResponse])
def get_schedules(db: Session = Depends(get_db)):
    return db.query(Schedule).all()
