from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # 1. Import HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM
from app.dependencies import get_db
from app import models

# 2. Use HTTPBearer instead of OAuth2PasswordBearer
security = HTTPBearer()

# 3. Update get_current_user to accept credentials
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 4. Extract the token string from the credentials object
    token = credentials.credentials

    # Check if token is revoked
    if db.query(models.RevokedToken).filter(models.RevokedToken.token == token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Remember our previous fix: use email here if you followed Option A, or user_id for Option B
        email: str | None = payload.get("sub") 
        
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ensure this query matches your 'sub' claim (email vs id)
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user