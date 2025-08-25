
-- Tabla de categorías (primero debe existir para la FK)
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla de productos (con categoría)
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    imagen VARCHAR(255),
    categoria_id INT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Tabla de pedidos
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_pedido VARCHAR(20) UNIQUE NOT NULL,
    cliente_nombre VARCHAR(100) NOT NULL,
    cliente_email VARCHAR(100) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de detalles del pedido
CREATE TABLE detalle_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Insertar categorías básicas
INSERT INTO categorias (nombre) VALUES
('Abarrotes'),
('Lácteos'),
('Bebidas'),
('Limpieza'),
('Cuidado Personal');

-- Insertar productos con categorías
INSERT INTO productos (nombre, precio, stock, imagen, categoria_id) VALUES
('Arroz 1kg', 2.50, 100, 'arroz.jpg', 1),
('Leche entera 1L', 1.20, 50, 'leche.jpg', 2),
('Refresco cola 2L', 2.10, 80, 'refresco.jpg', 3),
('Detergente 500ml', 3.75, 60, 'detergente.jpg', 4),
('Jabón de baño', 0.80, 200, 'jabon.jpg', 5),
('Aceite vegetal 1L', 3.00, 40, 'aceite.jpg', 1),
('Yogur natural', 1.50, 70, 'yogur.jpg', 2),
('Agua mineral 600ml', 0.75, 120, 'agua.jpg', 3),
('Cloro 1L', 1.50, 55, 'cloro.jpg', 4),
('Crema dental', 2.30, 90, 'crema_dental.jpg', 5);