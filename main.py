import flet as ft
import os
import uvicorn
from fastapi import FastAPI
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flet app
def flet_main(page: ft.Page):
    page.title = "OTC Medicine Marketplace"
    page.add(ft.Text("Hello from Flet (FastAPI)"))

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Flet app is running at /flet"}

# Mount Flet at /flet
ft.fastapi.FastAPIAdapter(flet_main, "/flet").mount(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
