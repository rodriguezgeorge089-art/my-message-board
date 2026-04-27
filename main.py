import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-me")

templates = Jinja2Templates(directory="templates")

# Helper: get current user from session
def get_current_user(request: Request):
    token = request.session.get("access_token")
    refresh = request.session.get("refresh_token")
    if not token or not refresh:
        return None
    try:
        supabase.auth.set_session(token, refresh)
        user = supabase.auth.get_user()
        return user.user
    except:
        return None

# ----- Authentication Pages -----

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def do_signup(request: Request, email: str = Form(...), password: str = Form(...),
                    full_name: str = Form(...), role: str = Form(...)):
    try:
        resp = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })
        user = resp.user
        if user:
            supabase.table("profiles").update({"role": role}).eq("user_id", user.id).execute()
            return RedirectResponse(url="/login?message=Account+created", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": str(e)})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, message: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
async def do_login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        request.session["access_token"] = resp.session.access_token
        request.session["refresh_token"] = resp.session.refresh_token
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    profile = supabase.table("profiles").select("*").eq("user_id", user.id).single().execute()
    user_role = profile.data['role']
    full_name = profile.data.get('full_name', 'User')
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "full_name": full_name,
        "role": user_role
    })

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/")
async def root():
    return RedirectResponse(url="/login")
