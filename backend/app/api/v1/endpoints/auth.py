from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.security.tenant import get_current_user
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    AuthResponse,
    TokenResponse,
    UserProfileResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication & Access"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Organization & Owner Account",
    description="Creates a new tenant organization and registers the primary owner with administrative privileges."
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    auth_service = AuthService(db)
    return auth_service.register(payload)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates credentials and returns JWT access & refresh tokens along with tenant membership."
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    auth_service = AuthService(db)
    return auth_service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate Refresh Token",
    description="Exchanges a valid refresh token for a fresh access token and new rotated refresh token."
)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)
    return auth_service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke Session",
    description="Revokes the active refresh token and terminates the current user session."
)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.logout(payload.refresh_token)
    return {"message": "Session logged out successfully"}


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Current User Profile",
    description="Returns the profile and active organization memberships of the authenticated user."
)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserProfileResponse:
    auth_service = AuthService(db)
    return auth_service.get_user_profile(current_user)
