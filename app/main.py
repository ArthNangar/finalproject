from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.routes import auth, pages, api

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(api.router)

    @app.middleware("http")
    async def flash_middleware(request: Request, call_next):
        response = await call_next(request)
        return response

    @app.on_event("startup")
    def _startup():
        init_db()

    return app

app = create_app()
