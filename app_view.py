import flet as ft
from data.cliente_dao import ClienteDAO
from data.producto_repository import ProductoRepository
from data.venta_repository import VentaRepository
from ui.components.clientes_view import ClientesView
from ui.components.productos_view import ProductosView
from ui.components.ventas_view import VentasView


class AppView:
    def __init__(self, page: ft.Page, ruta_bd: str) -> None:
        self._page = page
        cliente_dao = ClienteDAO(ruta_bd)
        producto_repo = ProductoRepository(ruta_bd)
        venta_repo = VentaRepository(ruta_bd)
        self._vistas = [
            ClientesView(page, cliente_dao),
            ProductosView(page, producto_repo),
            VentasView(page, cliente_dao, producto_repo, venta_repo),
        ]
        self._contenedor = ft.Container(content=self._vistas[0], expand=True, padding=16)
        self._botones = [
            ft.Button("Clientes", icon=ft.Icons.PEOPLE, on_click=lambda e: self._ir(0)),
            ft.Button("Productos", icon=ft.Icons.INVENTORY_2, on_click=lambda e: self._ir(1)),
            ft.Button("Ventas", icon=ft.Icons.POINT_OF_SALE, on_click=lambda e: self._ir(2)),
        ]

    def construir(self) -> None:
        self._page.title = "Tienda Alba - Sistema de Gestión"
        self._page.window.width, self._page.window.height = 1000, 720
        self._page.add(
            ft.Row([ft.Text("🛒 Tienda Alba", size=24, weight=ft.FontWeight.BOLD),
                    *self._botones], wrap=True),
            ft.Divider(),
            self._contenedor)

    def _ir(self, indice: int) -> None:
        vista = self._vistas[indice]
        vista.refrescar(actualizar=False)
        self._contenedor.content = vista
        self._page.update()
