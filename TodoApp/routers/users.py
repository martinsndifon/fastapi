"""
Main entry to the application
"""
from typing import Annotated
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from passlib.context import CryptContext

from database import SessionLocal
from models import Users
from .auth import get_current_user


router = APIRouter(prefix="/user", tags=["users"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    """Provides password data validation using pydantic BaseModel"""

    password: str
    new_password: str = Field(min_length=6)


class PhoneVerification(BaseModel):
    """Provides phone number validation"""

    phone_number: str


@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_current_user(user: user_dependency, db: db_dependency):
    """Return all the information about the logged in user"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "is_active": current_user.is_active,
        "role": current_user.role,
    }


@router.patch("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    user: user_dependency, db: db_dependency, user_request: UserVerification
):
    """Change the password of the logged in user"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(user_request.password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    current_user.hashed_password = bcrypt_context.hash(user_request.new_password)

    db.add(current_user)
    db.commit()


@router.patch("/change_phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_phone_number(
    user: user_dependency, db: db_dependency, user_request: PhoneVerification
):
    """Change the phone_number of the logged in user"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_user.phone_number = user_request.phone_number

    db.add(current_user)
    db.commit()
