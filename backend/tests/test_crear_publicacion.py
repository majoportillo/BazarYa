# Pruebas para crear una publicacion
# Tarea: BYA-75 (historia BYA-65 - Crear publicacion)
#
# Criterios de aceptacion de BYA-65:
#   AC-01 solo usuarios autenticados pueden crear publicaciones
#   AC-02 debe tener titulo
#   AC-03 debe tener descripcion
#   AC-04 debe tener precio
#   AC-05 debe pertenecer a una categoria
#   AC-06 debe permitir asociar una imagen
#   AC-07 una nueva publicacion queda en estado PENDING
#   AC-08 una publicacion PENDING no aparece en el catalogo publico
#   AC-09 la publicacion queda asociada al usuario creador
#   AC-10 los datos invalidos son rechazados
#   AC-11 el endpoint esta documentado en Swagger
#
# Las validaciones del esquema ProductoCreate ya estan en test_productos.py,
# aqui se prueba el endpoint completo.

import unittest

RUTA_CREAR = "/api/productos"
RUTA_CATALOGO = "/api/productos/catalogo"

IMAGEN_BASE64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

try:
    import utilidades_pruebas as util
    error_api = None
except Exception as e:
    error_api = e


class TestCrearPublicacion(unittest.TestCase):

    def setUp(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        if not util.ruta_existe("post", RUTA_CREAR):
            self.skipTest("El endpoint " + RUTA_CREAR + " no esta registrado en la API")
        self.client = util.client
        self.vendedor = util.crear_usuario()
        self.categoria = util.crear_categoria()
        util.entrar_como(self.vendedor)

    def tearDown(self):
        util.cerrar_sesion()

    def datos_producto(self, **cambios):
        datos = {
            "nombre": "Guitarra acustica " + util.texto_unico(),
            "descripcion": "Guitarra acustica con funda, casi nueva",
            "precio": "750.00",
            "stock": 1,
            "categoria_id": self.categoria.id,
            "imagenes": [{"url_imagen": IMAGEN_BASE64, "es_principal": True}],
        }
        datos.update(cambios)
        return datos

    def crear(self, **cambios):
        return self.client.post(RUTA_CREAR, json=self.datos_producto(**cambios))

    # AC-01
    def test_ac01_sin_sesion_no_puede_publicar(self):
        util.cerrar_sesion()
        resp = self.crear()
        self.assertIn(resp.status_code, [401, 403], "se creo la publicacion sin iniciar sesion: " + resp.text)

    def test_ac01_con_sesion_si_puede_publicar(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)

    # AC-02, AC-03, AC-04, AC-05
    def test_ac02_a_ac05_campos_obligatorios(self):
        for campo in ["nombre", "descripcion", "precio", "categoria_id"]:
            datos = self.datos_producto()
            del datos[campo]
            resp = self.client.post(RUTA_CREAR, json=datos)
            self.assertEqual(resp.status_code, 422, "acepto la publicacion sin " + campo)

    def test_ac02_titulo_vacio(self):
        resp = self.crear(nombre="   ")
        self.assertEqual(resp.status_code, 422, resp.text)

    def test_ac04_precio_cero_o_negativo(self):
        for precio in ["0", "-50"]:
            resp = self.crear(precio=precio)
            self.assertEqual(resp.status_code, 422, "acepto el precio " + precio)

    # AC-05
    def test_ac05_categoria_que_no_existe(self):
        resp = self.crear(categoria_id=999999)
        self.assertIn(resp.status_code, [400, 404, 422], resp.text)

    def test_ac05_categoria_inactiva(self):
        inactiva = util.crear_categoria(activo=False)
        resp = self.crear(categoria_id=inactiva.id)
        self.assertIn(resp.status_code, [400, 404, 422], resp.text)

    def test_ac05_respuesta_incluye_categoria(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)
        self.assertEqual(resp.json()["categoria"]["id"], self.categoria.id)

    # AC-06
    def test_ac06_guarda_la_imagen(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)
        imagenes = resp.json()["imagenes"]
        self.assertEqual(len(imagenes), 1)
        self.assertEqual(imagenes[0]["url_imagen"], IMAGEN_BASE64)

    def test_ac06_sin_imagen(self):
        resp = self.crear(imagenes=[])
        self.assertEqual(resp.status_code, 422, resp.text)

    # AC-07
    def test_ac07_queda_en_pending(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)
        self.assertEqual(resp.json()["estado"], "PENDING")

    # AC-08
    def test_ac08_pending_no_sale_en_catalogo(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)
        nuevo_id = resp.json()["id"]
        catalogo = self.client.get(RUTA_CATALOGO, params={"limit": 1000})
        self.assertEqual(catalogo.status_code, 200, catalogo.text)
        ids = [p["id"] for p in catalogo.json()]
        self.assertNotIn(nuevo_id, ids)

    # AC-09
    def test_ac09_queda_asociada_al_creador(self):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201, resp.text)
        self.assertEqual(resp.json()["usuario_id"], str(self.vendedor.id))

    # AC-10
    def test_ac10_datos_invalidos(self):
        casos = [
            {"precio": "mucho"},
            {"categoria_id": "abc"},
            {"imagenes": [{"url_imagen": "data:image/png;base64,$$$"}]},
            {"nombre": "ab"},
        ]
        for caso in casos:
            resp = self.crear(**caso)
            self.assertEqual(resp.status_code, 422, "acepto datos invalidos: " + str(caso))

    def test_ac10_texto_con_html_se_limpia(self):
        resp = self.crear(nombre="<script>alert(1)</script> Mesa")
        self.assertEqual(resp.status_code, 201, resp.text)
        self.assertNotIn("<script>", resp.json()["nombre"])


class TestDocumentacionPublicacion(unittest.TestCase):

    # AC-11 (esta prueba no se salta, si el endpoint no esta en la API tiene que fallar)
    def test_ac11_documentado_en_swagger(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        rutas = util.client.get("/openapi.json").json()["paths"]
        self.assertTrue(RUTA_CREAR in rutas, "POST /api/productos no aparece en Swagger")
        self.assertIn("post", rutas[RUTA_CREAR])


if __name__ == "__main__":
    unittest.main()
