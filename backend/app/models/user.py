from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field,Relationship
from app.models.group_member import GroupMember


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    google_sub: str = Field(index=True, unique=True)
    full_name: Optional[str] = Field(default=None)
    email: str = Field(index=True, unique=True)
    avatar_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    projects: list["Project"]=Relationship(back_populates="members",link_model=GroupMember)


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)