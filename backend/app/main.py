from fastapi import FastAPI
from app.routers.auth import router as auth_router  # Ajusta la ruta según tu estructura de carpetas

app = FastAPI(title="BazarYa API", version="1.0.0")

# Incluimos las rutas de autenticación
app.include_router(auth_router)