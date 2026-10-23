from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
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
    Aplica validación de categoría previa e inserta en estado 'PENDING' (AC-07).
    """
    # 1. Validación previa: Verificar existencia y estado de la categoría en BD
    categoria = get_categoria_by_id(db, producto_in.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría con ID {producto_in.categoria_id} no existe o se encuentra inactiva."
        )

    # 1. Crear la instancia de Producto
    nuevo_producto = Producto(
        usuario_id=usuario_id,                  # AC-09
        categoria_id=producto_in.categoria_id,  # AC-05
        nombre=producto_in.nombre,              # AC-02
        descripcion=producto_in.descripcion,    # AC-03
        precio=producto_in.precio,              # AC-04
        stock=producto_in.stock,
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

def obtener_productos_por_usuario(db: Session, usuario_id: UUID) -> List[Producto]:
    """
    AC-01: Obtiene todas las publicaciones pertenecientes a un usuario específico.
    """
    return (
        db.query(Producto)
        .filter(Producto.usuario_id == usuario_id)
        .order_by(Producto.fecha_creacion.desc())
        .all()
    )

# ==========================================
# ACTUALIZACIÓN / EDICIÓN DE PUBLICACIÓN (BYA-76)
# ==========================================

def actualizar_publicacion(
    db: Session, 
    producto_id: int, 
    producto_update: ProductoUpdate, 
    usuario_id: UUID
) -> Producto:
    """
    AC-02: Permite editar una publicación existente.
    AC-03: Verifica que la publicación pertenezca al usuario solicitante.
    AC-07: Bloquea cualquier modificación directa al estado administrativo.
    """
    # 1. Obtener el producto de la base de datos
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La publicación con ID {producto_id} no fue encontrada."
        )

    # 2. Validación estricta de propiedad (AC-03)
    if producto.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar una publicación que no te pertenece."
        )

    # 3. Extraer únicamente los campos enviados para actualización parcial
    datos_actualizacion = producto_update.model_dump(exclude_unset=True)

    # 4. Validar cambio de categoría si se incluyó en el request
    if "categoria_id" in datos_actualizacion:
        categoria = get_categoria_by_id(db, datos_actualizacion["categoria_id"])
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La categoría con ID {datos_actualizacion['categoria_id']} no existe o se encuentra inactiva."
            )

    # 5. Manejo de actualización de imágenes si fueron provistas
    nuevas_imagenes = datos_actualizacion.pop("imagenes", None)
    if nuevas_imagenes is not None:
        # Reemplazar imágenes anteriores asociadas al producto
        db.query(ImagenProducto).filter(ImagenProducto.producto_id == producto.id).delete()
        for img_data in nuevas_imagenes:
            nueva_img = ImagenProducto(
                producto_id=producto.id,
                url_imagen=img_data["url_imagen"],
                es_principal=img_data.get("es_principal", False)
            )
            db.add(nueva_img)

    # 6. Actualizar campos escalares permitidos (excluyendo el estado por AC-07)
    for campo, valor in datos_actualizacion.items():
        if campo != "estado": # AC-07
            setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto

# ==========================================
# ELIMINACIÓN DE PUBLICACIÓN (BYA-76: AC-04)
# ==========================================

def eliminar_publicacion(db: Session, producto_id: int, usuario_id: UUID) -> bool:
    """
    AC-04: Elimina una publicación de la base de datos.
    AC-03: Verifica estrictamente que la publicación pertenezca al usuario solicitante.
    """
    # 1. Buscar la publicación en la BD
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La publicación con ID {producto_id} no fue encontrada."
        )

    # 2. Validación estricta de propiedad (AC-03)
    if producto.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar una publicación que no te pertenece."
        )

    # 3. Eliminar de la base de datos (las imágenes asociadas se borran en cascada)
    db.delete(producto)
    db.commit()
    return True