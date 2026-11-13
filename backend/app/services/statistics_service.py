
from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
import pandas as pd
import numpy as np

from app.repositories.statistics_repository import (
    get_users_table,
    get_review_table,
    get_cart_participants_table,
    get_stores_table,
    get_carts_table,
)

from app.models.statistics import (
    StatisticsUserResponse,
    StatisticsCartResponse,
    StatisticsStoreResponse,
    StatisticsEnterpriseResponse,
)


# ==========================================
# ERROR HANDLING
# ==========================================

def error_handler(error: Exception):
    if isinstance(error, HTTPException):
        raise error

    elif isinstance(error, APIError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching statistics."
        ) from error

    elif isinstance(error, RequestError):
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the database."
        ) from error

    elif isinstance(error, ValueError):
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    else:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        ) from error


# ==========================================
# DATAFRAME HELPERS
# ==========================================

def union(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Equivalent to SQL UNION."""
    return pd.concat(
        [df1, df2],
        ignore_index=True
    ).drop_duplicates().reset_index(drop=True)


def join(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    on: str,
    how: str = "inner"
) -> pd.DataFrame:
    """Join two DataFrames on a shared column."""
    return pd.merge(df1, df2, on=on, how=how)


def to_dataframe(response) -> pd.DataFrame:
    """Convert a Supabase APIResponse to a Pandas DataFrame."""
    return pd.DataFrame(response.data)


# ==========================================
# REVIEW STATISTICS
# ==========================================

def avg_rating_of_a_user(user_id: int):
    """Calculate the average rating received by a user."""
    try:
        reviewTable = get_review_table()
        df = to_dataframe(reviewTable)

        if df.empty:
            return None

        ratings = df.loc[
            df["targetuserid"] == user_id,
            "rating"
        ]

        if ratings.empty:
            return None

        return float(np.mean(ratings.to_numpy(dtype=float)))
    
    except Exception as error:
        error_handler(error)


# ==========================================
# CART PARTICIPANT STATISTICS
# ==========================================

def total_spendings_by_user_in_cart(
    user_id: int,
    cart_id: int
):
    """Calculate the user's total contribution to a cart."""
    try:
        participantTable = get_cart_participants_table(cart_id)
        df = to_dataframe(participantTable)

        if df.empty:
            return 0.0

        contributions = df.loc[
            (df["userid"] == user_id) &
            (df["cartid"] == cart_id),
            "amountcontributed"
        ]

        return float(contributions.sum())

    except Exception as error:
        error_handler(error)


def average_contribution_by_user(user_id: int):
    """Calculate a user's average contribution across carts."""
    try:
        participantTable = get_cart_participants_table()
        df = to_dataframe(participantTable)

        if df.empty:
            return None

        contributions = df.loc[
            df["userid"] == user_id,
            "amountcontributed"
        ]

        if contributions.empty:
            return None

        return float(contributions.mean())

    except Exception as error:
        error_handler(error)


def total_spending_of_user(user_id: int):
    """Calculate a user's total contributions across all carts."""
    try:
        participantTable = get_cart_participants_table(
            user_id=user_id
        )

        df = to_dataframe(participantTable)

        if df.empty:
            return 0.0

        contributions = df.loc[
            df["userid"] == user_id,
            "amountcontributed"
        ]

        return float(contributions.sum())

    except Exception as error:
        error_handler(error)


# ==========================================
# STORE STATISTICS
# ==========================================

def total_number_of_locations_per_enterprise(
    enterprise_name: str
) -> int:
    """Count the store records belonging to an enterprise."""
    try:
        storeTable = get_stores_table(enterprise_name)
        df = to_dataframe(storeTable)

        if df.empty:
            return 0

        filtered = df.loc[
            df["enterprisename"] == enterprise_name
        ]

        return int(filtered.shape[0])

    except Exception as error:
        error_handler(error)


def total_open_carts_by_store(store_id: int):
    """Count unique open carts belonging to a store."""
    try:
        cartTable = get_carts_table()
        df = to_dataframe(cartTable)

        if df.empty:
            return 0

        filtered = df.loc[
            (df["storeid"] == store_id) &
            (df["status"] == "open")
        ]

        return int(filtered["cartid"].nunique())

    except Exception as error:
        error_handler(error)


def total_spending_at_store(store_id: int):
    """Calculate total recorded contributions to carts at a store."""
    try:
        cartTable = to_dataframe(get_carts_table())
        participantTable = to_dataframe(
            get_cart_participants_table()
        )

        if cartTable.empty or participantTable.empty:
            return 0.0

        merged = join(
            cartTable,
            participantTable,
            on="cartid"
        )

        contributions = merged.loc[
            merged["storeid"] == store_id,
            "amountcontributed"
        ]

        return float(contributions.sum())

    except Exception as error:
        error_handler(error)

# ==========================================
# RESPONSE BUILDER FUNCTIONS
# ==========================================

def get_user_statistics(user_id: int) -> StatisticsUserResponse:
    return StatisticsUserResponse(
        user_id=user_id,
        total_spending=total_spending_of_user(user_id),
        average_contribution=average_contribution_by_user(user_id),
        average_rating=avg_rating_of_a_user(user_id)
    )


def get_user_cart_statistics(
    user_id: int,
    cart_id: int
) -> StatisticsCartResponse:
    return StatisticsCartResponse(
        cart_id=cart_id,
        user_id=user_id,
        total_contribution=total_spendings_by_user_in_cart(
            user_id,
            cart_id
        )
    )


def get_store_statistics(store_id: int) -> StatisticsStoreResponse:
    return StatisticsStoreResponse(
        store_id=store_id,
        total_open_carts=total_open_carts_by_store(store_id),
        total_spending=total_spending_at_store(store_id)
    )


def get_enterprise_statistics(
    enterprise_name: str
) -> StatisticsEnterpriseResponse:
    return StatisticsEnterpriseResponse(
        enterprise_name=enterprise_name,
        total_locations=total_number_of_locations_per_enterprise(
            enterprise_name
        )
    )
