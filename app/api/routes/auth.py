from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from passlib.context import CryptContext

from app.schemas.auth import TokenResponse
from app.services.auth_service import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Production would validate against a user database.
# For this take-home, a single hardcoded attorney account is sufficient.
HARDCODED_USER = {
    "username": "attorney@alma.com",
    "hashed_password": "$2b$12$fomfe8H4G.6iKyYaddwED..L0sn9wfWA2CVwuD319O/Z2C9GqEIOW",  # password123
}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain access token",
    description="Authenticate with username and password to receive a JWT access token.",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    if (
        form_data.username != HARDCODED_USER["username"]
        or not pwd_context.verify(form_data.password, HARDCODED_USER["hashed_password"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": form_data.username})
    return TokenResponse(access_token=token)
