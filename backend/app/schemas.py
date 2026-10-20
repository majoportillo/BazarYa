from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from models import RolUsuario

class UsuarioCreate(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    telefono: str
    fotografia_url: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: UUID
    nombre_completo: str
    email: EmailStr
    telefono: str
    fotografia_url: Optional[str]
    rol: RolUsuario
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True