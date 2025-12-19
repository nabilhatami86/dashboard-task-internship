from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.config_env import ACCESS_TOKEN_EXPIRE_MINUTES


def register_user(data, db: Session):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    user = User(
        name=data.name,
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Register success",
            "data": {
                "id":user.id,
                "name":user.name,
                "username":user.username,
                "email":user.email,
                "role": user.role.value

            }}


def login_user(data, db: Session):
    user = db.query(User).filter(
        or_(
            User.username == data.identifier,
            User.email == data.identifier
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value
        },
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {
        "message": "Login success",
        "data": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        },
        "access_token": token,
        "token_type": "bearer"
    }
