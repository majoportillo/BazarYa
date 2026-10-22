# Diccionario de Datos - Tabla de Usuarios

| Campo | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, Default UUID | Identificador único del usuario. |
| `nombre_completo` | `VARCHAR(100)` | NOT NULL | Nombre y apellido del usuario. |
| `email` | `VARCHAR(150)` | NOT NULL, UNIQUE, Index | Correo electrónico para inicio de sesión (almacenado siempre en minúsculas). |
| `password_hash` | `VARCHAR(255)` | NOT NULL | Contraseña encriptada. |
| `telefono` | `VARCHAR(20)` | NOT NULL | Teléfono para contacto directo con el vendedor. |
| `fotografia_url` | `TEXT` / `VARCHAR(255)` | NULLABLE | Cadena que contiene la imagen de perfil (soporta formato Base64 según BYA-71 o URL externa). |
| `rol` | `ENUM ('rol_usuario')` | NOT NULL, Default 'COMPRADOR_VENDEDOR' | Rol en el sistema (`COMPRADOR_VENDEDOR` o `ADMINISTRADOR`). |
| `activo` | `BOOLEAN` | NOT NULL, Default `TRUE` | Estado de la cuenta para moderación. |
| `fecha_creacion` | `TIMESTAMP` | Default `NOW()` | Auditoría de fecha de registro. |
| `fecha_actualizacion` | `TIMESTAMP` | Default `NOW()` | Auditoría de fecha de última actualización. |