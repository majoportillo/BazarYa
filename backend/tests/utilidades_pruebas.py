# Configuracion comun para las pruebas que llaman a la API.
#
# Las pruebas usan una base de datos SQLite temporal para no tocar la base
# de datos de PostgreSQL que usamos para desarrollar. Cada vez que se corren
# las pruebas la base se crea desde cero.

import os
import tempfile
import uuid
from decimal import Decimal

RUTA_BD = os.path.join(tempfile.gettempdir(), "bazarya_pruebas.db")
URL_BD = "sqlite:///" + RUTA_BD.replace("\\", "/")

# se tiene que poner antes de importar la app para que no se conecte a PostgreSQL
os.environ["DATABASE_URL"] = URL_BD

if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

from sqlalchemy import create_engine
from fastapi.testclient import TestClient

from app import database

# si app.database ya se habia importado antes (por otra prueba) se cambia el engine
database.engine = create_engine(URL_BD, connect_args={"check_same_thread": False})
database.SessionLocal.configure(bind=database.engine)

from app.main import app
from app import models
from app.routers import auth

database.Base.metadata.create_all(bind=database.engine)

client = TestClient(app)


def ruta_existe(metodo, ruta):
    # revisa en el swagger si el endpoint existe
    rutas = app.openapi()["paths"]
    return ruta in rutas and metodo.lower() in rutas[ruta]


def texto_unico():
    return uuid.uuid4().hex[:8]


def crear_usuario(rol="COMPRADOR_VENDEDOR", password="Segura123", **cambios):
    datos = {
        "nombre_completo": "Usuario Prueba",
        "email": "usuario" + texto_unico() + "@correo.com",
        "password_hash": auth.hash_password(password),
        "telefono": "55551234",
        "rol": rol,
    }
    datos.update(cambios)
    db = database.SessionLocal()
    usuario = models.Usuario(**datos)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    db.expunge(usuario)
    db.close()
    return usuario


def crear_categoria(activo=True):
    db = database.SessionLocal()
    categoria = models.Categoria(nombre="Categoria " + texto_unico(), activo=activo)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    db.expunge(categoria)
    db.close()
    return categoria


def crear_producto(usuario, categoria, estado="ACTIVO", nombre=None, descripcion=None):
    # crea el producto directo en la base para poder ponerle cualquier estado
    db = database.SessionLocal()
    producto = models.Producto(
        usuario_id=usuario.id,
        categoria_id=categoria.id,
        nombre=nombre or "Producto " + texto_unico(),
        descripcion=descripcion or "Descripcion del producto de prueba",
        precio=Decimal("100.00"),
        stock=1,
        estado=estado,
    )
    db.add(producto)
    db.flush()
    db.add(models.ImagenProducto(producto_id=producto.id, url_imagen="https://img.com/1.jpg", es_principal=True))
    db.commit()
    db.refresh(producto)
    db.expunge(producto)
    db.close()
    return producto


def buscar_producto(producto_id):
    db = database.SessionLocal()
    producto = db.get(models.Producto, producto_id)
    db.close()
    return producto


def entrar_como(usuario):
    # simula que el usuario inicio sesion, sin depender de como se maneje el token
    from app.routers import productos
    if hasattr(auth, "get_current_user"):
        app.dependency_overrides[auth.get_current_user] = lambda: usuario
    if hasattr(productos, "get_current_user_id"):
        app.dependency_overrides[productos.get_current_user_id] = lambda: usuario.id


def cerrar_sesion():
    app.dependency_overrides.clear()
