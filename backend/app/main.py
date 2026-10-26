
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import Usuario, Producto, Categoria, ImagenProducto
from app.routers import productos, usuarios, auth

# Inicializar la aplicación
app = FastAPI(
    title="BazarYa API",
    version="1.0.0",
    description="API oficial para el sistema de moderación y gestión de BazarYa"
)

# Permitir la conexión del frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas si todavía no existen
Base.metadata.create_all(bind=engine)

# Registrar las rutas del sistema
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(usuarios.router)


@app.get("/")
def root():
    return {
        "message": "Bienvenido a la API de BazarYa"
    }
