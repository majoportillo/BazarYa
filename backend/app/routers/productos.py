from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas import ProductoCreate, ProductoResponse, CategoriaResponse
from app import crud
from app.models import Usuario
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/productos",
    tags=["Productos / Publicaciones"]
)
@router.get(
    "/mis-publicaciones", 
    response_model=List[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar las publicaciones propias del usuario autenticado (AC-01)"
)

def listar_mis_publicaciones(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user) # Inyección del usuario desde el Token JWT
):
    """
    Permite al vendedor autenticado consultar el listado completo de sus publicaciones.
    Garantiza que solo pueda ver sus propios productos (AC-01, AC-03).
    """
    return crud.obtener_productos_por_usuario(db=db, usuario_id=usuario_actual.id)

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
    usuario_actual: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva publicación en el sistema asociada al usuario autenticado.
    """

    return crud.crear_publicacion(db, producto_in, usuario_actual.id)


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