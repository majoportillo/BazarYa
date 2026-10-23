from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.models import Producto, ImagenProducto, Categoria, EstadoProducto
from app.schemas import ProductoCreate, CategoriaResponse


# ==========================================
# CRUD DE CATEGORÍAS
# ==========================================

def get_categorias(db: Session) -> List[Categoria]:
    """Obtiene todas las categorías activas para el catálogo (AC-05)."""
    return db.query(Categoria).filter(Categoria.activo == True).all()

def get_categoria_by_id(db: Session, categoria_id: int) -> Optional[Categoria]:
    """Valida la existencia de una categoría."""
    return db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.activo == True).first()


# ==========================================
# CRUD DE PRODUCTOS / PUBLICACIONES
# ==========================================

def crear_publicacion(db: Session, producto_in: ProductoCreate, usuario_id: UUID) -> Producto:
    """
    Crea una publicación asociada al usuario creador (AC-09).
    Nace automáticamente en estado 'PENDING' (AC-07).
    """
    # 1. Crear la instancia de Producto
    nuevo_producto = Producto(
        usuario_id=usuario_id,                  # AC-09
        categoria_id=producto_in.categoria_id,  # AC-05
        nombre=producto_in.nombre,              # AC-02
        descripcion=producto_in.descripcion,    # AC-03
        precio=producto_in.precio,              # AC-04
        stock=1,
        estado=EstadoProducto.PENDING           # AC-07 (Estado inicial obligatorio)
    )
    
    db.add(nuevo_producto)
    db.flush()  # Obtiene el ID del producto recién insertado sin hacer commit definitivo

    # 2. Asociar las imágenes del producto (AC-06)
    for img in producto_in.imagenes:
        nueva_imagen = ImagenProducto(
            producto_id=nuevo_producto.id,
            url_imagen=img.url_imagen,
            es_principal=img.es_principal
        )
        db.add(nueva_imagen)

    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


def get_productos_publicos(db: Session, skip: int = 0, limit: int = 10) -> List[Producto]:
    """
    Obtiene el catálogo público.
    AC-08: Las publicaciones en estado PENDING NO se incluyen en este listado.
    """
    return (
        db.query(Producto)
        .filter(Producto.estado == EstadoProducto.ACTIVO)  # Filtra excluyendo PENDING (AC-08)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_producto_by_id(db: Session, producto_id: int) -> Optional[Producto]:
    """Obtiene el detalle de un producto por su ID."""
    return db.query(Producto).filter(Producto.id == producto_id).first()