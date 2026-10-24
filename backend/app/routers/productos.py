from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.schemas import ProductoCreate, ProductoResponse, ProductoUpdate, CategoriaResponse, VendedorContactoResponse
from app import crud
from app.models import Usuario, EstadoProducto
from app.routers.auth import get_current_user, get_current_admin_user

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
    usuario_actual = Depends(get_current_user)
):
    """
    Permite al vendedor autenticado consultar el listado completo de sus publicaciones.
    Garantiza que solo pueda ver sus propios productos (AC-01, AC-03).
    """
    return crud.obtener_productos_por_usuario(db=db, usuario_id=usuario_actual.id)


# ---------------------------------------------------------
# ENDPOINT: Listar Categorías
# ---------------------------------------------------------
@router.get("/categorias", response_model=List[CategoriaResponse], status_code=status.HTTP_200_OK)
def obtener_categorias(db: Session = Depends(get_db)):
    """Devuelve las categorías disponibles para asociar al crear un producto (AC-05)."""
    return crud.get_categorias(db)


# ---------------------------------------------------------
# ENDPOINT: Crear Publicación
# ---------------------------------------------------------
@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_nueva_publicacion(
    producto_in: ProductoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """Crea una nueva publicación en el sistema asociada al usuario autenticado."""
    return crud.crear_publicacion(db, producto_in, usuario_actual.id)


# ---------------------------------------------------------
# ENDPOINT: Catálogo Público
# ---------------------------------------------------------
@router.get("/catalogo", response_model=List[ProductoResponse], status_code=status.HTTP_200_OK)
def listar_catalogo_publico(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Muestra solo los productos listos para venta (Excluye PENDING)."""
    return crud.get_productos_publicos(db, skip=skip, limit=limit)


# ---------------------------------------------------------
# ENDPOINT: Contacto del Vendedor (BYA-93 / AC-01 al AC-05)
# ---------------------------------------------------------
@router.get(
    "/{producto_id}/contacto",
    response_model=VendedorContactoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener información de contacto del vendedor (BYA-93)"
)
def obtener_contacto_vendedor(producto_id: int, db: Session = Depends(get_db)):
    """
    BYA-93: Permite al comprador obtener la información de contacto directa
    del vendedor para una publicación específica (AC-01 a AC-05).
    """
    vendedor, error = crud.get_contacto_vendedor_by_producto_id(db, producto_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    return {
        "vendedor_id": vendedor.id,
        "nombre_completo": vendedor.nombre_completo,
        "email": vendedor.email,
        "telefono": vendedor.telefono,
        "nota": "Contacto directo entre comprador y vendedor (Sin pasarela de pagos ni envíos)."
    }


# ---------------------------------------------------------
# ENDPOINT: Editar / Actualizar Publicación (BYA-76)
# ---------------------------------------------------------
@router.put(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Editar una publicación propia (AC-02, AC-03)"
)
def editar_publicacion(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """Permite al vendedor actualizar la información de su publicación."""
    return crud.actualizar_publicacion(
        db=db,
        producto_id=producto_id,
        producto_update=producto_update,
        usuario_id=usuario_actual.id
    )


# ---------------------------------------------------------
# ENDPOINT: Eliminar Publicación (BYA-76)
# ---------------------------------------------------------
@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una publicación propia (AC-04)"
)
def eliminar_publicacion(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """Permite al vendedor eliminar permanentemente una de sus publicaciones."""
    crud.eliminar_publicacion(db=db, producto_id=producto_id, usuario_id=usuario_actual.id)
    return None


# ---------------------------------------------------------
# ENDPOINT: Marcar Publicación como Vendida (BYA-76)
# ---------------------------------------------------------
@router.patch(
    "/{producto_id}/vender",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Marcar una publicación como vendida (AC-05, AC-06)"
)
def cambiar_estado_vendido(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    """Permite al vendedor cambiar el estado de su publicación a VENDIDO."""
    return crud.marcar_producto_como_vendido(db=db, producto_id=producto_id, usuario_id=usuario_actual.id)



# ---------------------------------------------------------
# ENDPOINT: Búsqueda y Filtrado de Publicaciones (BYA-84)
# ---------------------------------------------------------
@router.get(
    "/buscar",
    response_model=List[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar publicaciones por palabra clave y/o categoría (BYA-84)"
)
def buscar_productos(
    q: Optional[str] = Query(None, description="Palabra clave"),
    categoria_id: Optional[int] = Query(None, gt=0, description="ID de categoría"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Permite a compradores explorar productos por término y categoría."""
    return crud.buscar_publicaciones(db=db, q=q, categoria_id=categoria_id, skip=skip, limit=limit)



# ---------------------------------------------------------
# ENDPOINT: Obtener Detalle de una Publicación
# ---------------------------------------------------------
@router.get(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de una publicación (AC-07)"
)
def obtener_detalle_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Permite abrir y visualizar la información completa de un artículo publicado."""
    producto = crud.obtener_detalle_publicacion(db=db, producto_id=producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La publicación con ID {producto_id} no existe o no está disponible."
        )
    return producto


# ---------------------------------------------------------
# ENDPOINT: Obtener Publicaciones por Categoría
# ---------------------------------------------------------
@router.get(
    "/categoria/{categoria_id}",
    response_model=List[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener publicaciones pertenecientes a una categoría específica (AC-06)"
)
def listar_publicaciones_por_categoria(
    categoria_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Devuelve el listado de publicaciones asociadas a una categoría determinada."""
    return crud.obtener_publicaciones_por_categoria(db=db, categoria_id=categoria_id, skip=skip, limit=limit)


# =========================================================
# MÓDULO DE ADMINISTRACIÓN / MODERACIÓN (BYA-40 / BYA-97 / BYA-99)
# =========================================================

@router.get(
    "/admin/pendientes",
    response_model=List[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar publicaciones pendientes de moderación (Solo ADMIN)"
)
def listar_publicaciones_pendientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_actual: Usuario = Depends(get_current_admin_user)
):
    """Permite únicamente al Administrador revisar la cola de publicaciones en estado PENDING (AC-01, AC-02, AC-08, AC-09)."""
    return crud.obtener_publicaciones_pendientes(db=db, skip=skip, limit=limit)


class ModeracionDecision(BaseModel):
    estado: EstadoProducto  # ACTIVO (Aprobado) o RECHAZADO
    motivo_rechazo: Optional[str] = None


@router.patch(
    "/admin/{producto_id}/moderar",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Aprobar o rechazar una publicación pendiente (Solo ADMIN)"
)
def moderar_publicacion_admin(
    producto_id: int,
    decision: ModeracionDecision,
    db: Session = Depends(get_db),
    admin_actual: Usuario = Depends(get_current_admin_user)
):
    """Permite al Administrador aprobar (ACTIVO) o rechazar una publicación pendiente (BYA-99)."""
    return crud.moderar_publicacion(
        db=db,
        producto_id=producto_id,
        nuevo_estado=decision.estado,
        motivo_rechazo=decision.motivo_rechazo
    )
