from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from .models import RolUsuario

class UsuarioCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    telefono: str = Field(..., min_length=8, max_length=20)
    fotografia_url: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

class UsuarioResponse(BaseModel):
    id: UUID
    nombre_completo: str
    email: EmailStr
    telefono: str
    fotografia_url: Optional[str]
    rol: RolUsuario
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True