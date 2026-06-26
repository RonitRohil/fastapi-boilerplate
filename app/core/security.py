import jwt
from datetime import datetime, timedelta
from app.core.config import settings


def hash_password(password: str) -> str:
    import bcrypt

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def encode_access_token(user: dict) -> str:
    payload = {
        "sub": user["id"],
        "user_details": {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"],
            "is_active": user["is_active"],
            "is_verified": user["is_verified"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "created_by": user["created_by"],
            "updated_by": user["updated_by"],
        },
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
