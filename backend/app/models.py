import enum
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RolUsuario(str, enum.Enum):
    COMPRADOR_VENDEDOR = "COMPRADOR_VENDEDOR"
    ADMINISTRADOR = "ADMINISTRADOR"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    fotografia_url = Column(String(255), nullable=True)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.COMPRADOR_VENDEDOR, index=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())