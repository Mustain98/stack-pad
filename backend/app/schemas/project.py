from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from app.models.group_member import GroupMember
from app.schemas.user import UserRead

class CreateProject(SQLModel):
    title: str
    description: Optional[str] = None
    github_link: Optional[str] = None
    deployed_link: Optional[str] = None

class ProjectRead(SQLModel):
    id: UUID
    title: str
    description: Optional[str] = None
    github_link: Optional[str] = None
    deployed_link: Optional[str] = None

class ProjectWithMembersRead(ProjectRead):
    members: list[UserRead] = []