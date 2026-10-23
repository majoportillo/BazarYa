from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas import ProductoCreate, ProductoResponse, CategoriaResponse
from app import crud

router = APIRouter(
    prefix="/api/productos",
    tags=["Productos / Publicaciones"]
)

# Dependencia simulada para obtener el ID del usuario autenticado (AC-01)
def get_current_user_id() -> UUID:
    # TODO: Conectar con el JWT/Sesión del módulo de autenticación
    # Devuelve un UUID de prueba registrado previamente
    return UUID("123e4567-e89b-12d3-a456-426614174000")


# ---------------------------------------------------------
# ENDPOINT: Listar Categorías (Para llenar dropdowns en frontend)
# ---------------------------------------------------------
@router.get("/categorias", response_model=List[CategoriaResponse], status_code=status.HTTP_200_OK)
def obtener_categorias(db: Session = Depends(get_db)):
    """Devuelve las categorías disponibles para asociar al crear un producto (AC-05)."""
    return crud.get_categorias(db)


# ---------------------------------------------------------
# ENDPOINT: Crear Publicación (AC-01 al AC-07, AC-09 al AC-11)
# ---------------------------------------------------------
@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_nueva_publicacion(
    producto_in: ProductoCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = Depends(get_current_user_id)  # AC-01: Usuario autenticado
):
    """
    Crea una nueva publicación en el sistema.
    - Se valida que la categoría exista (AC-05).
    - Asigna estado PENDING por defecto (AC-07).
    - Asocia la publicación al usuario creador (AC-09).
    """
    # Validar que la categoría exista
    categoria = crud.get_categoria_by_id(db, producto_in.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría con ID {producto_in.categoria_id} no existe o no está activa."
        )

    # Crear la publicación usando el CRUD
    producto_creado = crud.crear_publicacion(db, producto_in, usuario_id)
    return producto_creado


# ---------------------------------------------------------
# ENDPOINT: Catálogo Público (AC-08)
# ---------------------------------------------------------
@router.get("/catalogo", response_model=List[ProductoResponse], status_code=status.HTTP_200_OK)
def listar_catalogo_publico(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Muestra solo los productos listos para venta.
    AC-08: Excluye automáticamente publicaciones en estado PENDING.
    """
    return crud.get_productos_publicos(db, skip=skip, limit=limit)