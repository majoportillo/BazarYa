-- Tabla: categorias
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE productos 
    ADD CONSTRAINT fk_productos_categoria 
    FOREIGN KEY (categoria_id) 
    REFERENCES categorias(id) 
    ON DELETE RESTRICT;

-- Insertar categorías iniciales para prueba/catalogo inicial
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónica', 'Dispositivos electrónicos, celulares, computadoras y accesorios'),
('Ropa y Moda', 'Prendas de vestir, calzado y accesorios'),
('Hogar y Muebles', 'Artículos para el hogar, decoración y muebles'),
('Juguetes y Hobbies', 'Juegos, coleccionables y artículos de entretenimiento')
ON CONFLICT (nombre) DO NOTHING;