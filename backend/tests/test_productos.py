# Pruebas para la creación de publicaciones
# Tarea: Integración del módulo Crear Publicación (BazarYa)
# Criterios de Aceptación:
#   AC-02: Nombre requerido y limpio (min 3)
#   AC-03: Descripción requerida y limpia (min 10)
#   AC-04: Precio estrictamente mayor a 0 (Decimal)
#   AC-05: Validación de categoría existente y activa
#   AC-06: Mínimo 1 imagen y máximo 5; sanitización Base64
#   AC-07: Estado inicial obligatorio en PENDING
#   AC-10: Sanitización de textos contra XSS

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


if __name__ == "__main__":
    unittest.main()