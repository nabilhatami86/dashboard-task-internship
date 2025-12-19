from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.database import engine, Base
from app.config.deps import get_db
from app.routes import auth, category


# create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="ASMI Dashboard API",
    version="0.1.0"
)


@app.on_event("startup")
def startup_db_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL CONNECTED")
    except Exception as e:
        print("❌ PostgreSQL CONNECTION FAILED:", e)


# routes
app.include_router(auth.router)
app.include_router(category.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/db-connect", tags=["Health"])
def db_connect(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "database": "postgresql",
        "status": "connected"
    }
