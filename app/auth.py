from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.database import engine
from app.models import User
from app.security import hash_password, verify_password

SECRET_KEY = "HUEhuiHUIHEIUhuiehwIUEweuvwQEUGwygeuGWEgqugjhbeQWJBELhjegbjwhJHEGwgeIUWGHWJkegwHJLGEWjlhD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_session():
    with Session(engine) as session:
        yield session


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")

    hashed = hash_password(data.password)

    first_user = session.exec(select(User)).first()
    is_first_user = first_user is None

    user = User(email=data.email, hashed_password=hashed, is_admin=is_first_user)
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"id": user.id, "email": user.email, "is_admin": user.is_admin}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = session.exec(select(User).where(User.email == data.email)).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise credentials_exception

    return user


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "is_admin": current_user.is_admin}
