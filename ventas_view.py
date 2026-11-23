import flet as ft
from data.cliente_dao import ClienteDAO
from data.producto_repository import ProductoRepository
from data.venta_repository import VentaRepository
from domain.venta import Venta, DetalleVenta
from ui.components.utils import mostrar_mensaje, confirmar


class VentasView(ft.Column):
    def __init__(self, page: ft.Page, cliente_dao: ClienteDAO,
                 producto_repo: ProductoRepository, venta_repo: VentaRepository) -> None:
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=12)
        self._page = page
        self._clientes, self._productos, self._ventas = cliente_dao, producto_repo, venta_repo
        self._carrito: Venta | None = None

        self.dd_cliente = ft.Dropdown(label="Cliente", width=260)
        self.dd_producto = ft.Dropdown(label="Producto", width=260)
        self.txt_cantidad = ft.TextField(label="Cantidad", width=110, value="1",
                                         keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_agregar = ft.Button("Agregar al carrito", icon=ft.Icons.ADD_SHOPPING_CART,
                                     on_click=self._agregar_item)
        self.lbl_total = ft.Text("Total: $0", size=18, weight=ft.FontWeight.BOLD)
        self.btn_registrar = ft.Button("Registrar venta", icon=ft.Icons.POINT_OF_SALE,
                                       on_click=self._registrar)
        self.tabla_carrito = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in
                     ("Producto", "Cant.", "Precio", "Subtotal", "")], rows=[])
        self.tabla_ventas = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(t)) for t in
                     ("N°", "Fecha", "Cliente", "Total", "Acciones")],
            rows=[], heading_row_color=ft.Colors.BLUE_GREY_50)

        self.controls = [
            ft.Text("Ventas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([self.dd_cliente, self.dd_producto, self.txt_cantidad], wrap=True),
            self.btn_agregar,
            ft.Row([self.tabla_carrito], scroll=ft.ScrollMode.AUTO),
            ft.Row([self.lbl_total, self.btn_registrar]),
            ft.Divider(),
            ft.Text("Historial de ventas", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([self.tabla_ventas], scroll=ft.ScrollMode.AUTO),
        ]
        self.refrescar(actualizar=False)


    def refrescar(self, actualizar: bool = True) -> None:
        cliente_sel, producto_sel = self.dd_cliente.value, self.dd_producto.value
        self.dd_cliente.options = [ft.DropdownOption(key=str(c.id), text=c.nombre)
                                   for c in self._clientes.listar()]
        self.dd_producto.options = [ft.DropdownOption(key=str(p.id), text=f"{p.nombre} (stock {p.stock})")
                                    for p in self._productos.listar()]
        self.dd_cliente.value, self.dd_producto.value = cliente_sel, producto_sel
        self._pintar_carrito()
        self.tabla_ventas.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(v.id))), ft.DataCell(ft.Text(v.fecha)),
                ft.DataCell(ft.Text(v.nombre_cliente)), ft.DataCell(ft.Text(f"${v.total:,.0f}")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.RECEIPT_LONG, tooltip="Ver detalle",
                                  on_click=lambda e, ve=v: self._ver_detalle(ve)),
                    ft.IconButton(ft.Icons.EDIT, tooltip="Cambiar cliente",
                                  on_click=lambda e, ve=v: self._cambiar_cliente(ve)),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_600, tooltip="Anular venta",
                                  on_click=lambda e, ve=v: self._pedir_anular(ve)),
                ], spacing=0)),
            ]) for v in self._ventas.listar()]
        if actualizar:
            self._page.update()

    def _pintar_carrito(self) -> None:
        detalles = self._carrito.detalles if self._carrito else []
        self.tabla_carrito.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(d.nombre_producto)), ft.DataCell(ft.Text(str(d.cantidad))),
                ft.DataCell(ft.Text(f"${d.precio_unitario:,.0f}")),
                ft.DataCell(ft.Text(f"${d.subtotal:,.0f}")),
                ft.DataCell(ft.IconButton(ft.Icons.CLOSE, on_click=lambda e, x=d: self._quitar_item(x))),
            ]) for d in detalles]
        total = self._carrito.total if self._carrito else 0
        self.lbl_total.value = f"Total: ${total:,.0f}"


    def _agregar_item(self, e) -> None:
        if not self.dd_producto.value:
            mostrar_mensaje(self._page, "Seleccione un producto.", error=True)
            return
        try:
            cantidad = int(self.txt_cantidad.value)
            producto = self._productos.obtener(int(self.dd_producto.value))
            if cantidad > producto.stock:
                raise ValueError(f"Solo hay {producto.stock} unidades de '{producto.nombre}'.")
            if self._carrito is None:
                self._carrito = Venta(cliente_id=0)
            self._carrito.agregar_detalle(
                DetalleVenta(producto.id, cantidad, producto.precio, producto.nombre))
        except ValueError as err:
            mostrar_mensaje(self._page, str(err) if "unidades" in str(err) or "cantidad" in str(err)
                            else "Ingrese una cantidad entera válida.", error=True)
            return
        self._pintar_carrito()
        self._page.update()

    def _quitar_item(self, detalle: DetalleVenta) -> None:
        self._carrito.quitar_detalle(detalle.producto_id)
        self._pintar_carrito()
        self._page.update()

    def _registrar(self, e) -> None:
        if not self.dd_cliente.value:
            mostrar_mensaje(self._page, "Seleccione un cliente.", error=True)
            return
        if not self._carrito or len(self._carrito) == 0:
            mostrar_mensaje(self._page, "Agregue productos al carrito.", error=True)
            return
        venta = Venta(cliente_id=int(self.dd_cliente.value))
        for d in self._carrito.detalles:
            venta.agregar_detalle(d)
        try:
            self._ventas.registrar(venta)
        except ValueError as err:
            mostrar_mensaje(self._page, str(err), error=True)
            return
        self._carrito = None
        mostrar_mensaje(self._page, "Venta registrada.")
        self.refrescar()


    def _ver_detalle(self, venta: Venta) -> None:
        lineas = [ft.Text(str(d)) for d in self._ventas.detalles_de(venta.id)]
        self._page.show_dialog(ft.AlertDialog(
            title=ft.Text(f"Venta #{venta.id} - {venta.nombre_cliente}"),
            content=ft.Column(lineas + [ft.Divider(), ft.Text(f"Total: ${venta.total:,.0f}",
                                                              weight=ft.FontWeight.BOLD)],
                              tight=True),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._page.pop_dialog())]))

    def _cambiar_cliente(self, venta: Venta) -> None:
        dd = ft.Dropdown(label="Nuevo cliente", value=str(venta.cliente_id), width=280,
                         options=[ft.DropdownOption(key=str(c.id), text=c.nombre)
                                  for c in self._clientes.listar()])

        def guardar(e):
            self._ventas.cambiar_cliente(venta.id, int(dd.value))
            self._page.pop_dialog()
            mostrar_mensaje(self._page, "Venta actualizada.")
            self.refrescar()

        self._page.show_dialog(ft.AlertDialog(
            modal=True, title=ft.Text(f"Venta #{venta.id}"), content=dd,
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self._page.pop_dialog()),
                     ft.Button("Guardar", on_click=guardar)]))

    def _pedir_anular(self, venta: Venta) -> None:
        confirmar(self._page, "Anular venta",
                  f"¿Anular la venta #{venta.id}? El stock será devuelto.",
                  lambda: self._anular(venta))

    def _anular(self, venta: Venta) -> None:
        self._ventas.eliminar(venta.id)
        mostrar_mensaje(self._page, "Venta anulada y stock restituido.")
        self.refrescar()
