from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import get_db
from ..models import Usuario, RolUsuario
from ..schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin

# 1. Definir el Router primero
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# 2. Configuración de seguridad y hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# ==========================================
# DEPENDENCIAS DE AUTENTICACIÓN Y AUTORIZACIÓN
# ==========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario autenticado a partir del token JWT/OAuth2.
    """
    # Si aún no estás validando JWT tokens, buscamos un usuario de prueba o mock:
    # Ajusta esta lógica según cómo estés manejando tus tokens actualizados.
    usuario = db.query(Usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado o token inválido."
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


def get_current_admin_user(
    usuario_actual: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    BYA-97 & BYA-99: Verifica que el usuario autenticado tenga el rol ADMINISTRADOR.
    Si un usuario normal intenta acceder, bloquea con HTTP 403 Forbidden.
    """
    if usuario_actual.rol != RolUsuario.ADMINISTRADOR and usuario_actual.rol != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren privilegios de Administrador."
        )
    return usuario_actual


# ==========================================
# ENDPOINTS DE AUTENTICACIÓN
# ==========================================

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