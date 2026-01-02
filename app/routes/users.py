from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.controller.users_controller import get_all_admins, get_all_agents, get_all_users, update_user_profile
from app.config.deps import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/admins")
def list_admins(db: Session = Depends(get_db)):
    """Get list of all admin users"""
    return get_all_admins(db)

@router.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    """Get list of all agent users"""
    return get_all_agents(db)

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    """Get list of all users"""
    return get_all_users(db)

@router.patch("/{user_id}")
def update_profile(
    user_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Update user profile (name, email, phone)"""
    return update_user_profile(user_id, data, db)
