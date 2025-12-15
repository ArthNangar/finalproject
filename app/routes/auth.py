from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import create_access_token
from app.services.user_service import create_user, authenticate, UserAlreadyExists, InvalidCredentials

router = APIRouter()

@router.post("/auth/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        create_user(db, username=username, email=email, password=password)
    except UserAlreadyExists as e:
        request.state.flash = ("error", str(e))
        return RedirectResponse(url="/register", status_code=303)
    request.state.flash = ("success", "Account created. Please login.")
    return RedirectResponse(url="/login", status_code=303)

@router.post("/auth/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = authenticate(db, username=username, password=password)
    except InvalidCredentials:
        request.state.flash = ("error", "Invalid username or password")
        return RedirectResponse(url="/login", status_code=303)

    token = create_access_token(subject=user.username)
    resp = RedirectResponse(url="/dashboard", status_code=303)
    # Store JWT in HttpOnly cookie
    resp.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=60 * 60,
    )
    return resp

@router.get("/auth/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("access_token")
    return resp