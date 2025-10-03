from fastapi import FastAPI
from app.api.auth.auth_router import router as auth_router
from app.api.collection_routes.collection_route_router import router as collection_routes_router
from app.api.daily_cutoff.daily_cutoff_router import router as daily_cutoff_router

app = FastAPI(
    title="PayTrack API",
    description="API para gestión de pagos y cobranzas",
    version="1.0.0"
)

# Incluir routers
app.include_router(auth_router)
app.include_router(collection_routes_router)
app.include_router(daily_cutoff_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}