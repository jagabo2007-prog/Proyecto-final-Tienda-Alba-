import os
import flet as ft
from data.database_manager import inicializar_bd
from data.datos_demo import cargar_datos_demo
from ui.app_view import AppView

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tienda.db")


def main(page: ft.Page) -> None:
    AppView(page, RUTA_BD).construir()


if __name__ == "__main__":
    inicializar_bd(RUTA_BD)
    cargar_datos_demo(RUTA_BD)
    ft.run(main)
