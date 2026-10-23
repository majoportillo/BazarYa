from pydantic import BaseModel, model_validator, EmailStr, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from .models import RolUsuario, EstadoProducto
import html
from decimal import Decimal

# ==========================================
# ESQUEMAS DE CATEGORÍAS
# ==========================================

class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True

# ==========================================
# ESQUEMAS DE USUARIOS
# ==========================================

# Entrada: Registro de Usuario (AC-02, AC-06 de BYA-43)
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


# Salida: Respuesta de Perfil (Segura sin password)
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
# ESQUEMAS DE PRODUCTOS / PUBLICACIONES
# ==========================================

# Sub-esquema para imágenes del producto (AC-06)
class ImagenProductoCreate(BaseModel):
    url_imagen: str = Field(..., min_length=5, description="URL o cadena Base64 de la imagen")
    es_principal: bool = False

    @field_validator("url_imagen", mode="before")
    @classmethod
    def sanear_url(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

class ImagenProductoResponse(BaseModel):
    id: int
    url_imagen: str
    es_principal: bool

    class Config:
        from_attributes = True


# Entrada: Crear Publicación (AC-02, AC-03, AC-04, AC-05, AC-06, AC-10)
class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150, description="Título del producto")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada")
    precio: float = Field(..., gt=0, description="Precio positivo mayor a cero")
    stock: int = Field(1, ge=1, description="Cantidad inicial disponible")
    categoria_id: int = Field(..., gt=0, description="ID de categoría válido")
    imagenes: List[ImagenProductoCreate] = Field(..., min_items=1, max_items=5, description="Requiere al menos una imagen, máximo 5")

    @field_validator("nombre", "descripcion", mode="before")
    @classmethod
    def strip_and_validate_strings(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean:
                raise ValueError("El campo no puede estar vacío ni contener solo espacios")
            return html.escape(v_clean)
        return v
    
    # Regla de Negocio: Garantizar que exista exactamente una imagen principal
    @model_validator(mode="after")
    def validar_imagen_principal(self):
        if self.imagenes:
            principales = [img for img in self.imagenes if img.es_principal]
            if len(principales) == 0:
                # Asigna la primera imagen como principal por defecto
                self.imagenes[0].es_principal = True
            elif len(principales) > 1:
                raise ValueError("Solo una imagen puede ser marcada como principal.")
        return self


# Salida: Respuesta de Publicación (Devuelve estado PENDING inicial por AC-07)
class ProductoResponse(BaseModel):
    id: int
    usuario_id: UUID  # AC-09: Asociado al creador
    categoria: CategoriaResponse
    nombre: str
    descripcion: str
    precio: Decimal
    stock: int
    estado: EstadoProducto  # Vendrá como 'PENDING'
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    imagenes: List[ImagenProductoResponse]

    class Config:
        from_attributes = True