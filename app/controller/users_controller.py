from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User, UserRole


def get_all_admins(db: Session):
    """Get all admin users"""
    admins = db.query(User).filter(User.role == UserRole.admin).all()

    return [
        {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "phone": admin.phone,
            "username": admin.username,
            "role": admin.role.value,
            "online": False  # TODO: Implement online status tracking
        }
        for admin in admins
    ]


def get_all_agents(db: Session):
    """Get all agent users"""
    agents = db.query(User).filter(User.role == UserRole.agent).all()

    return [
        {
            "id": agent.id,
            "name": agent.name,
            "email": agent.email,
            "phone": agent.phone,
            "username": agent.username,
            "role": agent.role.value,
            "online": False  # TODO: Implement online status tracking
        }
        for agent in agents
    ]


def get_all_users(db: Session):
    """Get all users"""
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "username": user.username,
            "role": user.role.value,
            "online": False  # TODO: Implement online status tracking
        }
        for user in users
    ]


def update_user_profile(user_id: int, data: dict, db: Session):
    """Update user profile (name, email, phone)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if "name" in data and data["name"]:
        user.name = data["name"]

    if "email" in data and data["email"]:
        # Check if email is already taken by another user
        existing = db.query(User).filter(
            User.email == data["email"],
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = data["email"]

    if "phone" in data:
        user.phone = data["phone"]

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "username": user.username,
            "role": user.role.value
        }
    }
