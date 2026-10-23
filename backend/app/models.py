import enum
import uuid
from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from app.database import Base

Base = declarative_base()

# ==========================================
# ENUMS DEL SYSTEMA
# ==========================================
class RolUsuario(str, enum.Enum):
    COMPRADOR_VENDEDOR = "COMPRADOR_VENDEDOR"
    ADMINISTRADOR = "ADMINISTRADOR"

class EstadoProducto(str, enum.Enum):
    PENDING = "PENDING"      # Estado inicial obligatorio por AC-07
    ACTIVO = "ACTIVO"        # Visible en catálogo
    VENDIDO = "VENDIDO"      # Marcado como vendido por el dueño
    RECHAZADO = "RECHAZADO"  # Moderado por el administrador


# ==========================================
# MODELO DE USUARIO
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    fotografia_url = Column(Text, nullable=True)
    rol = Column(Enum(RolUsuario, name="rol_usuario"), nullable=False, default=RolUsuario.COMPRADOR_VENDEDOR, index=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con sus productos publicados (AC-09)
    productos = relationship("Producto", back_populates="usuario", cascade="all, delete-orphan")


# ==========================================
# MODELO DE PRODUCTO
# ==========================================
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False) # AC-09
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False, index=True) # AC-05
    nombre = Column(String(150), nullable=False) # AC-02
    descripcion = Column(Text, nullable=False) # AC-03
    precio = Column(Numeric(10, 2), nullable=False) # AC-04
    stock = Column(Integer, nullable=False, default=1)
    estado = Column(String(20), nullable=False, default=EstadoProducto.PENDING, index=True) # AC-07
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="productos")
    imagenes = relationship("ImagenProducto", back_populates="producto", cascade="all, delete-orphan")
    categoria = relationship("Categoria", back_populates="productos")


# ==========================================
# MODELO DE IMÁGENES DE PRODUCTO
# ==========================================
class ImagenProducto(Base):
    __tablename__ = "imagenes_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    url_imagen = Column(Text, nullable=False) # AC-06
    es_principal = Column(Boolean, nullable=False, default=False)

    producto = relationship("Producto", back_populates="imagenes")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    productos = relationship("Producto", back_populates="categoria")