from fastapi import APIRouter
from pydantic import BaseModel
from models import Users

router = APIRouter()


class CreateUserREquest(BaseModel):
    """Provides data validation using pydantic BaseModel"""

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth")
async def create_user(user_request: CreateUserREquest):
    """Get authenticated user"""
    create_user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=user_request.password,
        is_active=True,
    )

    return create_user_model
