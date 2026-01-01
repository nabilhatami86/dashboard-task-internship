"""
Script untuk membuat akun admin dan agent demo
"""
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password


def create_demo_users():
    db: Session = SessionLocal()

    try:
        # Cek apakah user sudah ada
        admin_exists = db.query(User).filter(User.username == "admin").first()
        agent_exists = db.query(User).filter(User.username == "agent").first()

        # Buat admin user jika belum ada
        if not admin_exists:
            admin_user = User(
                name="Admin User",
                email="admin@example.com",
                username="admin",
                password=hash_password("admin123"),
                role=UserRole.admin
            )
            db.add(admin_user)
            print("✅ Admin user created: admin / admin123")
        else:
            print("ℹ️  Admin user already exists")

        # Buat agent user jika belum ada
        if not agent_exists:
            agent_user = User(
                name="Agent User",
                email="agent@example.com",
                username="agent",
                password=hash_password("agent123"),
                role=UserRole.agent
            )
            db.add(agent_user)
            print("✅ Agent user created: agent / agent123")
        else:
            print("ℹ️  Agent user already exists")

        # Commit changes
        db.commit()
        print("\n🎉 Demo users setup completed!")
        print("\nCredentials:")
        print("Admin — admin | admin123")
        print("Agent — agent | agent123")

    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()
