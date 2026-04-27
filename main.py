import flet as ft
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Message Board"
    
    username_field = ft.TextField(label="Your Name", width=300)
    message_field = ft.TextField(label="Message", width=300, multiline=True)
    messages_list = ft.Column()

    def load_messages():
        messages_list.controls.clear()
        try:
            res = supabase.table("messages").select("*").order("id", desc=True).limit(10).execute()
            for row in res.data:
                messages_list.controls.append(ft.Text(f"{row['username']}: {row['content']}"))
        except Exception as e:
            messages_list.controls.append(ft.Text(f"Error: {e}"))
        page.update()

    def add_message(e):
        supabase.table("messages").insert({"username": username_field.value, "content": message_field.value}).execute()
        username_field.value = ""
        message_field.value = ""
        load_messages()

    page.add(
        ft.Text("📢 Public Message Board", style="headlineLarge"),
        username_field, message_field,
        ft.ElevatedButton("Post", on_click=add_message),
        ft.ElevatedButton("Refresh", on_click=lambda _: load_messages()),
        ft.Divider(),
        ft.Text("Recent Messages:"),
        messages_list
    )
    load_messages()

ft.app(target=main, view=ft.AppView.FLET_APP)
