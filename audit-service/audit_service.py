"""
app/services/audit_service.py
-----------------------------
Handles configuring the SQLite DB and inserting Audit Log records.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from shared.models.audit_models import Base, AuditLog

# Create DB near ChromaDB inside the data folder
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render and Heroku use 'postgres://' but SQLAlchemy requires 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, "audit_logs.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Check if reg_no exists in audit_logs table, if not add it dynamically (SQLite schema migration)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    try:
        columns = [col['name'] for col in inspector.get_columns('audit_logs')]
        if 'reg_no' not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE audit_logs ADD COLUMN reg_no VARCHAR(50)"))
            print("Successfully added reg_no column to audit_logs table.")
    except Exception as e:
        print(f"Failed to check/migrate audit_logs table schema: {e}")

def insert_audit_log(role: str, query: str, intent: str, risk_level: str, confidence_score: str, decision: str, needs_review: bool, reg_no: str = None):
    """
    Inserts a newly completed multi-agent workflow into the local DB.
    """
    db = SessionLocal()
    try:
        log_entry = AuditLog(
            user_role=role,
            query=query,
            intent=intent,
            risk_level=risk_level,
            confidence_score=confidence_score,
            decision_summary=decision,
            needs_review=1 if needs_review else 0,
            reg_no=reg_no
        )
        db.add(log_entry)
        db.commit()

    except Exception as e:
        print(f"Failed to write audit log: {e}")
        db.rollback()
    finally:
        db.close()
