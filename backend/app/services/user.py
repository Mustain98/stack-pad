from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.user import User
from app.core.security import decode_access_token

def get_current_user(
    request:Request,
    session:Session=Depends(get_session),
)->User:
    token=request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    try:
        payload=decode_access_token(token)
        if payload.get("type")!="access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token"
            )
        user_id=payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    
    user=session.get(User,user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


