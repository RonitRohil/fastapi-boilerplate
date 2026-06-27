from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.services.user_service import (
    create_user_service,
    update_user_service,
)


router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user_route(user: UserCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return await create_user_service(db, user, current_user)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}


# @app.put("/users/{user_id}", response_model=UserResponse) 
async def update_user_route(db, user_id: str, user):
    try:
        return await update_user_service(db, user_id, user)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}
