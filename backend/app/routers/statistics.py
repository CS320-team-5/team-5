from fastapi import APIRouter, Path

from services import statistics_service

from models.statistics import (
    StatisticsUserResponse,
    StatisticsCartResponse,
    StatisticsStoreResponse,
    StatisticsEnterpriseResponse
)


# ==========================================
# ROUTER SETUP
# ==========================================

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)


# ==========================================
# USER STATISTICS
# ==========================================

@router.get(
    "/users/{user_id}",
    response_model=StatisticsUserResponse
)
def get_user_statistics(
    user_id: int = Path(..., gt=0)
):
    return statistics_service.get_user_statistics(user_id)


# ==========================================
# CART STATISTICS
# ==========================================

@router.get(
    "/carts/{cart_id}/users/{user_id}",
    response_model=StatisticsCartResponse
)
def get_cart_statistics(
    cart_id: int = Path(..., gt=0),
    user_id: int = Path(..., gt=0)
):
    return statistics_service.get_cart_statistics(
        user_id=user_id,
        cart_id=cart_id
    )


# ==========================================
# STORE STATISTICS
# ==========================================

@router.get(
    "/stores/{store_id}",
    response_model=StatisticsStoreResponse
)
def get_store_statistics(
    store_id: int = Path(..., gt=0)
):
    return statistics_service.get_store_statistics(store_id)


# ==========================================
# ENTERPRISE STATISTICS
# ==========================================

@router.get(
    "/enterprises/{enterprise_name}",
    response_model=StatisticsEnterpriseResponse
)
def get_enterprise_statistics(
    enterprise_name: str
):
    return statistics_service.get_enterprise_statistics(
        enterprise_name
    )
