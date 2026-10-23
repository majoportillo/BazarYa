from fastapi import FastAPI
from app.routers import productos, usuarios
from app.routers.auth import router as auth_router

app = FastAPI(
    title="BazarYa API",
    description="API REST para la gestión de productos, usuarios y publicaciones",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(productos.router)
app.include_router(usuarios.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de BazarYa"}