# Pruebas para la creación de publicaciones y administracion de publicaciones
import unittest
from decimal import Decimal

try:
    from pydantic import ValidationError
    from app.schemas import ProductoCreate, ImagenProductoCreate
    error_schemas = None
except Exception as e:
    error_schemas = e


def datos_producto_validos(**cambios):
    datos = {
        "nombre": "Cámara Fotográfica Vintage",
        "descripcion": "Cámara fotográfica analógica en excelente estado de conservación.",
        "precio": Decimal("150.00"),
        "stock": 2,
        "categoria_id": 1,
        "imagenes": [
            {
                "url_imagen": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
                "es_principal": True
            }
        ]
    }
    datos.update(cambios)
    return datos


class TestEsquemaProducto(unittest.TestCase):

    def setUp(self):
        if error_schemas:
            self.fail("No se pudieron importar los schemas de Producto: " + repr(error_schemas))
    # BYA-76: AC-01 - Consultar publicaciones propias
    def test_ac01_consultar_mis_publicaciones_vacio(self):
        # Verifica que la función del CRUD filtre correctamente por el ID del usuario
        usuario_id_dummy = uuid.uuid4()
        productos = obtener_productos_por_usuario(db=self.db, usuario_id=usuario_id_dummy)
        self.assertEqual(len(productos), 0)
    # AC-02 y AC-10: Saneamiento XSS y validación de espacios
    def test_ac02_ac10_sanitizacion_xss_y_espacios(self):
        datos = datos_producto_validos(
            nombre="  <script>alert('xss')</script> Laptop  ",
            descripcion="  <g>Descripción detallada del producto</g>  "
        )
        producto = ProductoCreate(**datos)
        # Verifica que se eliminaron espacios y se escaparon los tags HTML
        self.assertNotIn("<script>", producto.nombre)
        self.assertIn("&lt;script&gt;", producto.nombre)
        self.assertEqual(producto.nombre.startswith(" "), False)

    # BYA-76: AC-02 / AC-03 - Edición de Publicaciones
    def test_ac02_ac03_edicion_publicacion_propiedad(self):
        # 1. Simular esquema de actualización válido
        update_data = {
            "nombre": "Laptop Gamer Usada Editada",
            "precio": Decimal("750.00")
        }
        esquema_update = ProductoUpdate(**update_data)
        self.assertEqual(esquema_update.nombre, "Laptop Gamer Usada Editada")
        self.assertEqual(esquema_update.precio, Decimal("750.00"))

    def test_ac03_edicion_usuario_no_propietario_error(self):
        # Verifica la regla de autorización a nivel de servicio CRUD
        usuario_dueno = uuid.uuid4()
        usuario_intruso = uuid.uuid4()
        
        # Inserción dummy de producto en sesión de prueba
        producto = Producto(
            usuario_id=usuario_dueno,
            categoria_id=1,
            nombre="Producto Original",
            descripcion="Descripción del producto original",
            precio=100.00,
            stock=1,
            estado=EstadoProducto.PENDING
        )
        self.db.add(producto)
        self.db.commit()

        # Intentar editar con usuario distinto genera un error 403 HTTP
        update_schema = ProductoUpdate(nombre="Hackeo de Nombre")
        with self.assertRaises(HTTPException) as context:
            actualizar_publicacion(
                db=self.db,
                producto_id=producto.id,
                producto_update=update_schema,
                usuario_id=usuario_intruso
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
    
    # BYA-76: AC-04 / AC-03 - Eliminación de Publicación
    def test_ac04_eliminar_publicacion_propia_exito(self):
        usuario_id = uuid.uuid4()
        
        # Crear publicación de prueba
        producto = Producto(
            usuario_id=usuario_id,
            categoria_id=1,
            nombre="Producto a Eliminar",
            descripcion="Descripción de prueba para eliminación",
            precio=50.00,
            stock=1,
            estado=EstadoProducto.PENDING
        )
        self.db.add(producto)
        self.db.commit()

        # Ejecutar eliminación
        resultado = eliminar_publicacion(
            db=self.db,
            producto_id=producto.id,
            usuario_id=usuario_id
        )
        self.assertTrue(resultado)

        # Verificar que ya no existe en la base de datos
        prod_borrado = get_producto_by_id(self.db, producto.id)
        self.assertIsNone(prod_borrado)

    def test_ac03_eliminar_publicacion_ajena_error(self):
        usuario_dueno = uuid.uuid4()
        usuario_intruso = uuid.uuid4()

        producto = Producto(
            usuario_id=usuario_dueno,
            categoria_id=1,
            nombre="Producto Protegido",
            descripcion="Descripción de prueba de autorización",
            precio=150.00,
            stock=1,
            estado=EstadoProducto.PENDING
        )
        self.db.add(producto)
        self.db.commit()

        # Intentar eliminar con un usuario diferente debe lanzar 403
        with self.assertRaises(HTTPException) as context:
            eliminar_publicacion(
                db=self.db,
                producto_id=producto.id,
                usuario_id=usuario_intruso
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)

    # AC-04: Validación de Precio
    def test_ac04_precio_invalido(self):
        for precio_invalido in [0, -10.50, -1]:
            with self.assertRaises(ValidationError, msg=f"Aceptó precio inválido: {precio_invalido}"):
                ProductoCreate(**datos_producto_validos(precio=precio_invalido))

    # AC-06: Asignación automática de imagen principal si ninguna viene marcada
    def test_ac06_imagen_principal_automatica(self):
        datos = datos_producto_validos(imagenes=[
            {"url_imagen": "https://imagen.com/1.jpg", "es_principal": False}
        ])
        producto = ProductoCreate(**datos)
        self.assertTrue(producto.imagenes[0].es_principal)

    # AC-06: Error si más de una imagen es marcada como principal
    def test_ac06_multiple_imagen_principal_error(self):
        datos = datos_producto_validos(imagenes=[
            {"url_imagen": "https://imagen.com/1.jpg", "es_principal": True},
            {"url_imagen": "https://imagen.com/2.jpg", "es_principal": True}
        ])
        with self.assertRaises(ValidationError):
            ProductoCreate(**datos)

    # AC-06: Validar formato Base64 malformado
    def test_ac06_base64_invalido(self):
        datos = datos_producto_validos(imagenes=[
            {"url_imagen": "data:image/png;base64,FORMATO_CORRUPTO_O_INVALIDO_$$$", "es_principal": True}
        ])
        with self.assertRaises(ValidationError):
            ProductoCreate(**datos)
    # BYA-76: AC-05 / AC-06 - Marcar como Vendido y Exclusión del Catálogo
    def test_ac05_ac06_marcar_como_vendido_exito(self):
        usuario_id = uuid.uuid4()
        
        # Crear publicación activa de prueba
        producto = Producto(
            usuario_id=usuario_id,
            categoria_id=1,
            nombre="Bicicleta de Montaña",
            descripcion="Bicicleta en buen estado",
            precio=200.00,
            stock=1,
            estado=EstadoProducto.ACTIVO
        )
        self.db.add(producto)
        self.db.commit()

        # Cambiar estado a VENDIDO
        prod_actualizado = marcar_producto_como_vendido(
            db=self.db,
            producto_id=producto.id,
            usuario_id=usuario_id
        )
        
        # Verificación AC-05: El estado cambia a VENDIDO
        self.assertEqual(prod_actualizado.estado, EstadoProducto.VENDIDO)

        # Verificación AC-06: No debe figurar dentro de las publicaciones del catálogo público activo
        catalogo = get_productos_publicos(self.db)
        ids_en_catalogo = [p.id for p in catalogo]
        self.assertNotIn(producto.id, ids_en_catalogo)

    def test_ac05_marcar_como_vendido_usuario_ajeno_error(self):
        usuario_dueno = uuid.uuid4()
        usuario_intruso = uuid.uuid4()

        producto = Producto(
            usuario_id=usuario_dueno,
            categoria_id=1,
            nombre="Celular Usado",
            descripcion="Smartphone en buen estado",
            precio=120.00,
            stock=1,
            estado=EstadoProducto.ACTIVO
        )
        self.db.add(producto)
        self.db.commit()

        # Un usuario no propietario debe recibir un error 403 HTTP
        with self.assertRaises(HTTPException) as context:
            marcar_producto_como_vendido(
                db=self.db,
                producto_id=producto.id,
                usuario_id=usuario_intruso
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
    
    # BYA-84: Pruebas de Búsqueda y Navegación
    def test_bya84_busqueda_excluye_pending_y_rechazado(self):
        usuario_id = uuid.uuid4()
        
        # Crear productos en diferentes estados
        p_activo = Producto(usuario_id=usuario_id, categoria_id=1, nombre="Silla de Oficina", descripcion="Silla ergonómica", precio=80.00, stock=1, estado=EstadoProducto.ACTIVO)
        p_pending = Producto(usuario_id=usuario_id, categoria_id=1, nombre="Mesa de Centro", descripcion="Mesa de madera", precio=50.00, stock=1, estado=EstadoProducto.PENDING)
        p_rechazado = Producto(usuario_id=usuario_id, categoria_id=1, nombre="Sillón Antiguo", descripcion="Sillón usado", precio=40.00, stock=1, estado=EstadoProducto.RECHAZADO)
        p_vendido = Producto(usuario_id=usuario_id, categoria_id=1, nombre="Silla Gamer", descripcion="Silla de carreras", precio=120.00, stock=1, estado=EstadoProducto.VENDIDO)

        self.db.add_all([p_activo, p_pending, p_rechazado, p_vendido])
        self.db.commit()

        # Búsqueda general
        resultados = buscar_publicaciones(db=self.db, q="Silla")
        ids_resultados = [p.id for p in resultados]

        # AC-01 & AC-04: ACTIVO y VENDIDO sí aparecen
        self.assertIn(p_activo.id, ids_resultados)
        self.assertIn(p_vendido.id, ids_resultados)

        # AC-02 & AC-03: PENDING y RECHAZADO NUNCA aparecen
        self.assertNotIn(p_pending.id, ids_resultados)
        self.assertNotIn(p_rechazado.id, ids_resultados)

    def test_bya84_filtro_por_categoria_y_palabra_clave(self):
        usuario_id = uuid.uuid4()
        
        p1 = Producto(usuario_id=usuario_id, categoria_id=1, nombre="Laptop Asus", descripcion="Laptop Gamer I7", precio=900.00, stock=1, estado=EstadoProducto.ACTIVO)
        p2 = Producto(usuario_id=usuario_id, categoria_id=2, nombre="Camisa Azul", descripcion="Camisa de vestir", precio=25.00, stock=1, estado=EstadoProducto.ACTIVO)

        self.db.add_all([p1, p2])
        self.db.commit()

        # Filtrar por palabra clave "Asus" (AC-05)
        res_palabra = buscar_publicaciones(db=self.db, q="Asus")
        self.assertEqual(len(res_palabra), 1)
        self.assertEqual(res_palabra[0].id, p1.id)

        # Filtrar por Categoría 2 (AC-06)
        res_cat = buscar_publicaciones(db=self.db, categoria_id=2)
        self.assertEqual(len(res_cat), 1)
        self.assertEqual(res_cat[0].id, p2.id)

if __name__ == "__main__":
    unittest.main()