from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Form
from app.db.session import get_db
from app.routes.deps import get_current_user
from app.services.calc_service import list_calculations, get_stats
from app.services.user_service import update_profile, change_password, UserAlreadyExists, PasswordChangeError

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def _pop_flash(request: Request):
    flash = getattr(request.state, "flash", None)
    if flash:
        request.session["flash"] = flash
    return request.session.pop("flash", None)

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    flash = _pop_flash(request)
    return templates.TemplateResponse("index.html", {"request": request, "flash": flash})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    flash = _pop_flash(request)
    return templates.TemplateResponse("auth/login.html", {"request": request, "flash": flash})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    flash = _pop_flash(request)
    return templates.TemplateResponse("auth/register.html", {"request": request, "flash": flash})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    flash = _pop_flash(request)
    calcs = list_calculations(db, user_id=user.id, limit=20)
    stats = get_stats(db, user_id=user.id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "calcs": calcs,
        "stats": stats,
        "flash": flash
    })

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, user=Depends(get_current_user)):
    flash = _pop_flash(request)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "flash": flash})

@router.post("/profile")
def profile_update(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        update_profile(db, user=user, username=username, email=email)
        request.state.flash = ("success", "Profile updated.")
    except UserAlreadyExists as e:
        request.state.flash = ("error", str(e))
    return RedirectResponse(url="/profile", status_code=303)


@router.post("/profile/password")
def profile_password_change(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if new_password != confirm_password:
        request.state.flash = ("error", "New passwords do not match.")
        return RedirectResponse(url="/profile", status_code=303)
    try:
        change_password(db, user=user, current_password=current_password, new_password=new_password)
        request.state.flash = ("success", "Password changed. Please login again.")
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie("access_token")
        return resp
    except PasswordChangeError as e:
        request.state.flash = ("error", str(e))
        return RedirectResponse(url="/profile", status_code=303)
