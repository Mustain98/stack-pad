from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import SQLModel


class UserRead(SQLModel):
    id: UUID
    google_sub: str
    full_name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    is_active: bool
   


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"