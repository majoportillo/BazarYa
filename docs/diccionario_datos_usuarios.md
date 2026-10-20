# Diccionario de Datos - Tabla de Usuarios

| Campo | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, Default UUID | Identificador único del usuario[cite: 1]. |
| `nombre_completo` | `VARCHAR(100)` | NOT NULL | Nombre y apellido del usuario[cite: 1]. |
| `email` | `VARCHAR(150)` | NOT NULL, UNIQUE, Index | Correo electrónico para inicio de sesión[cite: 1]. |
| `password_hash` | `VARCHAR(255)` | NOT NULL | Contraseña encriptada. |
| `telefono` | `VARCHAR(20)` | NOT NULL | Teléfono para contacto directo con el vendedor[cite: 1]. |
| `fotografia_url` | `VARCHAR(255)` | NULLABLE | URL de la imagen de perfil guardada en Cloudinary. |
| `rol` | `ENUM` | NOT NULL, Default 'COMPRADOR_VENDEDOR' | Rol en el sistema (`COMPRADOR_VENDEDOR` o `ADMINISTRADOR`). |
| `activo` | `BOOLEAN` | NOT NULL, Default `TRUE` | Estado de la cuenta para moderación. |
| `fecha_creacion` | `TIMESTAMP` | Default `NOW()` | Auditoría de fecha de registro. |