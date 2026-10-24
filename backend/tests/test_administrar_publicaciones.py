# Pruebas para la administracion de publicaciones del vendedor
# Tarea: BYA-83 (historia BYA-76 - Administracion de publicacion)
#
# Criterios de aceptacion de BYA-76:
#   AC-01 el usuario puede consultar sus propias publicaciones
#   AC-02 puede editar una publicacion propia
#   AC-03 no puede editar publicaciones de otro usuario
#   AC-04 puede eliminar una publicacion propia
#   AC-05 puede marcar una publicacion como vendida
#   AC-06 una publicacion vendida no aparece como disponible
#   AC-07 el usuario no puede modificar el estado de aprobacion administrativa
#
# Los endpoints son de BYA-77, BYA-78, BYA-79 y BYA-80. Si todavia no estan
# en develop las pruebas se saltan.

import unittest

RUTA_MIS_PUBLICACIONES = "/api/productos/mis-publicaciones"
RUTA_PRODUCTO = "/api/productos/{producto_id}"
RUTA_VENDER = "/api/productos/{producto_id}/vender"
RUTA_CATALOGO = "/api/productos/catalogo"

try:
    import utilidades_pruebas as util
    error_api = None
except Exception as e:
    error_api = e


class PruebaAdministrarBase(unittest.TestCase):
    metodo = None
    ruta = None

    def setUp(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        if not util.ruta_existe(self.metodo, self.ruta):
            self.skipTest("No existe el endpoint " + self.metodo.upper() + " " + self.ruta)
        self.client = util.client
        self.categoria = util.crear_categoria()
        self.vendedor = util.crear_usuario(nombre_completo="Vendedor")
        self.otro = util.crear_usuario(nombre_completo="Otro usuario")
        self.producto = util.crear_producto(self.vendedor, self.categoria, estado="ACTIVO")
        util.entrar_como(self.vendedor)

    def tearDown(self):
        util.cerrar_sesion()

    def url(self, ruta, producto_id=None):
        return ruta.format(producto_id=producto_id or self.producto.id)


class TestMisPublicaciones(PruebaAdministrarBase):
    metodo = "get"
    ruta = RUTA_MIS_PUBLICACIONES

    # AC-01
    def test_ac01_ve_solo_sus_publicaciones(self):
        pendiente = util.crear_producto(self.vendedor, self.categoria, estado="PENDING")
        ajeno = util.crear_producto(self.otro, self.categoria, estado="ACTIVO")
        resp = self.client.get(RUTA_MIS_PUBLICACIONES)
        self.assertEqual(resp.status_code, 200, resp.text)
        ids = [p["id"] for p in resp.json()]
        self.assertIn(self.producto.id, ids)
        self.assertIn(pendiente.id, ids)
        self.assertNotIn(ajeno.id, ids)

    def test_ac01_usuario_sin_publicaciones(self):
        util.entrar_como(util.crear_usuario())
        resp = self.client.get(RUTA_MIS_PUBLICACIONES)
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json(), [])

    def test_ac01_sin_sesion(self):
        util.cerrar_sesion()
        resp = self.client.get(RUTA_MIS_PUBLICACIONES)
        self.assertIn(resp.status_code, [401, 403], resp.text)


class TestEditarPublicacion(PruebaAdministrarBase):
    metodo = "put"
    ruta = RUTA_PRODUCTO

    # AC-02
    def test_ac02_edita_publicacion_propia(self):
        resp = self.client.put(self.url(RUTA_PRODUCTO), json={"nombre": "Nombre editado", "precio": "80.50"})
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["nombre"], "Nombre editado")
        self.assertEqual(float(resp.json()["precio"]), 80.50)

    def test_ac02_edicion_con_datos_invalidos(self):
        for datos in [{"precio": "-5"}, {"nombre": "   "}, {"descripcion": "corta"}]:
            resp = self.client.put(self.url(RUTA_PRODUCTO), json=datos)
            self.assertEqual(resp.status_code, 422, "acepto datos invalidos: " + str(datos))

    def test_ac02_publicacion_que_no_existe(self):
        resp = self.client.put(self.url(RUTA_PRODUCTO, 999999), json={"nombre": "Nombre editado"})
        self.assertEqual(resp.status_code, 404, resp.text)

    # AC-03
    def test_ac03_no_edita_publicacion_ajena(self):
        util.entrar_como(self.otro)
        resp = self.client.put(self.url(RUTA_PRODUCTO), json={"nombre": "Intento de cambio"})
        self.assertEqual(resp.status_code, 403, resp.text)
        self.assertNotEqual(util.buscar_producto(self.producto.id).nombre, "Intento de cambio")

    def test_ac03_sin_sesion_no_edita(self):
        util.cerrar_sesion()
        resp = self.client.put(self.url(RUTA_PRODUCTO), json={"nombre": "Intento de cambio"})
        self.assertIn(resp.status_code, [401, 403], resp.text)

    # AC-07
    def test_ac07_no_cambia_estado_de_aprobacion(self):
        pendiente = util.crear_producto(self.vendedor, self.categoria, estado="PENDING")
        resp = self.client.put(self.url(RUTA_PRODUCTO, pendiente.id),
                               json={"estado": "ACTIVO", "nombre": "Ya aprobado"})
        self.assertIn(resp.status_code, [200, 422], resp.text)
        self.assertEqual(util.buscar_producto(pendiente.id).estado, "PENDING")


class TestEliminarPublicacion(PruebaAdministrarBase):
    metodo = "delete"
    ruta = RUTA_PRODUCTO

    # AC-04
    def test_ac04_elimina_publicacion_propia(self):
        resp = self.client.delete(self.url(RUTA_PRODUCTO))
        self.assertIn(resp.status_code, [200, 204], resp.text)
        self.assertIsNone(util.buscar_producto(self.producto.id))

    def test_ac04_eliminar_publicacion_que_no_existe(self):
        resp = self.client.delete(self.url(RUTA_PRODUCTO, 999999))
        self.assertEqual(resp.status_code, 404, resp.text)

    # AC-03
    def test_ac03_no_elimina_publicacion_ajena(self):
        util.entrar_como(self.otro)
        resp = self.client.delete(self.url(RUTA_PRODUCTO))
        self.assertEqual(resp.status_code, 403, resp.text)
        self.assertIsNotNone(util.buscar_producto(self.producto.id))


class TestMarcarVendido(PruebaAdministrarBase):
    metodo = "patch"
    ruta = RUTA_VENDER

    # AC-05
    def test_ac05_marca_como_vendida(self):
        resp = self.client.patch(self.url(RUTA_VENDER))
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["estado"], "VENDIDO")

    def test_ac05_no_marca_vendida_publicacion_ajena(self):
        util.entrar_como(self.otro)
        resp = self.client.patch(self.url(RUTA_VENDER))
        self.assertEqual(resp.status_code, 403, resp.text)
        self.assertEqual(util.buscar_producto(self.producto.id).estado, "ACTIVO")

    # AC-06
    def test_ac06_vendida_no_aparece_disponible(self):
        self.client.patch(self.url(RUTA_VENDER))
        catalogo = self.client.get(RUTA_CATALOGO, params={"limit": 1000}).json()
        for p in catalogo:
            if p["id"] == self.producto.id:
                self.assertNotEqual(p["estado"], "ACTIVO", "la publicacion vendida sigue como disponible")


if __name__ == "__main__":
    unittest.main()
