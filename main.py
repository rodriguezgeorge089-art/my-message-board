import flet as ft
import os
from supabase import create_client, Client

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "OTC Medicine Marketplace"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Store current user session
    current_user = None

    def show_snackbar(text, color="black"):
        page.snack_bar = ft.SnackBar(ft.Text(text, color=color), open=True)
        page.update()

    # ----- Sign Up View -----
    def signup_view():
        email = ft.TextField(label="Email", width=300)
        password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        full_name = ft.TextField(label="Full Name", width=300)
        role = ft.Dropdown(label="I am a", options=[
            ft.dropdown.Option("buyer", "Buyer (Customer)"),
            ft.dropdown.Option("seller", "Seller (Pharmacy)")
        ], width=300)

        def do_signup(e):
            nonlocal current_user
            try:
                # Create auth user
                auth_response = supabase.auth.sign_up({
                    "email": email.value,
                    "password": password.value,
                    "options": {"data": {"full_name": full_name.value}}
                })
                # Update profile with role
                user = auth_response.user
                if user:
                    supabase.table("profiles").update({"role": role.value}).eq("user_id", user.id).execute()
                    show_snackbar("Account created! Please check your email to confirm.", "green")
                    # Clear fields
                    email.value, password.value, full_name.value = "", "", ""
                    page.go("/login")
            except Exception as ex:
                show_snackbar(f"Error: {ex}", "red")
            page.update()

        return ft.Column([
            ft.Text("Create Account", style="headlineMedium"),
            full_name, email, password, role,
            ft.ElevatedButton("Sign Up", on_click=do_signup),
            ft.TextButton("Already have an account? Log in", on_click=lambda _: page.go("/login"))
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ----- Login View -----
    def login_view():
        email = ft.TextField(label="Email", width=300)
        password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)

        def do_login(e):
            nonlocal current_user
            try:
                response = supabase.auth.sign_in_with_password({"email": email.value, "password": password.value})
                current_user = response.user
                if current_user:
                    show_snackbar("Logged in!", "green")
                    page.go("/dashboard")
            except Exception as ex:
                show_snackbar(f"Login failed: {ex}", "red")
            page.update()

        return ft.Column([
            ft.Text("Login", style="headlineMedium"),
            email, password,
            ft.ElevatedButton("Log In", on_click=do_login),
            ft.TextButton("Don't have an account? Sign up", on_click=lambda _: page.go("/signup"))
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ----- Dashboard View -----
    def dashboard_view():
        if not current_user:
            page.go("/login")
            return ft.Text("Redirecting...")

        # Get user profile
        profile = supabase.table("profiles").select("*").eq("user_id", current_user.id).single().execute()
        if profile.data:
            user_role = profile.data['role']
            full_name = profile.data.get('full_name', 'User')
        else:
            user_role = 'unknown'
            full_name = 'User'

        def logout(e):
            nonlocal current_user
            supabase.auth.sign_out()
            current_user = None
            page.go("/login")

        return ft.Column([
            ft.Text(f"Welcome, {full_name} ({user_role})", style="headlineSmall"),
            ft.ElevatedButton("Logout", on_click=logout),
            ft.Text("Marketplace features coming soon...")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ----- Route management -----
    def route_change(route):
        page.controls.clear()
        if page.route == "/signup":
            page.controls.append(signup_view())
        elif page.route == "/login":
            page.controls.append(login_view())
        elif page.route == "/dashboard":
            page.controls.append(dashboard_view())
        else:
            # Default: go to login
            page.go("/login")
        page.update()

    page.on_route_change = route_change
    page.go("/login")

ft.run(main, port=int(os.getenv("PORT", 8000)))
