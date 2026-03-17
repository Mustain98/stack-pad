from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from app.models.group_member import GroupMember


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    github_link: Optional[str] = Field(default=None)
    deployed_link: Optional[str] = Field(default=None)

    members: list["User"] = Relationship(
        back_populates="projects",
        link_model=GroupMember
    )

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CreateProject(SQLModel):
    title: str
    description: Optional[str] = None
    github_link: Optional[str] = None
    deployed_link: Optional[str] = None