from fastapi import FastAPI
from app.database import engine, Base
from app.models import Usuario, Producto, Categoria, ImagenProducto  # Importante para que SQLAlchemy cree las tablas
from app.routers import productos, usuarios, auth

# instancia de la aplicación FastAPI
app = FastAPI(
    title="BazarYa API",
    version="1.0.0",
    description="API oficial para el sistema de moderación y gestión de BazarYa"
)

# 2. Crea las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

# 3. DESPUÉS registras y agrupa todos los routers usando la variable 'app' ya creada
app.include_router(auth.router)
app.include_router(productos.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de BazarYa"}
