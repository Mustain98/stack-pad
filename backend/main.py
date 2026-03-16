from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.db.database import create_db_and_tables
from app.routers.auth import router as auth_router
from app.routers.user import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Stackpad Backend", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,  
    same_site="lax",
    https_only=settings.is_production,
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}