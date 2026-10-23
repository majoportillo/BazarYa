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

# ==========================================
# MARCAR COMO VENDIDO (BYA-76: AC-05, AC-06)
# ==========================================

def marcar_producto_como_vendido(db: Session, producto_id: int, usuario_id: UUID) -> Producto:
    """
    AC-05: Transiciona el estado de la publicación a VENDIDO.
    AC-06: Al no estar en estado ACTIVO, se excluye automáticamente del catálogo público.
    AC-03: Garantiza que solo el propietario del producto realice el cambio.
    """
    # 1. Buscar la publicación en la base de datos
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
            detail="No tienes permisos para modificar el estado de una publicación que no te pertenece."
        )

    # 3. Cambiar el estado a VENDIDO
    producto.estado = EstadoProducto.VENDIDO
    
    db.commit()
    db.refresh(producto)
    return producto

# ==========================================
# BÚSQUEDA Y FILTRADO DE PUBLICACIONES (BYA-84)
# ==========================================

def buscar_publicaciones(
    db: Session,
    q: Optional[str] = None,
    categoria_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Producto]:
    """
    AC-01: Muestra publicaciones aprobadas (ACTIVO) y vendidas (VENDIDO).
    AC-02 & AC-03: Excluye PENDING y RECHAZADO.
    AC-04: Muestra productos VENDIDO (para marcar su indisponibilidad en UI).
    AC-05: Filtra por palabra clave (q) en nombre o descripción (sin distinción de mayúsculas/minúsculas).
    AC-06: Filtra por categoría si se provee.
    """
    # 1. Base query: Incluir solo estados visibles para compradores (ACTIVO y VENDIDO)
    # Excluye explícitamente PENDING (AC-02) y RECHAZADO (AC-03)
    query = db.query(Producto).filter(
        Producto.estado.in_([EstadoProducto.ACTIVO, EstadoProducto.VENDIDO])
    )

    # 2. Filtro por Categoría (AC-06)
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == categoria_id)

    # 3. Filtro por Palabra Clave (AC-05) - Búsqueda en nombre o descripción
    if q and q.strip():
        termino = f"%{q.strip()}%"
        query = query.filter(
            (Producto.nombre.ilike(termino)) | (Producto.descripcion.ilike(termino))
        )

    # 4. Ordenar por fecha de creación descendente y aplicar paginación
    return query.order_by(Producto.fecha_creacion.desc()).offset(skip).limit(limit).all()


def obtener_detalle_publicacion(db: Session, producto_id: int) -> Optional[Producto]:
    """
    AC-07: Consulta el detalle completo de una publicación específica.
    Solo permite ver si el producto está en estado visible (ACTIVO o VENDIDO).
    """
    producto = get_producto_by_id(db, producto_id)
    if not producto or producto.estado not in [EstadoProducto.ACTIVO, EstadoProducto.VENDIDO]:
        return None
    return producto

# ==========================================
# PUBLICACIONES POR CATEGORÍA (BYA-84: AC-06)
# ==========================================

def obtener_publicaciones_por_categoria(
    db: Session, 
    categoria_id: int, 
    skip: int = 0, 
    limit: int = 20
) -> List[Producto]:
    """
    AC-06: Obtiene las publicaciones pertenecientes a una categoría específica.
    AC-01 & AC-04: Muestra publicaciones en estado ACTIVO y VENDIDO (marcado como no disponible).
    AC-02 & AC-03: Excluye explícitamente publicaciones en estado PENDING y RECHAZADO.
    """
    # Validar primero si la categoría existe y está activa
    categoria = get_categoria_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con ID {categoria_id} no fue encontrada o se encuentra inactiva."
        )

    return (
        db.query(Producto)
        .filter(
            Producto.categoria_id == categoria_id,
            Producto.estado.in_([EstadoProducto.ACTIVO, EstadoProducto.VENDIDO]) # AC-01 al AC-04
        )
        .order_by(Producto.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )