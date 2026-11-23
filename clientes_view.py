import sqlite3
import flet as ft
from data.cliente_dao import ClienteDAO
from domain.cliente import Cliente
from ui.components.utils import mostrar_mensaje, confirmar


class ClientesView(ft.Column):
    def __init__(self, page: ft.Page, dao: ClienteDAO) -> None:
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=12)
        self._page, self._dao = page, dao
        self._editando_id: int | None = None

        self.txt_nombre = ft.TextField(label="Nombre", width=240)
        self.txt_telefono = ft.TextField(label="Teléfono", width=160)
        self.txt_direccion = ft.TextField(label="Dirección", width=260)
        self.txt_buscar = ft.TextField(label="Buscar por nombre", width=220,
                                       prefix_icon=ft.Icons.SEARCH,
                                       on_change=lambda e: self.refrescar())
        self.btn_guardar = ft.Button("Agregar cliente", icon=ft.Icons.SAVE, on_click=self._guardar)
        self.btn_cancelar = ft.TextButton("Cancelar edición", visible=False, on_click=self._cancelar)
        self.tabla = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in
                     ("ID", "Nombre", "Teléfono", "Dirección", "Acciones")],
            rows=[], heading_row_color=ft.Colors.BLUE_GREY_50)

        self.controls = [
            ft.Text("Clientes", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([self.txt_nombre, self.txt_telefono, self.txt_direccion], wrap=True),
            ft.Row([self.btn_guardar, self.btn_cancelar]),
            self.txt_buscar,
            ft.Row([self.tabla], scroll=ft.ScrollMode.AUTO),
        ]
        self.refrescar(actualizar=False)

    def refrescar(self, actualizar: bool = True) -> None:
        self.tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(c.id))), ft.DataCell(ft.Text(c.nombre)),
                ft.DataCell(ft.Text(c.telefono)), ft.DataCell(ft.Text(c.direccion)),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar",
                                  on_click=lambda e, cl=c: self._cargar(cl)),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_600, tooltip="Eliminar",
                                  on_click=lambda e, cl=c: self._pedir_eliminar(cl)),
                ], spacing=0)),
            ]) for c in self._dao.listar(self.txt_buscar.value or "")]
        if actualizar:
            self._page.update()

    def _guardar(self, e) -> None:
        try:
            cliente = Cliente(self.txt_nombre.value, self.txt_telefono.value,
                              self.txt_direccion.value, id=self._editando_id)
            if self._editando_id is None:
                self._dao.crear(cliente)
                mostrar_mensaje(self._page, "Cliente agregado.")
            else:
                self._dao.actualizar(cliente)
                mostrar_mensaje(self._page, "Cliente actualizado.")
        except ValueError as err:
            mostrar_mensaje(self._page, str(err), error=True)
            return
        self._cancelar(None)

    def _cargar(self, c: Cliente) -> None:
        self._editando_id = c.id
        self.txt_nombre.value, self.txt_telefono.value = c.nombre, c.telefono
        self.txt_direccion.value = c.direccion
        self.btn_guardar.content = "Guardar cambios"
        self.btn_cancelar.visible = True
        self._page.update()

    def _cancelar(self, e) -> None:
        self._editando_id = None
        self.txt_nombre.value = self.txt_telefono.value = self.txt_direccion.value = ""
        self.btn_guardar.content = "Agregar cliente"
        self.btn_cancelar.visible = False
        self.refrescar()

    def _pedir_eliminar(self, c: Cliente) -> None:
        confirmar(self._page, "Eliminar cliente", f"¿Eliminar a {c}?",
                  lambda: self._eliminar(c))

    def _eliminar(self, c: Cliente) -> None:
        try:
            self._dao.eliminar(c.id)
            mostrar_mensaje(self._page, "Cliente eliminado.")
        except sqlite3.IntegrityError:
            mostrar_mensaje(self._page, "No se puede eliminar: el cliente tiene ventas registradas.", error=True)
        self.refrescar()
