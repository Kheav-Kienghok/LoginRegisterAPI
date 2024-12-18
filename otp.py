import smtplib
import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from models import TempUser

# Load environment variables
load_dotenv()

# Retrieve email and password from .env
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Function to generate OTP
def generate_otp(length=6):
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


# Function to send OTP via email
def send_otp_email(user_email: str, otp: str):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtpserver:
            smtpserver.login(SENDER_EMAIL, PASSWORD)
            smtpserver.sendmail(SENDER_EMAIL, user_email, f"Subject: Your OTP\n\nThis is your OTP: {otp}")
        return "OTP sent successfully!"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")


# Function to generate and send OTP
def generate_and_send_otp(user_email: str, db: Session):

    user = db.query(TempUser).filter(TempUser.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=2)  # OTP expires in 2 minutes

    user.otp = otp
    user.otp_expiry = otp_expiry
    db.commit()

    return send_otp_email(user_email, otp)

def verify_otp(email: str, otp: str, db: Session):
    user = db.query(TempUser).filter(TempUser.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found.")
    
    if not user.otp or not user.otp_expiry:
        raise HTTPException(status_code=400, detail="No OTP found. Please request a new OTP.")
    
    if datetime.now() > user.otp_expiry:
        db.delete(user)  
        db.commit()  
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new OTP.")

    if int(otp) == user.otp:
        return True
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")


