from fastapi import APIRouter, Depends, HTTPException

from sqlmodel import Session
from app.db.database import get_session
from app.services.user import get_current_user
from app.models.user import User
from app.models.project import Project,CreateProject
from app.models.group_member import GroupMember,Role
from app.schemas.user import UserRead

def get_all_projects_for_user(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[Project]:
    if not current_user.projects:
        raise HTTPException(
            status_code=404,
            detail="not found"
        )
    return current_user.projects

def create_project_for_user(
    project_data: CreateProject,
    session: Session,
    current_user: User,
) -> Project:
    db_project = Project(
        title=project_data.title,
        description=project_data.description,
        github_link=project_data.github_link,
        deployed_link=project_data.deployed_link,
    )

    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    membership = GroupMember(
        project_id=db_project.id,
        member_id=current_user.id,
        role=Role.owner,
    )

    session.add(membership)
    session.commit()

    return db_project
    