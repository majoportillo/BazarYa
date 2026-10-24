-- Tabla: productos
CREATE TABLE productos (
    id BIGSERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL, --Relacion con la tabla usuario
    categoria_id INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock INT NOT NULL DEFAULT 1 CHECK (stock >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE
    CONSTRAINT fk_productos_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla: imagenes_producto
CREATE TABLE imagenes_producto (
    id BIGSERIAL PRIMARY KEY,
    producto_id BIGINT NOT NULL,
    url_imagen TEXT NOT NULL,
    es_principal BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_imagenes_producto_producto
        FOREIGN KEY (producto_id) 
        REFERENCES productos(id) 
        ON DELETE CASCADE
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_productos_usuario ON productos(usuario_id);
CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_productos_estado ON productos(estado);