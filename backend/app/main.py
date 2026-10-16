from fastapi import Depends, FastAPI

from .auth import AuthSession, get_auth_session
from .cart import router as cart_router


app = FastAPI()

app.include_router(cart_router)


@app.get("/")
def read_root():
    return {"message": "CoCart API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/auth/test")
def auth_test(
    session: AuthSession = Depends(get_auth_session),
):
    return {
        "authenticated": True,
        "auth_id": session.auth_id,
        "user_id": session.user_id,
    }