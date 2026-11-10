from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
from supabase import Client as sb
#todo: Implement repository methods for statistics-related queries



#user related statistics methods
def get_all_users_table(user_id: int | None = None):
    # Implement the logic to fetch all users' statistics from the database
    
    if(user_id is not None):
        return sb.table("users").select("*").eq("id", user_id).execute()
    return sb.table("users").select("*").execute()

#cart related statistics methods
def get_all_carts_table(cart_id: int | None = None):
    # Implement the logic to fetch all carts' statistics from the database
    if(cart_id is not None):
        return sb.table("carts").select("*").eq("id", cart_id).execute()
    return sb.table("carts").select("*").execute()

#store related statistics methods
def get_store_table(store_id: int | None = None, enterprise_name: str | None = None):
    # Implement the logic to fetch store statistics from the database
    if(store_id is not None):
        return sb.table("store").select("*").eq("storeid", store_id).execute()
    if(enterprise_name is not None):
        return sb.table("store").select("*").eq("enterprisename", enterprise_name).execute()
    return sb.table("store").select("*").execute()
