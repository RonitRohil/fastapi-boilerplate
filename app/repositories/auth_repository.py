from app.models.auth import UserSession, UserToken
from app.schemas.auth import UserSessionCreate, AddUserToken
from datetime import datetime, timezone


def create_user_session_no_commit(db, user_session: UserSessionCreate):
    db_user_session = UserSession(
        user_id=user_session.user_id,
        session_id=user_session.session_id,
        device_name=user_session.device_name,
        user_agent=user_session.user_agent,
        ip_address=user_session.ip_address,
        expires_at=user_session.expires_at,
    )
    db.add(db_user_session)
    return db_user_session


def get_user_session(db, session_id: str):
    return db.query(UserSession).filter(UserSession.session_id == session_id).first()


def revoke_user_session_no_commit(db, session_id: str):
    user_session = get_user_session(db, session_id)
    if user_session:
        user_session.revoked_at = datetime.now(timezone.utc)
    return user_session


def revoke_all_user_sessions_no_commit(db, user_id: str):
    user_sessions = db.query(UserSession).filter(UserSession.user_id == user_id).all()
    for user_session in user_sessions:
        user_session.revoked_at = datetime.now(timezone.utc)
    return user_sessions


def add_user_token_no_commit(db, user_token: AddUserToken):
    db_user_token = UserToken(
        jti=user_token.jti,
        user_id=user_token.user_id,
        session_id=user_token.session_id,
        token_type=user_token.token_type,
        expires_at=user_token.expires_at,
    )
    db.add(db_user_token)
    return db_user_token


def get_user_token_with_jti(db, jti: str):
    return db.query(UserToken).filter(UserToken.jti == jti).first()


def revoke_all_user_tokens_no_commit(db, user_id: str):
    user_tokens = db.query(UserToken).filter(UserToken.user_id == user_id).all()
    for user_token in user_tokens:
        user_token.revoked_at = datetime.now(timezone.utc)
    return user_tokens


def revoke_user_token_no_commit(db, jti: str):
    user_token = db.query(UserToken).filter(UserToken.jti == jti).first()
    if user_token:
        user_token.revoked_at = datetime.now(timezone.utc)
    return user_token
