# Pruebas para la busqueda y navegacion de publicaciones
# Tarea: BYA-91 (historia BYA-84 - Busqueda y navegacion entre publicaciones)
#
# Criterios de aceptacion de BYA-84:
#   AC-01 el usuario puede consultar publicaciones aprobadas
#   AC-02 las publicaciones PENDING no aparecen
#   AC-03 las publicaciones REJECTED no aparecen
#   AC-04 las publicaciones SOLD se muestran como no disponibles
#   AC-05 puede buscar por palabra clave
#   AC-06 puede filtrar por categoria
#   AC-07 puede abrir el detalle de una publicacion
#   AC-08 el listado muestra informacion basica del articulo
#
# En el codigo los estados se llaman ACTIVO (aprobado), RECHAZADO y VENDIDO.
# Los endpoints son de BYA-85 y BYA-86. Si todavia no estan en develop las
# pruebas se saltan.

import unittest

RUTA_BUSCAR = "/api/productos/buscar"
RUTA_DETALLE = "/api/productos/{producto_id}"
RUTA_POR_CATEGORIA = "/api/productos/categoria/{categoria_id}"

try:
    import utilidades_pruebas as util
    error_api = None
except Exception as e:
    error_api = e


class PruebaBusquedaBase(unittest.TestCase):
    metodo = "get"
    ruta = RUTA_BUSCAR

    def setUp(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        if not util.ruta_existe(self.metodo, self.ruta):
            self.skipTest("No existe el endpoint " + self.ruta)
        self.client = util.client
        util.cerrar_sesion()  # la busqueda es publica
        self.vendedor = util.crear_usuario()
        self.categoria = util.crear_categoria()
        # palabra unica para que no salgan productos de otras pruebas
        self.palabra = "lampara" + util.texto_unico()
        self.activo = self.crear("ACTIVO")
        self.pendiente = self.crear("PENDING")
        self.rechazado = self.crear("RECHAZADO")
        self.vendido = self.crear("VENDIDO")

    def crear(self, estado, categoria=None):
        return util.crear_producto(self.vendedor, categoria or self.categoria, estado=estado,
                                   nombre="Lampara de mesa " + self.palabra)

    def buscar(self, **params):
        resp = self.client.get(RUTA_BUSCAR, params=params)
        self.assertEqual(resp.status_code, 200, resp.text)
        return resp.json()

    def ids(self, lista):
        return [p["id"] for p in lista]


class TestBuscarPublicaciones(PruebaBusquedaBase):

    # AC-01
    def test_ac01_muestra_aprobadas(self):
        self.assertIn(self.activo.id, self.ids(self.buscar(q=self.palabra)))

    # AC-02
    def test_ac02_no_muestra_pending(self):
        self.assertNotIn(self.pendiente.id, self.ids(self.buscar(q=self.palabra)))

    # AC-03
    def test_ac03_no_muestra_rechazadas(self):
        self.assertNotIn(self.rechazado.id, self.ids(self.buscar(q=self.palabra)))

    # AC-04
    def test_ac04_vendidas_salen_como_no_disponibles(self):
        resultado = self.buscar(q=self.palabra)
        vendidos = [p for p in resultado if p["id"] == self.vendido.id]
        self.assertEqual(len(vendidos), 1, "la publicacion vendida no aparece")
        self.assertEqual(vendidos[0]["estado"], "VENDIDO")

    # AC-05
    def test_ac05_busca_por_palabra_sin_importar_mayusculas(self):
        self.assertIn(self.activo.id, self.ids(self.buscar(q=self.palabra.upper())))

    def test_ac05_busca_en_la_descripcion(self):
        palabra = "vintage" + util.texto_unico()
        producto = util.crear_producto(self.vendedor, self.categoria, estado="ACTIVO",
                                       descripcion="Radio antigua estilo " + palabra)
        self.assertIn(producto.id, self.ids(self.buscar(q=palabra)))

    def test_ac05_palabra_sin_resultados(self):
        self.assertEqual(self.buscar(q="noexiste" + util.texto_unico()), [])

    # AC-06
    def test_ac06_filtra_por_categoria(self):
        otra_categoria = util.crear_categoria()
        de_otra = self.crear("ACTIVO", categoria=otra_categoria)
        resultado = self.ids(self.buscar(q=self.palabra, categoria_id=self.categoria.id))
        self.assertIn(self.activo.id, resultado)
        self.assertNotIn(de_otra.id, resultado)

    # AC-08
    def test_ac08_muestra_informacion_basica(self):
        resultado = [p for p in self.buscar(q=self.palabra) if p["id"] == self.activo.id][0]
        for campo in ["nombre", "precio", "estado", "imagenes", "categoria"]:
            self.assertIn(campo, resultado)
        self.assertTrue(len(resultado["imagenes"]) > 0)


class TestPublicacionesPorCategoria(PruebaBusquedaBase):
    ruta = RUTA_POR_CATEGORIA

    # AC-06
    def test_ac06_lista_por_categoria(self):
        resp = self.client.get(RUTA_POR_CATEGORIA.format(categoria_id=self.categoria.id))
        self.assertEqual(resp.status_code, 200, resp.text)
        resultado = self.ids(resp.json())
        self.assertIn(self.activo.id, resultado)
        self.assertIn(self.vendido.id, resultado)
        self.assertNotIn(self.pendiente.id, resultado)
        self.assertNotIn(self.rechazado.id, resultado)

    def test_ac06_categoria_que_no_existe(self):
        resp = self.client.get(RUTA_POR_CATEGORIA.format(categoria_id=999999))
        self.assertEqual(resp.status_code, 404, resp.text)


class TestDetallePublicacion(PruebaBusquedaBase):
    ruta = RUTA_DETALLE

    # AC-07
    def test_ac07_abre_detalle(self):
        resp = self.client.get(RUTA_DETALLE.format(producto_id=self.activo.id))
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["id"], self.activo.id)
        self.assertIn("descripcion", resp.json())

    def test_ac07_detalle_de_vendida(self):
        resp = self.client.get(RUTA_DETALLE.format(producto_id=self.vendido.id))
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["estado"], "VENDIDO")

    # AC-02 y AC-03
    def test_ac02_ac03_detalle_de_pending_o_rechazada_no_se_ve(self):
        for producto in [self.pendiente, self.rechazado]:
            resp = self.client.get(RUTA_DETALLE.format(producto_id=producto.id))
            self.assertEqual(resp.status_code, 404, "se pudo ver el detalle de un producto " + producto.estado)


if __name__ == "__main__":
    unittest.main()
