
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario, RolUsuario
from ..schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Autenticación"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def crear_token(usuario: Usuario) -> str:
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Falta JWT_SECRET en backend/.env"
        )

    payload = {
        "sub": str(usuario.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o vencido",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Falta JWT_SECRET en backend/.env"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        usuario_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise error

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None or not usuario.activo:
        raise error

    return usuario


def get_current_admin_user(
    usuario_actual: Usuario = Depends(get_current_user)
) -> Usuario:
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    return usuario_actual


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def registrar_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    existente = db.query(Usuario).filter(
        Usuario.email == usuario_data.email
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = Usuario(
        nombre_completo=usuario_data.nombre_completo,
        email=usuario_data.email,
        password_hash=hash_password(usuario_data.password),
        telefono=usuario_data.telefono,
        fotografia_url=usuario_data.fotografia_url
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.post("/login")
def login_usuario(
    credentials: UsuarioLogin,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.email == credentials.email
    ).first()

    if not usuario or not pwd_context.verify(
        credentials.password[:72],
        usuario.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="Cuenta desactivada"
        )

    token = crear_token(usuario)

    return {
        "mensaje": "Inicio de sesión exitoso",
        "access_token": token,
        "token": token,
        "token_tipo": "bearer",
        "usuario": {
            "id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "email": usuario.email,
            "rol": usuario.rol.value
        }
    }
