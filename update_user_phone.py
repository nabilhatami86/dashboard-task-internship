"""
Script untuk update nomor telepon user dengan ID tertentu
"""
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.user import User

def update_user_phone(user_id: int, phone: str):
    db: Session = SessionLocal()
    try:
        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            print(f"❌ User dengan ID {user_id} tidak ditemukan")
            return False

        # Update phone
        user.phone = phone
        db.commit()
        db.refresh(user)

        print(f"✅ Berhasil update user {user.name} (ID: {user_id})")
        print(f"   Email: {user.email}")
        print(f"   Phone: {user.phone}")
        print(f"   Role: {user.role.value}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Update admin (ID 1) dengan nomor WhatsApp admin
    update_user_phone(user_id=1, phone="087731624016")

    # Update agent (ID 2) dengan nomor agent
    update_user_phone(user_id=2, phone="081234567890")
