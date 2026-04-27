import flet as ft
import os

def main(page: ft.Page):
    page.add(ft.Text("Hello from Flet!"))

ft.run(main, port=int(os.getenv("PORT", 8000)))
