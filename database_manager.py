import sqlite3
from typing import Any, Optional

RUTA_BD = "tienda.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    telefono  TEXT NOT NULL,
    direccion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS productos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio    REAL NOT NULL CHECK (precio >= 0),
    stock     INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS ventas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    fecha      TEXT NOT NULL,
    total      REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS detalle_venta (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id        INTEGER NOT NULL,
    producto_id     INTEGER NOT NULL,
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario REAL NOT NULL,
    FOREIGN KEY (venta_id)    REFERENCES ventas(id)    ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
);
"""


class DatabaseManager:
    def __init__(self, ruta: str = RUTA_BD) -> None:
        self._ruta = ruta
        self._conexion: Optional[sqlite3.Connection] = None

    def __enter__(self) -> "DatabaseManager":
        self._conexion = sqlite3.connect(self._ruta)
        self._conexion.execute("PRAGMA foreign_keys = ON;")
        return self

    def __exit__(self, tipo_exc, valor_exc, traza) -> bool:
        if self._conexion is not None:
            if tipo_exc is None:
                self._conexion.commit()
            else:
                self._conexion.rollback()
            self._conexion.close()
            self._conexion = None
        return False

    def ejecutar(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        return self._conexion.execute(sql, parametros)

    def consultar(self, sql: str, parametros: tuple = ()) -> list[tuple[Any, ...]]:
        return self._conexion.execute(sql, parametros).fetchall()

    def consultar_uno(self, sql: str, parametros: tuple = ()) -> Optional[tuple]:
        return self._conexion.execute(sql, parametros).fetchone()


def inicializar_bd(ruta: str = RUTA_BD) -> None:
    with DatabaseManager(ruta) as db:
        db._conexion.executescript(ESQUEMA)
