from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from .models import RolUsuario, EstadoProducto

# ==========================================
# 1. ESQUEMAS DE CATEGORÍAS
# ==========================================
class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


# ==========================================
# 2. ESQUEMAS DE USUARIOS
# ==========================================
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


# ==========================================
# 3. ESQUEMAS DE PRODUCTOS / PUBLICACIONES
# ==========================================
class ImagenProductoCreate(BaseModel):
    url_imagen: str = Field(..., min_length=5, description="URL o cadena Base64 de la imagen")
    es_principal: bool = False


class ImagenProductoResponse(BaseModel):
    id: int
    url_imagen: str
    es_principal: bool

    class Config:
        from_attributes = True


class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, description="AC-02: Título del producto")
    descripcion: str = Field(..., min_length=10, description="AC-03: Descripción detallada")
    precio: float = Field(..., gt=0, description="AC-04: Precio positivo mayor a cero")
    categoria_id: int = Field(..., gt=0, description="AC-05: ID de categoría válido")
    imagenes: List[ImagenProductoCreate] = Field(..., min_items=1, description="AC-06: Requiere al menos una imagen")

    @field_validator("nombre", "descripcion", mode="before")
    @classmethod
    def strip_and_validate_strings(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean:
                raise ValueError("El campo no puede estar vacío ni contener solo espacios")
            return v_clean
        return v


class ProductoResponse(BaseModel):
    id: int
    usuario_id: UUID
    categoria: CategoriaResponse
    nombre: str
    descripcion: str
    precio: float
    stock: int
    estado: EstadoProducto
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    imagenes: List[ImagenProductoResponse]

    class Config:
        from_attributes = True