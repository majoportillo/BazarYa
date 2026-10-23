# Pruebas para el inicio de sesion
# Tarea: BYA-55 (historia BYA-50 - Inicio de sesion de usuarios registrados)
#
# Criterios de aceptacion de BYA-50:
#   AC-01 el usuario se autentica con email y password
#   AC-02 credenciales incorrectas generan error
#   AC-03 una autenticacion valida permite acceder al area privada
#   AC-04 el sistema identifica el rol del usuario
#   AC-05 las funcionalidades privadas requieren autenticacion
#   AC-06 un usuario no autenticado no puede crear publicaciones
#   AC-07 la API esta documentada en Swagger

import unittest

RUTA_LOGIN = "/auth/login"
RUTA_REGISTRO = "/auth/register"
RUTA_PRODUCTOS = "/api/productos"

try:
    import utilidades_pruebas as util
    error_api = None
except Exception as e:
    error_api = e


class TestLogin(unittest.TestCase):

    def setUp(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        if not util.ruta_existe("post", RUTA_LOGIN):
            self.skipTest("No existe el endpoint " + RUTA_LOGIN)
        self.client = util.client
        util.cerrar_sesion()
        # cada prueba registra su propio usuario por la API
        self.email = "login" + util.texto_unico() + "@correo.com"
        self.password = "Segura123"
        resp = self.client.post(RUTA_REGISTRO, json={
            "nombre_completo": "Luis Perez",
            "email": self.email,
            "password": self.password,
            "telefono": "55559876",
        })
        self.assertEqual(resp.status_code, 201, "no se pudo registrar el usuario de prueba: " + resp.text)

    def login(self, email, password):
        return self.client.post(RUTA_LOGIN, json={"email": email, "password": password})

    # AC-01
    def test_ac01_login_correcto(self):
        resp = self.login(self.email, self.password)
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["usuario"]["email"], self.email)

    def test_ac01_login_con_email_en_mayusculas(self):
        resp = self.login(self.email.upper(), self.password)
        self.assertEqual(resp.status_code, 200, resp.text)

    # AC-02
    def test_ac02_password_incorrecta(self):
        resp = self.login(self.email, "OtraClave999")
        self.assertEqual(resp.status_code, 401, resp.text)

    def test_ac02_email_no_registrado(self):
        resp = self.login("noexiste" + util.texto_unico() + "@correo.com", self.password)
        self.assertEqual(resp.status_code, 401, resp.text)

    def test_ac02_campos_vacios(self):
        resp = self.login("", "")
        self.assertEqual(resp.status_code, 422, resp.text)

    def test_ac02_respuesta_no_incluye_password(self):
        resp = self.login(self.email, self.password)
        self.assertNotIn(self.password, resp.text)
        self.assertNotIn("password_hash", resp.text)

    # AC-03
    def test_ac03_login_devuelve_token_para_area_privada(self):
        # para entrar al area privada el frontend necesita algo que mandar en las
        # siguientes peticiones (token o cookie de sesion)
        resp = self.login(self.email, self.password)
        self.assertEqual(resp.status_code, 200, resp.text)
        tiene_token = "access_token" in resp.json() or "set-cookie" in resp.headers
        self.assertTrue(tiene_token, "el login no devuelve token ni cookie: " + resp.text)

    # AC-04
    def test_ac04_identifica_rol_usuario_normal(self):
        resp = self.login(self.email, self.password)
        self.assertEqual(resp.json()["usuario"]["rol"], "COMPRADOR_VENDEDOR")

    def test_ac04_identifica_rol_administrador(self):
        admin = util.crear_usuario(rol="ADMINISTRADOR", password="Admin12345")
        resp = self.login(admin.email, "Admin12345")
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["usuario"]["rol"], "ADMINISTRADOR")

    # AC-05 y AC-06
    def test_ac05_ac06_no_autenticado_no_puede_publicar(self):
        if not util.ruta_existe("post", RUTA_PRODUCTOS):
            self.skipTest("No existe el endpoint " + RUTA_PRODUCTOS)
        categoria = util.crear_categoria()
        resp = self.client.post(RUTA_PRODUCTOS, json={
            "nombre": "Bicicleta usada",
            "descripcion": "Bicicleta en buen estado, poco uso",
            "precio": "500.00",
            "categoria_id": categoria.id,
            "imagenes": [{"url_imagen": "https://img.com/bici.jpg"}],
        })
        self.assertIn(resp.status_code, [401, 403], "se creo la publicacion sin iniciar sesion: " + resp.text)

    # AC-07
    def test_ac07_documentado_openapi(self):
        rutas = self.client.get("/openapi.json").json()["paths"]
        self.assertIn(RUTA_LOGIN, rutas)
        self.assertIn("post", rutas[RUTA_LOGIN])


if __name__ == "__main__":
    unittest.main()
