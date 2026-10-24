from fastapi import FastAPI
from app.routers import auth, productos
app = FastAPI(
    title="BazarYa API",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(productos.router)

@app.get("/")
def root():
    return {"message": "¡Servidor de BazarYa activo!"}