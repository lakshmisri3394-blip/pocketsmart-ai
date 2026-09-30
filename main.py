from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .database import init_db
from .auth import get_current_user
from .routes.auth_routes import router as auth_router
from .routes.planner_routes import router as planner_router

app=FastAPI(title="PocketSmart AI", version="1.0.0")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads")
templates=Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html",{"request":request,"user":get_current_user(request)})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html",{"request":request,"user":get_current_user(request)})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html",{"request":request,"user":get_current_user(request)})

@app.get("/dashboard")
def dashboard(request: Request):
    user=get_current_user(request)
    if not user:
        return RedirectResponse("/login",status_code=303)
    return templates.TemplateResponse("dashboard.html",{"request":request,"user":user})

@app.get("/planner/{category}")
def planner(request: Request, category: str):
    user=get_current_user(request)
    if not user:
        return RedirectResponse("/login",status_code=303)
    allowed={"home","party","jewelry"}
    if category not in allowed:
        return RedirectResponse("/dashboard",status_code=303)
    return templates.TemplateResponse(f"{category}.html",{"request":request,"user":user})

@app.get("/history")
def history(request: Request):
    user=get_current_user(request)
    if not user:
        return RedirectResponse("/login",status_code=303)
    from .database import get_db
    with get_db() as db:
        rows=db.execute("""SELECT id,category,budget,input_json,result_json,created_at
                           FROM recommendations WHERE user_id=? ORDER BY id DESC""",(user["id"],)).fetchall()
    return templates.TemplateResponse("history.html",{"request":request,"user":user,"rows":[dict(r) for r in rows]})

app.include_router(auth_router)
app.include_router(planner_router)
