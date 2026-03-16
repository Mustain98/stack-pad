from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import Session, select

from app.core.config import settings
from app.core.auth import oauth
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_token,
)
from app.db import get_session
from app.models import RefreshToken, User