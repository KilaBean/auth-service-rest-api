from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies_auth import get_current_user, require_admin
from app.dependencies import get_db
from app import models
from app.schemas import UserOut

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user

# --- NEW PROMOTE ENDPOINT ---
@router.post("/promote/{user_id}")
def promote_user_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    # Only allow this if the requester is already an admin
    current_admin=Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = "admin"
    db.commit()
    
    return {"message": f"User {user.email} has been promoted to admin"}

@router.get("/admin-only")
def admin_dashboard(admin=Depends(require_admin)):
    return {"message": "Welcome admin"}