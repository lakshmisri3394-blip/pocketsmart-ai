from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from ..database import get_db
from ..auth import hash_password, verify_password, create_access_token

router=APIRouter()

@router.post("/register")
def register(request: Request, name: str=Form(...), email: str=Form(...), password: str=Form(...)):
    email=email.strip().lower()
    with get_db() as db:
        existing=db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            return RedirectResponse("/register?error=Email+already+registered",status_code=303)
        db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                   (name.strip(),email,hash_password(password)))
    return RedirectResponse("/login?success=Account+created",status_code=303)

@router.post("/login")
def login(request: Request, email: str=Form(...), password: str=Form(...)):
    with get_db() as db:
        user=db.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if not user or not verify_password(password,user["password_hash"]):
        return RedirectResponse("/login?error=Invalid+email+or+password",status_code=303)
    token=create_access_token(user["id"])
    response=RedirectResponse("/dashboard",status_code=303)
    response.set_cookie("access_token",token,httponly=True,samesite="lax",max_age=43200)
    return response

@router.get("/logout")
def logout():
    response=RedirectResponse("/",status_code=303)
    response.delete_cookie("access_token")
    return response
