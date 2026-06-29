from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import (
    get_db,
    get_current_user,
    require_admin,
    verify_csrf_token,
)
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserSelfUpdate,
    UserUpdate,
)
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


def serialize_user(orm_user) -> dict:
    return UserResponse.model_validate(orm_user).model_dump(mode="json")


def serialize_users(orm_users: list) -> list:
    return [serialize_user(u) for u in orm_users]


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return api_response(
        success=1,
        status_code=200,
        message="User profile fetched successfully",
        result=serialize_user(current_user),
    )


@router.put("/update/me")
async def update_user_self(
    user: UserSelfUpdate,
    db=Depends(get_db),
    _=Depends(verify_csrf_token),
    current_user=Depends(get_current_user),
):
    try:
        updated = await update_user_service(
            db, str(current_user.id), user, current_user
        )
        return api_response(
            success=1,
            status_code=200,
            message="User updated successfully",
            result=serialize_user(updated),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", status_code=201)
async def create_user_route(
    user: UserCreate,
    db=Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        result = await create_user_service(db, user, current_user)
        return api_response(
            success=1,
            status_code=201,
            message="User created successfully",
            result=serialize_user(result),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{user_id}")
async def update_user_route(
    user: UserUpdate,
    user_id: str,
    db=Depends(get_db),
    _=Depends(verify_csrf_token),
    current_user=Depends(require_admin),
):
    try:
        updated = await update_user_service(db, user_id, user, current_user)
        return api_response(
            success=1,
            status_code=200,
            message="User updated successfully",
            result=serialize_user(updated),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/list")
async def get_users_list_route(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
    role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    try:
        filters = {"role": role, "is_active": is_active, "is_verified": is_verified}
        users_list = await get_users_list_service(db, page, page_size, filters)
        users_list["users"] = serialize_users(users_list["users"])

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


@router.get("/get/{user_id}")
async def get_user_by_id_route(
    user_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user = await get_user_service(db, user_id)
        return api_response(
            success=1,
            status_code=200,
            message="User details fetched successfully",
            result=serialize_user(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{user_id}")
async def delete_user_route(
    user_id: str,
    db=Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        deleted = await delete_user_service(db, user_id, current_user)
        return api_response(
            success=1,
            status_code=200,
            message="User deleted successfully",
            result=serialize_user(deleted),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}/update/status")
async def user_update_status_route(
    user_id: str,
    db=Depends(get_db),
    _=Depends(verify_csrf_token),
    current_user=Depends(require_admin),
):
    try:
        updated = await update_user_status_service(db, user_id, current_user)
        return api_response(
            success=1,
            status_code=200,
            message="User status updated successfully",
            result=serialize_user(updated),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
