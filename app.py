from fastapi import FastAPI, Depends, HTTPException, Form, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models import User, TempUser 
from database import get_db  
from otp import generate_and_send_otp, verify_otp  

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class OTP_Vertification(BaseModel):
    email: str

# Middleware for authentication
async def get_current_user(request: Request, db: Session = Depends(get_db)):

    if not request:
        raise HTTPException(status_code=500, detail="Invalid request object")

    user_id = request.cookies.get("user_id")  # Get user ID from session (cookie)
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorization")

    # Check if the user exists in the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid session")
    
    return user


# Routes
@app.get("/")
async def redirect_to_login():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})

    # Set user session (cookie)
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)  # HttpOnly cookie for security
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def handle_register(
    request: Request,
    response: Response,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered!"})

    # Validate password confirmation
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Passwords do not match!"}
        )

    # Register the user
    new_user = TempUser(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()

    # Send OTP to the user's email
    generate_and_send_otp(email, db)

    return RedirectResponse(url=f"/verify?id={new_user.id}", status_code=303)


@app.get("/verify", response_class=HTMLResponse)
async def verify(request: Request, id: int, message: str = ""):
    return templates.TemplateResponse(
        "otp_verify.html", {"request": request, "id": id, "message": message}
    )

@app.post("/verify")
async def verify_otp_route(
    request: Request,
    otp: str = Form(...),
    id: int = Form(...),  
    db: Session = Depends(get_db)
):
    user = db.query(TempUser).filter(TempUser.id == id).first()

    if not user:
        raise HTTPException(status_code=400, detail="Email not found in session. Please register first.")
    
    email = user.email

    result = verify_otp(email, otp, db)

    if result:
        # Fetch the user from TempUser (Temporary table)
        temp_user = db.query(TempUser).filter(TempUser.email == email).first()

        if not temp_user:
            raise HTTPException(status_code=400, detail="Temp user not found.")
        
        # Register the user in the User table after OTP verification
        new_user = User(name=temp_user.name, email=temp_user.email, password=temp_user.password)
        db.add(new_user)
        db.commit()

        # Delete the temporary user from TempUser table after registration
        db.delete(temp_user)
        db.commit()

        return RedirectResponse(url="/login", status_code=303)

    raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)  # Ensure the user is authenticated
):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="user_id")  # Remove session cookie
    return response
