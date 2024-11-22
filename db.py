import sqlite3

# Conectar a la base de datos (se creará automáticamente si no existe)
conn = sqlite3.connect('soa.db')
cursor = conn.cursor()

# Script para crear las tablas
cursor.executescript("""
-- Tabla Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    idUser INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    tipo TINYINT NOT NULL CHECK(tipo BETWEEN 1 AND 3), -- 1: visitante, 2: operador, 3: administrador
    contraseña TEXT NOT NULL
);

-- Tabla Fondas
CREATE TABLE IF NOT EXISTS Fondas (
    idFonda INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE, -- Nombre único para cada fonda
    descripcion TEXT NOT NULL,
    cantidad_mesas INTEGER NOT NULL
);

-- Tabla OperadoresFonda (nueva)
CREATE TABLE IF NOT EXISTS OperadoresFonda (
    idFonda INTEGER NOT NULL,
    idOperador INTEGER NOT NULL,
    PRIMARY KEY (idFonda, idOperador),
    FOREIGN KEY (idFonda) REFERENCES Fondas(idFonda) ON DELETE CASCADE,
    FOREIGN KEY (idOperador) REFERENCES Usuarios(idUser) ON DELETE CASCADE
);

-- Tabla Productos
CREATE TABLE IF NOT EXISTS Productos (
    idProducto INTEGER PRIMARY KEY AUTOINCREMENT,
    idFonda INTEGER NOT NULL, -- Relación con la fonda
    nombre VARCHAR(100) NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL,
    esPromocion BOOLEAN DEFAULT 0, -- Indica si es una promoción
    FOREIGN KEY (idFonda) REFERENCES Fondas(idFonda) ON DELETE CASCADE
);

-- Tabla Mesas
CREATE TABLE IF NOT EXISTS Mesas (
    idMesa INTEGER PRIMARY KEY AUTOINCREMENT,
    idFonda INTEGER NOT NULL, -- Relación con la fonda
    numero INTEGER NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE, -- Disponibilidad de la mesa
    FOREIGN KEY (idFonda) REFERENCES Fondas(idFonda) ON DELETE CASCADE
);

-- Tabla Reservas
CREATE TABLE IF NOT EXISTS Reservas (
    idReserva INTEGER PRIMARY KEY AUTOINCREMENT,
    idUser INTEGER NOT NULL, -- Usuario que realiza la reserva
    idMesa INTEGER NOT NULL, -- Mesa reservada
    cantidad_personas INTEGER NOT NULL,
    hora_inicio DATETIME NOT NULL,
    hora_termino DATETIME NOT NULL,
    estado TEXT DEFAULT 'Pendiente', -- Estado de la reserva (Pendiente, Cancelada, Finalizada)
    FOREIGN KEY (idUser) REFERENCES Usuarios(idUser) ON DELETE CASCADE,
    FOREIGN KEY (idMesa) REFERENCES Mesas(idMesa) ON DELETE CASCADE
);

-- Tabla Opiniones
CREATE TABLE IF NOT EXISTS Opiniones (
    idOpinion INTEGER PRIMARY KEY AUTOINCREMENT,
    idFonda INTEGER NOT NULL,
    idUser INTEGER NOT NULL,
    calificacion TINYINT NOT NULL CHECK(calificacion BETWEEN 1 AND 5), -- Calificación entre 1 y 5
    opinion TEXT,
    respuesta TEXT, -- Respuesta del operador a la opinión
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idFonda) REFERENCES Fondas(idFonda) ON DELETE CASCADE,
    FOREIGN KEY (idUser) REFERENCES Usuarios(idUser) ON DELETE CASCADE
);

-- Tabla Alertas (antes llamada Alarmas)
CREATE TABLE IF NOT EXISTS Alertas (
    idAlerta INTEGER PRIMARY KEY AUTOINCREMENT,
    idMesa INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente', -- Estado de la alerta (Pendiente, Resuelta)
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idMesa) REFERENCES Mesas(idMesa) ON DELETE CASCADE
);
""")

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos creada exitosamente.")
