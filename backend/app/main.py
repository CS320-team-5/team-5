from fastapi import FastAPI
from .cart import router as cart_router

app = FastAPI()
app.include_router(cart_router)

@app.get("/")
def read_root():
    return {"message": "CoCart API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
