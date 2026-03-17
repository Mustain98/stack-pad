from fastapi import APIRouter, Depends

from sqlmodel import Session
from app.db.database import get_session
from app.services.user import get_current_user
from app.models.user import User
from app.models.project import Project,CreateProject
from app.schemas.user import UserRead
from app.controllers.user import(
    get_all_projects_for_user,
    create_project_for_user
)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/projects",response_model=list[Project])
def get_all_projects(all_projects:list[Project]=Depends(get_all_projects_for_user)):
    return all_projects


@router.post("/me/project", response_model=Project)
def create_new_project(
    project_data: CreateProject,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Project:
    return create_project_for_user(project_data, session, current_user)