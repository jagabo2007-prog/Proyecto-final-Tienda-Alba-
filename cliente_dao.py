from data.database_manager import DatabaseManager
from domain.cliente import Cliente


class ClienteDAO:
    def __init__(self, ruta_bd: str) -> None:
        self._ruta = ruta_bd

    def crear(self, cliente: Cliente) -> int:
        with DatabaseManager(self._ruta) as db:
            cur = db.ejecutar(
                "INSERT INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)",
                (cliente.nombre, cliente.telefono, cliente.direccion))
            return cur.lastrowid

    def listar(self, texto: str = "") -> list[Cliente]:
        with DatabaseManager(self._ruta) as db:
            filas = db.consultar(
                "SELECT id, nombre, telefono, direccion FROM clientes "
                "WHERE nombre LIKE ? ORDER BY nombre", (f"%{texto}%",))
        return [Cliente.desde_tupla(f) for f in filas]

    def obtener(self, id_cliente: int) -> Cliente | None:
        with DatabaseManager(self._ruta) as db:
            fila = db.consultar_uno(
                "SELECT id, nombre, telefono, direccion FROM clientes WHERE id = ?",
                (id_cliente,))
        return Cliente.desde_tupla(fila) if fila else None

    def actualizar(self, cliente: Cliente) -> None:
        with DatabaseManager(self._ruta) as db:
            db.ejecutar(
                "UPDATE clientes SET nombre = ?, telefono = ?, direccion = ? WHERE id = ?",
                (cliente.nombre, cliente.telefono, cliente.direccion, cliente.id))

    def eliminar(self, id_cliente: int) -> None:
        with DatabaseManager(self._ruta) as db:
            db.ejecutar("DELETE FROM clientes WHERE id = ?", (id_cliente,))
