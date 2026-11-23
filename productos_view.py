import sqlite3
import flet as ft
from data.producto_repository import ProductoRepository
from domain.producto import Producto
from ui.components.utils import mostrar_mensaje, confirmar

CATEGORIAS = ["Granos", "Lácteos", "Bebidas", "Panadería", "Aseo", "Otros"]


class ProductosView(ft.Column):
    def __init__(self, page: ft.Page, repo: ProductoRepository) -> None:
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=12)
        self._page, self._repo = page, repo
        self._editando_id: int | None = None

        self.txt_nombre = ft.TextField(label="Nombre", width=240)
        self.dd_categoria = ft.Dropdown(label="Categoría", width=180,
                                        options=[ft.DropdownOption(key=c, text=c) for c in CATEGORIAS])
        self.txt_precio = ft.TextField(label="Precio", width=130, keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_stock = ft.TextField(label="Stock", width=110, keyboard_type=ft.KeyboardType.NUMBER)
        self.txt_buscar = ft.TextField(label="Buscar por nombre", width=220,
                                       prefix_icon=ft.Icons.SEARCH,
                                       on_change=lambda e: self.refrescar())
        self.btn_guardar = ft.Button("Agregar producto", icon=ft.Icons.SAVE, on_click=self._guardar)
        self.btn_cancelar = ft.TextButton("Cancelar edición", visible=False, on_click=self._cancelar)
        self.tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in
                     ("ID", "Nombre", "Categoría", "Precio", "Stock", "Acciones")],
            rows=[], heading_row_color=ft.Colors.BLUE_GREY_50)

        self.controls = [
            ft.Text("Productos", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([self.txt_nombre, self.dd_categoria, self.txt_precio, self.txt_stock], wrap=True),
            ft.Row([self.btn_guardar, self.btn_cancelar]),
            self.txt_buscar,
            ft.Row([self.tabla], scroll=ft.ScrollMode.AUTO),
        ]
        self.refrescar(actualizar=False)

    def refrescar(self, actualizar: bool = True) -> None:
        self.tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p.id))), ft.DataCell(ft.Text(p.nombre)),
                ft.DataCell(ft.Text(p.categoria)), ft.DataCell(ft.Text(f"${p.precio:,.0f}")),
                ft.DataCell(ft.Text(str(p.stock),
                                    color=ft.Colors.RED_600 if p.stock < 5 else None)),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar",
                                  on_click=lambda e, pr=p: self._cargar(pr)),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_600, tooltip="Eliminar",
                                  on_click=lambda e, pr=p: self._pedir_eliminar(pr)),
                ], spacing=0)),
            ]) for p in self._repo.listar(self.txt_buscar.value or "")]
        if actualizar:
            self._page.update()

    def _guardar(self, e) -> None:
        try:
            producto = Producto(self.txt_nombre.value, self.dd_categoria.value or "",
                                self.txt_precio.value, self.txt_stock.value,
                                id=self._editando_id)
            if self._editando_id is None:
                self._repo.agregar(producto)
                mostrar_mensaje(self._page, "Producto agregado.")
            else:
                self._repo.actualizar(producto)
                mostrar_mensaje(self._page, "Producto actualizado.")
        except ValueError as err:
            mostrar_mensaje(self._page, str(err), error=True)
            return
        self._cancelar(None)

    def _cargar(self, p: Producto) -> None:
        self._editando_id = p.id
        self.txt_nombre.value, self.dd_categoria.value = p.nombre, p.categoria
        self.txt_precio.value, self.txt_stock.value = str(int(p.precio)), str(p.stock)
        self.btn_guardar.content = "Guardar cambios"
        self.btn_cancelar.visible = True
        self._page.update()

    def _cancelar(self, e) -> None:
        self._editando_id = None
        self.txt_nombre.value = self.txt_precio.value = self.txt_stock.value = ""
        self.dd_categoria.value = None
        self.btn_guardar.content = "Agregar producto"
        self.btn_cancelar.visible = False
        self.refrescar()

    def _pedir_eliminar(self, p: Producto) -> None:
        confirmar(self._page, "Eliminar producto", f"¿Eliminar '{p.nombre}'?",
                  lambda: self._eliminar(p))

    def _eliminar(self, p: Producto) -> None:
        try:
            self._repo.eliminar(p.id)
            mostrar_mensaje(self._page, "Producto eliminado.")
        except sqlite3.IntegrityError:
            mostrar_mensaje(self._page, "No se puede eliminar: el producto aparece en ventas.", error=True)
        self.refrescar()
