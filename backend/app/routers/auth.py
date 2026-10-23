from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioCreate, UsuarioResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext


router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Herramienta para encriptar contraseñas de forma segura
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Validar si el correo ya existe en la base de datos (Cumple AC-02 y AC-05)
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    # 2. Encriptar la contraseña (Nunca se guarda en texto plano)
    # Trunca la contraseña a los primeros 72 bytes por seguridad de bcrypt:
    password_encriptada = pwd_context.hash(usuario_data.password[:72])

    # 3. Crear la instancia del modelo Usuario con los datos limpios
    nuevo_usuario = Usuario(
        nombre_completo=usuario_data.nombre_completo,
        email=usuario_data.email,
        password_hash=password_encriptada,
        telefono=usuario_data.telefono,
        fotografia_url=usuario_data.fotografia_url
    )

    # 4. Guardar en la base de datos de PostgreSQL
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # 5. Devolver la respuesta usando el esquema (automáticamente oculta el password_hash)
    return nuevo_usuario

# ==========================================
# DEPENDENCIA DE AUTORIZACIÓN PARA ADMINS (BYA-97: AC-01, AC-08, AC-09)
# ==========================================
def get_current_admin_user(
    usuario_actual: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    AC-01, AC-08, AC-09: Verifica que el usuario autenticado tenga el rol ADMINISTRADOR.
    Si un usuario normal intenta acceder, bloquea con HTTP 403 Forbidden.
    """
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren privilegios de Administrador."
        )
    return usuario_actual