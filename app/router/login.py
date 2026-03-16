from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models.engine import get_db
from app.models.database import User
from app.schemas.gym import UserRequest, UserResponse
from app.utils.security import get_password_hash
from typing import List

login_router = APIRouter(prefix="/login", tags=["login"])

@login_router.post("/", response_model=UserResponse)
def create_user(user: UserRequest, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user_data = user.dict(exclude={"password"})
    new_user = User(**user_data, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@login_router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()