from data.database_manager import DatabaseManager


def cargar_datos_demo(ruta: str) -> None:
    with DatabaseManager(ruta) as db:
        if db.consultar_uno("SELECT COUNT(*) FROM clientes")[0] > 0:
            return
        clientes = [("Doña Marta Ruiz", "3001234567", "Calle 10 #5-20"),
                    ("Carlos Pérez", "3109876543", "Carrera 7 #12-30"),
                    ("Lucía Gómez", "3205558888", "Barrio El Prado")]
        productos = [("Arroz 1kg", "Granos", 4200, 50),
                     ("Leche 1L", "Lácteos", 3800, 30),
                     ("Huevos x30", "Lácteos", 16500, 20),
                     ("Gaseosa 1.5L", "Bebidas", 5500, 40),
                     ("Pan tajado", "Panadería", 6200, 15)]
        for c in clientes:
            db.ejecutar("INSERT INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)", c)
        for p in productos:
            db.ejecutar("INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)", p)
