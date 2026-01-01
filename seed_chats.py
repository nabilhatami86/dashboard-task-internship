"""
Script untuk membuat demo chats dan messages
"""
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.chat import Chat, ChatMode, ChatChannel
from app.models.message import Message, MessageSender, MessageStatus
from app.models.user import User
from datetime import datetime, timedelta


def create_demo_chats():
    db: Session = SessionLocal()

    try:
        # Check if chats already exist
        existing_chats = db.query(Chat).count()
        if existing_chats > 0:
            print(f"ℹ️  {existing_chats} chats already exist. Skipping seed.")
            return

        # Get admin and agent users
        admin = db.query(User).filter(User.username == "admin").first()
        agent = db.query(User).filter(User.username == "agent").first()

        if not admin or not agent:
            print("❌ Admin or Agent user not found. Please run seed_users.py first")
            return

        print("Creating demo chats...")

        # Chat 1: Active chat with agent assigned
        chat1 = Chat(
            customer_name="John Doe",
            customer_phone="+62 812-3456-7890",
            customer_email="john.doe@email.com",
            customer_address="Jakarta Selatan",
            channel=ChatChannel.whatsapp,
            mode=ChatMode.agent,
            online=True,
            unread_count=2,
            assigned_agent_id=agent.id,
            last_message_at=datetime.now(),
        )
        db.add(chat1)
        db.flush()

        # Messages for chat 1
        messages1 = [
            Message(
                chat_id=chat1.id,
                text="Halo, saya butuh bantuan!",
                sender=MessageSender.customer,
                status=MessageStatus.read,
                created_at=datetime.now() - timedelta(minutes=10),
            ),
            Message(
                chat_id=chat1.id,
                text="Halo! Ada yang bisa kami bantu?",
                sender=MessageSender.agent,
                status=MessageStatus.sent,
                agent_id=agent.id,
                created_at=datetime.now() - timedelta(minutes=9),
            ),
            Message(
                chat_id=chat1.id,
                text="Saya ingin tanya tentang produk Anda",
                sender=MessageSender.customer,
                status=MessageStatus.sent,
                created_at=datetime.now() - timedelta(minutes=1),
            ),
        ]
        for msg in messages1:
            db.add(msg)

        # Chat 2: Bot mode chat
        chat2 = Chat(
            customer_name="Sarah Williams",
            customer_phone="+1 555-0123",
            customer_email="sarah.w@email.com",
            customer_address="New York, USA",
            channel=ChatChannel.whatsapp,
            mode=ChatMode.bot,
            online=False,
            unread_count=0,
            last_message_at=datetime.now() - timedelta(hours=2),
        )
        db.add(chat2)
        db.flush()

        # Messages for chat 2
        messages2 = [
            Message(
                chat_id=chat2.id,
                text="Halo",
                sender=MessageSender.customer,
                status=MessageStatus.read,
                created_at=datetime.now() - timedelta(hours=2, minutes=5),
            ),
            Message(
                chat_id=chat2.id,
                text="Halo 👋 ada yang bisa kami bantu?",
                sender=MessageSender.agent,
                status=MessageStatus.sent,
                created_at=datetime.now() - timedelta(hours=2),
            ),
        ]
        for msg in messages2:
            db.add(msg)

        # Chat 3: Unassigned chat
        chat3 = Chat(
            customer_name="Maria Lopez",
            customer_phone="+34 612-998-221",
            customer_email="maria@email.com",
            customer_address="Madrid, Spain",
            channel=ChatChannel.whatsapp,
            mode=ChatMode.bot,
            online=True,
            unread_count=1,
            last_message_at=datetime.now() - timedelta(minutes=30),
        )
        db.add(chat3)
        db.flush()

        # Messages for chat 3
        messages3 = [
            Message(
                chat_id=chat3.id,
                text="Apakah pesanan saya sudah dikirim?",
                sender=MessageSender.customer,
                status=MessageStatus.sent,
                created_at=datetime.now() - timedelta(minutes=30),
            ),
        ]
        for msg in messages3:
            db.add(msg)

        # Chat 4: Paused chat
        chat4 = Chat(
            customer_name="Ahmed Hassan",
            customer_phone="+971 50-123-4567",
            customer_email="ahmed.h@email.com",
            customer_address="Dubai, UAE",
            channel=ChatChannel.telegram,
            mode=ChatMode.paused,
            online=False,
            unread_count=0,
            assigned_agent_id=agent.id,
            last_message_at=datetime.now() - timedelta(days=1),
        )
        db.add(chat4)
        db.flush()

        # Messages for chat 4
        messages4 = [
            Message(
                chat_id=chat4.id,
                text="I need some time to think about it",
                sender=MessageSender.customer,
                status=MessageStatus.read,
                created_at=datetime.now() - timedelta(days=1),
            ),
            Message(
                chat_id=chat4.id,
                text="Sure, take your time. Let us know when you're ready!",
                sender=MessageSender.agent,
                status=MessageStatus.sent,
                agent_id=agent.id,
                created_at=datetime.now() - timedelta(days=1),
            ),
        ]
        for msg in messages4:
            db.add(msg)

        # Commit all changes
        db.commit()

        print("\n✅ Demo chats created successfully!")
        print("\nDemo Chats:")
        print("1. John Doe (Agent mode, 2 unread) - Assigned to agent")
        print("2. Sarah Williams (Bot mode, 0 unread)")
        print("3. Maria Lopez (Bot mode, 1 unread) - Unassigned")
        print("4. Ahmed Hassan (Paused, 0 unread) - Assigned to agent")
        print("\n🎉 You can now test the chat functionality!")

    except Exception as e:
        print(f"❌ Error creating demo chats: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_chats()
