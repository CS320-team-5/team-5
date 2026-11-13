from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
from supabase import Client as sb
#todo: Implement repository methods for statistics-related queries



#user related statistics methods
def get_users_table(user_id: int | None = None):
    # Implement the logic to fetch all users' statistics from the database
    
    if(user_id is not None):

        return sb.table("users").select("*").eq("userid", user_id).execute()
    
    return sb.table("users").select("*").execute()

#cart related statistics methods
def get_carts_table(cart_id: int | None = None):
    # Implement the logic to fetch all carts' statistics from the database
    if(cart_id is not None):

        return sb.table("cart").select("*").eq("cartid", cart_id).execute()
    
    return sb.table("cart").select("*").execute()

#store related statistics methods
def get_stores_table(store_id: int | None = None, enterprise_name: str | None = None):
    # Implement the logic to fetch store statistics from the database
    if(store_id is not None):

        return sb.table("store").select("*").eq("storeid", store_id).execute()
    
    if(enterprise_name is not None):

        return sb.table("store").select("*").eq("enterprisename", enterprise_name).execute()
    
    return sb.table("store").select("*").execute()

def get_cart_participants_table(cart_id: int | None = None, user_id: int | None = None):
    # Implement the logic to fetch cart participant statistics from the database
    if(cart_id is not None and user_id is not None):

        return sb.table("cartparticipant").select("*").eq("cartid", cart_id).eq("userid", user_id).execute()
    
    if(cart_id is not None):

        return sb.table("cartparticipant").select("*").eq("cartid", cart_id).execute()
    
    if(user_id is not None):

        return sb.table("cartparticipant").select("*").eq("userid", user_id).execute()
    
    return sb.table("cartparticipant").select("*").execute()

def get_review_table(review_id: int | None = None, target_user_id: int | None = None):
    # Implement the logic to fetch review statistics from the database
    if(review_id is not None and target_user_id is not None):

        return sb.table("review").select("*").eq("id", review_id).eq("targetuserid", target_user_id).execute()
    
    if(review_id is not None):

        return sb.table("review").select("*").eq("id", review_id).execute()
    
    if(target_user_id is not None):

        return sb.table("review").select("*").eq("targetuserid", target_user_id).execute()
    
    return sb.table("review").select("*").execute()