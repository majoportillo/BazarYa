from fastapi import FastAPI
from app.database import engine, Base
from app.models import Usuario, Producto, Categoria, ImagenProducto  # <--- IMPORTANTE: Importar los modelos aquí
from app.routers import auth

# Esto lee los modelos importados y crea las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "BazarYa API funcionando"}