from fastapi import APIRouter, Depends, HTTPException

from sqlmodel import Session, select
from app.models.user import User
from app.models.project import Project
from app.models.group_member import GroupMember,Role,AddProjectMember
from app.schemas.project import CreateProject

def get_all_projects_for_user(
    current_user: User,
) -> list[Project]:
    projects = current_user.projects

    if not projects:
        raise HTTPException(status_code=404, detail="not found")

    return projects

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
    
def add_member_to_project_controller(
    data: AddProjectMember,
    session: Session,
    current_user: User,
) -> GroupMember:
    project = session.get(Project, data.project_id)
    user = session.get(User, data.member_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    current_membership = session.exec(
        select(GroupMember).where(
            GroupMember.project_id == data.project_id,
            GroupMember.member_id == current_user.id
        )
    ).first()

    if not current_membership:
        raise HTTPException(
            status_code=403,
            detail="Current user is not a member of this project"
        )

    if current_membership.role != Role.owner:
        raise HTTPException(
            status_code=403,
            detail=f"Only owner can add members. Your role is {current_membership.role}"
        )

    existing_membership = session.exec(
        select(GroupMember).where(
            GroupMember.project_id == data.project_id,
            GroupMember.member_id == data.member_id
        )
    ).first()

    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User already added to this project"
        )

    group_membership = GroupMember(
        project_id=data.project_id,
        member_id=data.member_id,
        role=data.role,
    )

    session.add(group_membership)
    session.commit()
    session.refresh(group_membership)

    return group_membership


