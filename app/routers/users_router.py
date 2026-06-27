from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.services.user_service import (
    create_user_service,
    update_user_service,
    get_user_service,
    get_users_list_service,
    update_user_status_service,
    delete_user_service,
)
from app.core.reponse import api_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", response_model=UserResponse, status_code=201)
async def create_user_route(
    user: UserCreate, db=Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        result = await create_user_service(db, user, current_user)
        return api_response(
            success=1,
            status_code=201,
            message="User created successfully",
            result=result,
        )
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user_route(db, user_id: str, user):
    try:
        return await update_user_service(db, user_id, user)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}


@router.get("/get/{user_id}", response_model=UserResponse)
async def get_user_route(db, user_id: str):
    try:
        return await get_user_service(db, user_id)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}


@router.get("/get/list", response_model=UserResponse)
async def get_users_list_route(db, page: int = 1, page_size: int = 10):
    try:
        return await get_users_list_service(db, page, page_size)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}


@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user_route(db, user_id: str):
    try:
        return await delete_user_service(db, user_id)
    except ValueError as e:
        return {"error": str(e)}


@router.put("/{user_id}/udpate/status", response_model=UserResponse, status_code=200)
async def user_update_status_route(db, user_id: str):
    try:
        return await update_user_status_service(db, user_id)
    except ValueError as e:
        return {"error": str(e)}
