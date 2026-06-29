from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserListResponse
from app.services.user_service import (
    create_user_service,
    update_user_service,
    get_user_service,
    get_users_list_service,
    update_user_status_service,
    delete_user_service,
)
from app.core.response import api_response

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
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user_route(
    user: UserUpdate,
    user_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await update_user_service(db, user_id, user, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{user_id}", response_model=UserResponse)
async def get_user_by_id_route(db=Depends(get_db), user_id: str = None):
    try:
        user = await get_user_service(db, user_id)
        return api_response(
            success=1,
            status_code=200,
            message="User details fetched successfully",
            result=user,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/list", response_model=UserListResponse)
async def get_users_list_route(
    db, page: int = 1, page_size: int = 10, filters: dict = {}
):
    try:
        users_list = await get_users_list_service(db, page, page_size, filters)
        return api_response(
            success=1,
            status_code=200,
            message="Users fetched successfully",
            result=users_list,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user_route(db, user_id: str, current_user=Depends(get_current_user)):
    try:
        delete_user = await delete_user_service(db, user_id, current_user)
        return api_response(
            success=1,
            status_code=200,
            message="User deleted successfully",
            result=delete_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}/update/status", response_model=UserResponse, status_code=200)
async def user_update_status_route(
    db, user_id: str, current_user=Depends(get_current_user)
):
    try:
        update_user_status = await update_user_status_service(db, user_id, current_user)

        return api_response(
            success=1,
            status_code=200,
            message="User status updated successfully",
            result=update_user_status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
