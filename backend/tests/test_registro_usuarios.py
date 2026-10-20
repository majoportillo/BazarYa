# Pruebas para el registro de usuarios
# Tarea: BYA-49 (historia BYA-43 - Registro de usuarios)
#
# Las pruebas estan basadas en los criterios de aceptacion de BYA-43:
#   AC-01 nombre, email y password
#   AC-02 email unico
#   AC-03 password no en texto plano
#   AC-04 si los datos son validos se crea el usuario
#   AC-05 email repetido da error
#   AC-06 validacion de campos obligatorios
#   AC-07 endpoint documentado en OpenAPI
#
# Las pruebas del endpoint se saltan mientras no exista app.main (BYA-45).
#
# Para correrlas desde la carpeta backend:
#   python -m unittest discover -s tests -v

import unittest
import uuid

# ruta que asumimos para el registro, cambiar si el endpoint queda con otra
RUTA_REGISTRO = "/api/usuarios/registro"

# tamaños segun la tabla usuarios
MAX_NOMBRE = 100
MAX_TELEFONO = 20


def datos_usuario(**cambios):
    # email random para que no choque entre pruebas
    datos = {
        "nombre_completo": "Ana Lopez",
        "email": "ana" + uuid.uuid4().hex[:6] + "@correo.com",
        "password": "Segura123",
        "telefono": "55551234",
    }
    datos.update(cambios)
    return datos


# si falla el import lo guardamos para mostrarlo en las pruebas
try:
    from pydantic import ValidationError
    from app.schemas import UsuarioCreate
    error_schemas = None
except Exception as e:
    error_schemas = e

try:
    from fastapi.testclient import TestClient
    from app.main import app
    error_api = None
except Exception as e:
    error_api = e


class TestEsquemaRegistro(unittest.TestCase):

    def setUp(self):
        if error_schemas:
            self.fail("No se pudo importar UsuarioCreate: " + repr(error_schemas))

    # AC-01
    def test_ac01_datos_validos(self):
        usuario = UsuarioCreate(**datos_usuario())
        self.assertEqual(usuario.nombre_completo, "Ana Lopez")
        self.assertEqual(usuario.password, "Segura123")

    # AC-02
    def test_ac02_email_en_minusculas(self):
        usuario = UsuarioCreate(**datos_usuario(email="Ana.Lopez@Correo.com"))
        self.assertEqual(usuario.email, "ana.lopez@correo.com")

    # AC-06
    def test_ac06_falta_campo_obligatorio(self):
        for campo in ["nombre_completo", "email", "password", "telefono"]:
            datos = datos_usuario()
            del datos[campo]
            with self.assertRaises(ValidationError, msg="no valido que falte " + campo):
                UsuarioCreate(**datos)

    def test_ac06_campos_vacios(self):
        for campo in ["nombre_completo", "password", "telefono"]:
            with self.assertRaises(ValidationError, msg="acepto " + campo + " vacio"):
                UsuarioCreate(**datos_usuario(**{campo: ""}))

    def test_ac06_campos_solo_espacios(self):
        for campo in ["nombre_completo", "telefono"]:
            with self.assertRaises(ValidationError, msg="acepto " + campo + " con espacios"):
                UsuarioCreate(**datos_usuario(**{campo: "   "}))

    def test_ac06_email_invalido(self):
        for email in ["ana", "ana@", "@correo.com", "ana correo.com"]:
            with self.assertRaises(ValidationError, msg="acepto el email " + email):
                UsuarioCreate(**datos_usuario(email=email))

    def test_ac06_textos_muy_largos(self):
        with self.assertRaises(ValidationError):
            UsuarioCreate(**datos_usuario(nombre_completo="a" * (MAX_NOMBRE + 1)))
        with self.assertRaises(ValidationError):
            UsuarioCreate(**datos_usuario(telefono="9" * (MAX_TELEFONO + 1)))

    def test_ac06_password_corta(self):
        with self.assertRaises(ValidationError):
            UsuarioCreate(**datos_usuario(password="abc12"))

    def test_ac06_valores_en_el_limite(self):
        usuario = UsuarioCreate(**datos_usuario(
            nombre_completo="a" * MAX_NOMBRE,
            telefono="9" * MAX_TELEFONO,
            password="12345678",
        ))
        self.assertEqual(len(usuario.nombre_completo), MAX_NOMBRE)


@unittest.skipIf(error_api is not None, "Todavia no existe el endpoint de registro (BYA-45)")
class TestEndpointRegistro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def registrar(self, **cambios):
        datos = datos_usuario(**cambios)
        respuesta = self.client.post(RUTA_REGISTRO, json=datos)
        return datos, respuesta

    # AC-04
    def test_ac04_crea_usuario(self):
        datos, resp = self.registrar()
        self.assertEqual(resp.status_code, 201, resp.text)
        body = resp.json()
        self.assertIn("id", body)
        self.assertEqual(body["email"], datos["email"])
        self.assertEqual(body["rol"], "COMPRADOR_VENDEDOR")

    # AC-03
    def test_ac03_no_devuelve_password(self):
        datos, resp = self.registrar()
        self.assertEqual(resp.status_code, 201, resp.text)
        self.assertNotIn("password", resp.json())
        self.assertNotIn("password_hash", resp.json())
        self.assertNotIn(datos["password"], resp.text)

    # AC-05
    def test_ac05_email_repetido(self):
        datos, resp = self.registrar()
        self.assertEqual(resp.status_code, 201, resp.text)
        _, resp2 = self.registrar(email=datos["email"])
        self.assertIn(resp2.status_code, [400, 409], resp2.text)

    # AC-02
    def test_ac02_email_repetido_mayusculas(self):
        datos, resp = self.registrar()
        self.assertEqual(resp.status_code, 201, resp.text)
        _, resp2 = self.registrar(email=datos["email"].upper())
        self.assertIn(resp2.status_code, [400, 409], resp2.text)

    # AC-06
    def test_ac06_datos_invalidos_422(self):
        _, resp = self.registrar(nombre_completo="")
        self.assertEqual(resp.status_code, 422, resp.text)

    # AC-07
    def test_ac07_documentado_openapi(self):
        rutas = self.client.get("/openapi.json").json()["paths"]
        self.assertIn(RUTA_REGISTRO, rutas)
        self.assertIn("post", rutas[RUTA_REGISTRO])


if __name__ == "__main__":
    unittest.main()
