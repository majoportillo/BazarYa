from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import get_db
from ..models import Usuario, RolUsuario
from ..schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin

# 1. Definir el Router primero
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# 2. Configurar la herramienta de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# ==========================================
# DEPENDENCIA: OBTENER USUARIO ACTUAL (Para productos y otros módulos)
# ==========================================
def get_current_user(email: str = Header(None), db: Session = Depends(get_db)) -> Usuario:
    """
    Identifica al usuario actual mediante el correo enviado por Header (o puedes ajustarlo a tu JWT).
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró credencial de autenticación (Header 'email' requerido para pruebas)."
        )

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado."
        )
    return usuario


# ==========================================
# DEPENDENCIA DE AUTORIZACIÓN PARA ADMINS (BYA-97)
# ==========================================
def get_current_admin_user(
        usuario_actual: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verifica que el usuario autenticado tenga el rol ADMINISTRADOR.
    """
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren privilegios de Administrador."
        )
    return usuario_actual


# 3. Endpoint de Registro
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    password_encriptada = hash_password(usuario_data.password)

    nuevo_usuario = Usuario(
        nombre_completo=usuario_data.nombre_completo,
        email=usuario_data.email,
        password_hash=password_encriptada,
        telefono=usuario_data.telefono,
        fotografia_url=usuario_data.fotografia_url
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


# 4. Endpoint de Login
@router.post("/login", status_code=status.HTTP_200_OK)
def login_usuario(credentials: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas: El correo no está registrado."
        )

    if not pwd_context.verify(credentials.password[:72], usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas: Contraseña inválida."
        )

    return {
        "mensaje": "Inicio de sesión exitoso",
        "token_tipo": "bearer",
        "usuario": {
            "id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }