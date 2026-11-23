# Tienda Alba - Sistema de Gestión (Programación II)

Autor: Jaime Gabriel Rodríguez González

Aplicación de escritorio con **Flet** y **SQLite** para gestionar clientes, productos y ventas de Tienda Alba, una tienda de barrio.

## Ejecutar
```
pip install flet
python main.py
```
La base de datos `tienda.db` se crea sola, con datos de ejemplo.

## Estructura
- `data/` – Persistencia: `DatabaseManager` (with, commit/rollback, `PRAGMA foreign_keys=ON`), `ClienteDAO`, `ProductoRepository`, `VentaRepository`.
- `domain/` – Negocio: `Cliente`, `Producto`, `Venta`, `DetalleVenta` (propiedades validadas, `desde_tupla`, métodos mágicos).
- `ui/` – Interfaz Flet: `app_view.py` y `components/` (vistas de clientes, productos y ventas).

## Base de datos
`clientes` 1:N `ventas` 1:N `detalle_venta` N:1 `productos` (consultas siempre parametrizadas con `?`).
