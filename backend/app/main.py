from fastapi import FastAPI
from .routers import productos
from app.routers import productos

app = FastAPI(
    title="BazarYa API",
    description="API REST para la gestión de productos, usuarios y publicaciones",
    version="1.0.0"
)

# Incluir las rutas del módulo de productos
app.include_router(productos.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de BazarYa"}