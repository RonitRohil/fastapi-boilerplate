from app.models.user import User
from app.models.auth import UserSession, UserToken
from app.schemas.auth import UserSessionCreate, UserSessionResponse, AddUserToken
from datetime import datetime


async def create_user_session(db, user_session: UserSessionCreate):
    db_user_session = UserSession(**user_session.dict())
    db.add(db_user_session)
    db.commit()
    db.refresh(db_user_session)
    return db_user_session


async def get_user_session(db, session_id: str):
    return db.query(UserSession).filter(UserSession.session_id == session_id).first()


async def revoke_user_session(db, session_id: str):
    user_session = await get_user_session(db, session_id)
    if user_session:
        user_session.revoked_at = datetime.utcnow()
        db.commit()


async def add_user_token(db, user_token: AddUserToken):
    db_user_token = UserToken(**user_token.dict())
    db.add(db_user_token)
    db.commit()
    db.refresh(db_user_token)
    return db_user_token