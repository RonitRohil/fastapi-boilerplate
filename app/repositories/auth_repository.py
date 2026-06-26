from app.models.user import User
from app.models.auth import UserSession
from app.schemas.auth import UserSessionCreate, UserSessionResponse

def create_user_session(db, user_session: UserSessionCreate):
    db_user_session = UserSession(**user_session.dict())
    db.add(db_user_session)
    db.commit()
    db.refresh(db_user_session)
    return db_user_session

def get_user_session(db, session_id: str):
    return db.query(UserSession).filter(
        UserSession.session_id == session_id
    ).first()
    
