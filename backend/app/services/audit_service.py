from sqlalchemy.orm import Session
from typing import Optional
from app.models.audit_log import AuditLog
from app.models.user import User
from app.database.connection import SessionLocal

def record_audit(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    user: Optional[User] = None,
    username: Optional[str] = None,
    role: Optional[str] = None,
    ip_address: Optional[str] = None,
    db: Optional[Session] = None
):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        u_id = user.id if user else None
        u_name = user.username if user else (username or "SYSTEM")
        u_role = user.role if user else (role or "SYSTEM")

        log = AuditLog(
            user_id=u_id,
            username=u_name,
            role=u_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Error recording audit log: {e}")
    finally:
        if should_close:
            db.close()
