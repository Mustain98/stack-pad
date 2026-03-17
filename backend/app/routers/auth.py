from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import Session, select
from datetime import datetime

from app.core.config import settings
from app.core.auth import oauth
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_token,
)
from app.db.database import get_session
from app.models.user import RefreshToken, User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/login/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(
        request,
        settings.GOOGLE_REDIRECT_URI
    )

@router.get("/google/callback")
async def google_callback(request:Request,session:Session=Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    userinfo=token.get("userinfo")

    if not userinfo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve Google user info",
        )
    
    google_sub=userinfo["sub"]
    email=userinfo["email"]
    full_name=userinfo["name"]
    avatar_url=userinfo["picture"]

    user = session.exec(
        select(User).where(User.google_sub == google_sub)
    ).first()

    if not user:
        user= User(
            google_sub=google_sub,
            full_name=full_name,
            avatar_url=avatar_url,
            email=email,
            is_active=True
        )
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token=create_access_token(str(user.id))
    refresh_token,refresh_hash,refresh_expires_at=create_refresh_token(str(user.id))

    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=refresh_expires_at,
    )
    session.add(db_refresh_token)
    session.commit()
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/success")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return response

@router.post("/refresh")
def refresh(
    request:Request,
    session:Session=Depends(get_session)
):
    raw_refresh_token=request.cookies.get("refresh_token")
    if not raw_refresh_token:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    
    try:
        payload=decode_refresh_token(raw_refresh_token)
        if payload.get("type")!="refresh":
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
    except Exception:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    stored=session.exec(
         select(RefreshToken).where (RefreshToken.token_hash==hash_token(raw_refresh_token))
        ).first()
    if not stored:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    if stored.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked",
        )
    if stored.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    
    new_access_token=create_access_token(payload["sub"])
    response = JSONResponse(
        content={"access_token": new_access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response

@router.post("/logout")
def logout(
    request: Request,
    session: Session = Depends(get_session),
):
    raw_refresh_token = request.cookies.get("refresh_token")

    if raw_refresh_token:
        stored = session.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == hash_token(raw_refresh_token)
            )
        ).first()

        if stored and stored.revoked_at is None:
            from datetime import datetime, timezone
            stored.revoked_at = datetime.now(timezone.utc)
            session.add(stored)
            session.commit()

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


