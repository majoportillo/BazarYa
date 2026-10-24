from fastapi import FastAPI
from app.routers import productos, usuarios
from app.routers.auth import router as auth_router
from app.database import engine, Base
from app.models import Usuario, Producto, Categoria, ImagenProducto  # <--- IMPORTANTE: Importar los modelos aquí
from app.routers import auth

# Esto lee los modelos importados y crea las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(productos.router)
app.include_router(usuarios.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de BazarYa"}
