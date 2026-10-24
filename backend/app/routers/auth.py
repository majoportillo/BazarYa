from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin

# 1. Definir el Router primero
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# 2. Configurar la herramienta de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# 3. Endpoint de Registro
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    # Validar si el correo ya existe en la base de datos
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    # Encriptar contraseña
    password_encriptada = hash_password(usuario_data.password)

    # Crear instancia del modelo
    nuevo_usuario = Usuario(
        nombre_completo=usuario_data.nombre_completo,
        email=usuario_data.email,
        password_hash=password_encriptada,
        telefono=usuario_data.telefono,
        fotografia_url=usuario_data.fotografia_url
    )

    # Guardar en BD
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


# 4. Endpoint de Login
@router.post("/login", status_code=status.HTTP_200_OK)
def login_usuario(credentials: UsuarioLogin, db: Session = Depends(get_db)):
    # Buscar al usuario por correo
    usuario = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas: El correo no está registrado."
        )

    # Verificar la contraseña con el hash guardado
    if not pwd_context.verify(credentials.password[:72], usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas: Contraseña inválida."
        )

    # Retorno exitoso de autenticación y rol (AC-01 a AC-04)
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