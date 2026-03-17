from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import SQLModel, Field, UniqueConstraint


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    editor = "editor"
    viewer = "viewer"
    owner = "owner"


class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("project_id", "member_id"),)

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    project_id: UUID = Field(foreign_key="projects.id")
    member_id: UUID = Field(foreign_key="users.id")
    role: Role = Field(default=Role.viewer)
    added: datetime = Field(default_factory=utc_now)
    updated: datetime = Field(default_factory=utc_now)

class AddProjectMember(SQLModel):
    project_id: UUID
    member_id: UUID
    role: Role = Role.viewer