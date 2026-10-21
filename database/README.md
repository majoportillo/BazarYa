## Creación local de una instancia de base de datos

Para la creación del contenedor de base de datos para realizar sus pruebas locales, deben utilizar
ya sea docker o podman según sus sistema operativo, utilizando la herrameinta compose
según su herramienta.

El archivo **bazarya-cp.yml** contiene la configuración necesaria.

### Ejecucución desde una terminal/Powershell

Antes de proceder con la creación de un contenedor de base de datos, debemos colocar el archivo compose **bazarya-cp.yml**
en un directorio local destinado para su configuración.
Agregar un archivo local .env que se utilizarán para configurar dos variables necesarias para su ambiente, estas variables
son necesarias para compartri de una forma más segura las credenciales de una base de datos.

El contenido debe ser el siguiente:
USER_DB=miuser
PASSWORD_DB=mipass

Este archivo debe estar en el mismo directorio que el archivo compose, y ustedes definiran el valor de cada variable.

si ya poseen la herramienta instalada de docker compose en su sistema operativo ejecutar el siguiente comando.

Para que la información sea persistente en el mismo directorio donde se guarde el archivo compose,
crear un directorio llamado  data, el cual será importado como volumen dentro del compose y se usará para guardar
la inforamción generado por la base de datos, esto permitirá que aunque el contenedor sea eliminado por mantenimiento
la información no se pierda.

```bash
    docker compose -f bazarya-cp.yml up -d
```
Si se necesita eliminar el contenedor se debe usar el comando anterior pero con la opcició down

```bash
    docker compose -f bazarya-cp.yml down -v
```
La opción -v de este comando solo es para que sea detallado de lo que está haciendo, es opcional

## Inicialización de la base de datos
 Por buena práctica para la creación de los scripts DDL deben ser manualmente y no dejar que se ejecuten de forma automática
 esto para evitar que cuando ya se tenga información creada esta se pierra volviendo a crearse los archivos o que fallen 
 por que algo ya existe.