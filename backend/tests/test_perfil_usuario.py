# Pruebas para el perfil publico y privado
# Tarea: BYA-62 (historia BYA-56 - Perfil publico y privado)
#
# Criterios de aceptacion de BYA-56:
#   AC-01 el usuario autenticado puede consultar su informacion privada
#   AC-02 el usuario puede actualizar informacion permitida de su perfil
#   AC-03 un visitante puede consultar el perfil publico de un vendedor
#   AC-04 el perfil publico no expone informacion privada
#   AC-05 el perfil publico muestra informacion suficiente para identificar al vendedor
#   AC-06 el perfil publico puede accederse desde una publicacion
#
# Los endpoints son de BYA-57 y BYA-58. Si todavia no estan en develop
# las pruebas se saltan.

import unittest

RUTA_PERFIL_PRIVADO = "/usuarios/me"
RUTA_PERFIL_PUBLICO = "/usuarios/{usuario_id}/publico"
RUTA_CATALOGO = "/api/productos/catalogo"

try:
    import utilidades_pruebas as util
    error_api = None
except Exception as e:
    error_api = e


class PruebaPerfilBase(unittest.TestCase):

    def setUp(self):
        if error_api:
            self.fail("No se pudo cargar la API: " + repr(error_api))
        self.client = util.client
        self.usuario = util.crear_usuario(nombre_completo="Maria Gomez", telefono="44441111")

    def tearDown(self):
        util.cerrar_sesion()

    def perfil_privado(self, usuario):
        # se manda el email porque asi lo pide el endpoint por ahora (BYA-57)
        return self.client.get(RUTA_PERFIL_PRIVADO, params={"email": usuario.email})

    def perfil_publico(self, usuario_id):
        return self.client.get(RUTA_PERFIL_PUBLICO.format(usuario_id=usuario_id))


class TestPerfilPrivado(PruebaPerfilBase):

    def setUp(self):
        super().setUp()
        if not util.ruta_existe("get", RUTA_PERFIL_PRIVADO):
            self.skipTest("No existe el endpoint " + RUTA_PERFIL_PRIVADO + " (BYA-57)")

    # AC-01
    def test_ac01_consulta_su_informacion(self):
        util.entrar_como(self.usuario)
        resp = self.perfil_privado(self.usuario)
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertEqual(body["email"], self.usuario.email)
        self.assertEqual(body["telefono"], "44441111")
        self.assertNotIn("password_hash", body)

    def test_ac01_sin_sesion_no_ve_datos_privados_de_otro(self):
        # un visitante no deberia poder ver el telefono y correo de alguien
        # solo con saber su email
        util.cerrar_sesion()
        resp = self.perfil_privado(self.usuario)
        self.assertIn(resp.status_code, [401, 403], "devolvio datos privados sin sesion: " + resp.text)

    # AC-02
    def test_ac02_actualiza_telefono_y_nombre(self):
        util.entrar_como(self.usuario)
        resp = self.client.put(RUTA_PERFIL_PRIVADO, params={"email": self.usuario.email},
                               json={"telefono": "77778888", "nombre_completo": "Maria G. Lopez"})
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["telefono"], "77778888")
        self.assertEqual(resp.json()["nombre_completo"], "Maria G. Lopez")

    def test_ac02_no_puede_cambiar_rol_ni_email(self):
        util.entrar_como(self.usuario)
        resp = self.client.put(RUTA_PERFIL_PRIVADO, params={"email": self.usuario.email},
                               json={"rol": "ADMINISTRADOR", "email": "otro@correo.com"})
        self.assertIn(resp.status_code, [200, 422], resp.text)
        util.entrar_como(self.usuario)
        body = self.perfil_privado(self.usuario).json()
        self.assertEqual(body["rol"], "COMPRADOR_VENDEDOR")
        self.assertEqual(body["email"], self.usuario.email)

    def test_ac02_datos_invalidos(self):
        util.entrar_como(self.usuario)
        for datos in [{"telefono": "123"}, {"nombre_completo": ""}, {"nombre_completo": "   "}]:
            resp = self.client.put(RUTA_PERFIL_PRIVADO, params={"email": self.usuario.email}, json=datos)
            self.assertEqual(resp.status_code, 422, "acepto datos invalidos: " + str(datos))


class TestPerfilPublico(PruebaPerfilBase):

    def setUp(self):
        super().setUp()
        if not util.ruta_existe("get", RUTA_PERFIL_PUBLICO):
            self.skipTest("No existe el endpoint " + RUTA_PERFIL_PUBLICO + " (BYA-58)")

    # AC-03
    def test_ac03_visitante_ve_perfil_publico(self):
        util.cerrar_sesion()
        resp = self.perfil_publico(self.usuario.id)
        self.assertEqual(resp.status_code, 200, resp.text)

    def test_ac03_usuario_que_no_existe(self):
        resp = self.perfil_publico("00000000-0000-0000-0000-000000000000")
        self.assertEqual(resp.status_code, 404, resp.text)

    def test_ac03_usuario_inactivo_no_se_muestra(self):
        inactivo = util.crear_usuario(activo=False)
        resp = self.perfil_publico(inactivo.id)
        self.assertEqual(resp.status_code, 404, resp.text)

    # AC-04
    def test_ac04_no_expone_informacion_privada(self):
        resp = self.perfil_publico(self.usuario.id)
        body = resp.json()
        for campo in ["email", "telefono", "password", "password_hash"]:
            self.assertNotIn(campo, body, "el perfil publico muestra " + campo)
        self.assertNotIn(self.usuario.email, resp.text)

    # AC-05
    def test_ac05_muestra_datos_para_identificar_vendedor(self):
        body = self.perfil_publico(self.usuario.id).json()
        self.assertEqual(body["nombre_completo"], "Maria Gomez")
        self.assertEqual(body["id"], str(self.usuario.id))

    # AC-06
    def test_ac06_se_llega_desde_una_publicacion(self):
        if not util.ruta_existe("get", RUTA_CATALOGO):
            self.skipTest("No existe el endpoint " + RUTA_CATALOGO)
        categoria = util.crear_categoria()
        producto = util.crear_producto(self.usuario, categoria, estado="ACTIVO")
        catalogo = self.client.get(RUTA_CATALOGO, params={"limit": 1000}).json()
        publicacion = [p for p in catalogo if p["id"] == producto.id][0]
        resp = self.perfil_publico(publicacion["usuario_id"])
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["nombre_completo"], "Maria Gomez")


if __name__ == "__main__":
    unittest.main()
