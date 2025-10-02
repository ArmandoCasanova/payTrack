from fastapi import FastAPI
from app.api.auth.auth_router import router as auth_router

app = FastAPI(
    title="PayTrack API",
    description="API para gestión de pagos",
    version="1.0.0"
)

# Incluir routers
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}