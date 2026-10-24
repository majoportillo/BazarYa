from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioResponse, UsuarioUpdate, UsuarioPublicResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Perfiles de Usuario"])


# NOTA: Para pruebas rápidas en Swagger sin complicarnos con tokens aún,
# usaremos el correo por query param o header, o puedes adaptarlo a tu token actual.

@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil_privado(current_user: Usuario = Depends(get_current_user)):
    """
    AC-01: El usuario autenticado puede consultar su información privada.
    Exige un Token JWT válido en los Headers para autorizar la petición.
    """
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def actualizar_perfil_privado(email: str, datos_actualizacion: UsuarioUpdate, db: Session = Depends(get_db)):
    """
    AC-02: El usuario puede actualizar información permitida de su perfil.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar solo los campos enviados
    datos_dict = datos_actualizacion.dict(exclude_unset=True)
    for key, value in datos_dict.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/{usuario_id}/publico", response_model=UsuarioPublicResponse)
def obtener_perfil_publico(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    AC-03 al AC-06: Un visitante o comprador puede consultar el perfil público
    de un vendedor sin exponer información privada (correo, teléfono).
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Perfil público no encontrado o inactivo")

    return usuario