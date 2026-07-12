from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from starlette.config import Config as StarletteConfig

from app.api.deps import get_auth_service, get_current_user
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    AuthenticatedResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService, TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_COOKIE_PATH = "/api/v1/auth"

_oauth = OAuth(StarletteConfig(environ={}))
_oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def _set_refresh_cookie(response: Response, tokens: TokenPair) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 3600,
        path=_REFRESH_COOKIE_PATH,
    )


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        email_verified=user.email_verified,
        streak_count=user.streak_count,
        created_at=user.created_at,
    )


@router.post("/register", response_model=AuthenticatedResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedResponse:
    user, tokens = await auth_service.register(payload.email, payload.password, payload.display_name)
    _set_refresh_cookie(response, tokens)
    return AuthenticatedResponse(
        user=_to_user_response(user),
        access_token=tokens.access_token,
        expires_in=tokens.expires_in,
    )


@router.post("/login", response_model=AuthenticatedResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedResponse:
    user, tokens = await auth_service.login(payload.email, payload.password)
    _set_refresh_cookie(response, tokens)
    return AuthenticatedResponse(
        user=_to_user_response(user),
        access_token=tokens.access_token,
        expires_in=tokens.expires_in,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AccessTokenResponse:
    refresh_token = request.cookies.get(_REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("No refresh token present.")

    tokens = await auth_service.refresh(refresh_token)
    _set_refresh_cookie(response, tokens)
    return AccessTokenResponse(access_token=tokens.access_token, expires_in=tokens.expires_in)


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    refresh_token = request.cookies.get(_REFRESH_COOKIE_NAME)
    if refresh_token:
        await auth_service.logout(refresh_token)
    response.delete_cookie(_REFRESH_COOKIE_NAME, path=_REFRESH_COOKIE_PATH)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return _to_user_response(current_user)


@router.post("/verify-email", response_model=UserResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await auth_service.verify_email(payload.token)
    return _to_user_response(user)


@router.post("/forgot-password", status_code=202)
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    await auth_service.request_password_reset(payload.email)
    # Always a generic 202, whether or not the email exists — see
    # AuthService.request_password_reset for the enumeration-prevention rationale.
    return {"detail": "If an account exists for this email, a reset link has been sent."}


@router.post("/reset-password", status_code=204)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await auth_service.reset_password(payload.token, payload.new_password)


@router.get("/google")
async def google_login(request: Request):
    settings = get_settings()
    return await _oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    settings = get_settings()
    token = await _oauth.google.authorize_access_token(request)
    profile = token.get("userinfo") or await _oauth.google.userinfo(token=token)

    user, tokens = await auth_service.login_or_register_with_google(
        oauth_id=profile["sub"],
        email=profile["email"],
        display_name=profile.get("name") or profile["email"].split("@")[0],
        avatar_url=profile.get("picture"),
    )

    redirect = RedirectResponse(url=f"{settings.frontend_base_url}/auth/callback")
    _set_refresh_cookie(redirect, tokens)
    # The access token can't travel in a redirect body, so it's handed to the
    # SPA via a short-lived query param that /auth/callback exchanges
    # immediately and never persists — the httpOnly refresh cookie above is
    # the durable credential.
    redirect.headers["Location"] += f"?access_token={tokens.access_token}"
    return redirect
