import asyncio # Required for running async email in sync route
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError

from app import models, schemas, security, config
from app.dependencies import get_db
from app.dependencies_auth import get_current_user

# Import the email service
from app.services.email_service import send_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Use HTTPBearer for a simple token input in Swagger
http_bearer = HTTPBearer()

# Helper to set the cookie
def set_refresh_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,      # JavaScript cannot read this
        secure=False,       # Set True if you are using HTTPS (Production)
        samesite="lax",     # CSRF protection
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

# ---------------------------
# REGISTER
# ---------------------------
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )

    new_user = models.User(
        email=user.email,
        hashed_password=security.hash_password(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------------------------
# LOGIN
# ---------------------------
@router.post("/login", response_model=schemas.Token)
def login(
    response: Response,
    form_data: schemas.UserLogin, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.email
    ).first()

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = security.create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    refresh_token = security.create_refresh_token(
        data={"sub": user.email}
    )

    # Set the HttpOnly cookie
    set_refresh_token_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------------------
# REFRESH TOKEN
# ---------------------------
@router.post("/refresh")
def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    # Read token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(
            refresh_token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check if user still exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
         raise HTTPException(status_code=401, detail="User not found")

    new_access_token = security.create_access_token(
        {"sub": email, "role": user.role},
        timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# ---------------------------
# LOGOUT
# ---------------------------
@router.post("/logout")
def logout(
    response: Response,
    credentials: HTTPBearer = Depends(http_bearer),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Extract token string
    token = credentials.credentials
    
    # Add to revoked list
    db.add(models.RevokedToken(token=token))
    db.commit()

    # Clear the cookie
    response.delete_cookie(key="refresh_token")

    return {"message": "Logged out successfully"}


# ---------------------------
# FORGOT PASSWORD (PRODUCTION EMAIL INTEGRATION)
# ---------------------------
@router.post("/forgot-password")
def forgot_password(
    request: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()

    # Security: Always return 200 OK, even if user doesn't exist.
    if not user:
        return {"message": "If that email exists, a reset link has been sent."}

    # Generate Token
    reset_token = security.create_password_reset_token(
        data={"sub": user.email}
    )

    # SEND EMAIL PRODUCTION
    # FastAPI routes are synchronous by default. We run the async email function 
    # in the event loop. This sends the email without blocking the API response.
    try:
        asyncio.run(send_reset_email(user.email, reset_token))
        print(f"✅ Email dispatched to {user.email}")
    except Exception as e:
        # Log error but don't crash API
        print(f"❌ Failed to send email: {e}")
        # In prod, you might use Sentry here.

    return {"message": "If that email exists, a reset link has been sent."}


# ---------------------------
# RESET PASSWORD
# ---------------------------
@router.post("/reset-password")
def reset_password(
    body: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            body.token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        
        token_type = payload.get("type")
        if token_type != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")

        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Basic Validation
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = security.hash_password(body.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}