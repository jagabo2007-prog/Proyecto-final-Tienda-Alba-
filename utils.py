import flet as ft


def mostrar_mensaje(page: ft.Page, texto: str, error: bool = False) -> None:
    page.show_dialog(ft.SnackBar(
        content=ft.Text(texto, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700))


def confirmar(page: ft.Page, titulo: str, texto: str, al_aceptar) -> None:
    def aceptar(e):
        page.pop_dialog()
        al_aceptar()

    page.show_dialog(ft.AlertDialog(
        modal=True, title=ft.Text(titulo), content=ft.Text(texto),
        actions=[ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                 ft.Button("Aceptar", on_click=aceptar)]))
