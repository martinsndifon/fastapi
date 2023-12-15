from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated

from pydantic import BaseModel
from database import SessionLocal
from models import Users

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "52d287e48fd2ad86d9d36d9f20662c220243786db5575ce3866f2b4ba48d35cd"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserREquest(BaseModel):
    """Provides data validation using pydantic BaseModel"""

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    """Response model for jwt token response route"""

    access_token: str
    token_type: str


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    """Authenticate user by verifying with saved db info"""
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return 1
    if not bcrypt_context.verify(password, user.hashed_password):
        return 2
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    """Creates a jwt access token"""
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """Verify the jwt token from the request"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: CreateUserREquest):
    """Get authenticated user"""
    email = db.query(Users).filter(Users.email == user_request.email).first()
    if email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="email already exists"
        )

    username = db.query(Users).filter(Users.username == user_request.username).first()
    if username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="username is taken"
        )

    create_user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    """Get access token after login"""
    user = authenticate_user(form_data.username, form_data.password, db)

    if user == 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate username.",
        )
    if user == 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate password.",
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}
