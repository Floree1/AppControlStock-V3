import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

class LoginWindow:
    def __init__(self, root, db, config_manager, callback):
        self.root = root
        self.db = db
        self.config_manager = config_manager
        self.callback = callback
        
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.login_window.geometry("450x300")
        self.login_window.resizable(False, False)
        
        # Centrar ventana
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        x = (screen_width / 2) - (450 / 2)
        y = (screen_height / 2) - (300 / 2)
        self.login_window.geometry(f'450x300+{int(x)}+{int(y)}')
        
        self.login_window.protocol("WM_DELETE_WINDOW", self.root.quit)
        self.crear_widgets_login()

    def crear_widgets_login(self):
        main_frame = ttk.Frame(self.login_window, padding=(30, 20))
        main_frame.pack(expand=True, fill="both")

        # --- Logo ---
        self.logo_label = ttk.Label(main_frame)
        self.logo_label.pack(pady=(0, 20))
        self.load_logo()

        # --- Formulario de Login ---
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(expand=True)
        
        ttk.Label(login_frame, text="Usuario:", font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.user_entry = ttk.Entry(login_frame, font=("Helvetica", 11), width=25)
        self.user_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(login_frame, text="Contraseña:", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.pass_entry = ttk.Entry(login_frame, show="*", font=("Helvetica", 11), width=25)
        self.pass_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.pass_entry.bind("<Return>", self.verificar_login)
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())
        
        btn_ingresar = ttk.Button(login_frame, text="Ingresar", command=self.verificar_login, width=20)
        btn_ingresar.grid(row=2, column=0, columnspan=2, pady=25)
        
        self.user_entry.focus()

    def load_logo(self):
        logo_path = self.config_manager.get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((250, 80)) # Redimensionar para mejor encaje
                self.logo_photo = ImageTk.PhotoImage(img)
                self.logo_label.config(image=self.logo_photo)
            except Exception as e:
                print(f"Error al cargar el logo: {e}")

    def verificar_login(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Campos vacíos", "Por favor, ingrese usuario y contraseña.")
            return

        user_data = self.db.verificar_usuario_y_obtener_rol(username, password)
        if user_data:
            self.login_window.destroy()
            self.callback(user_data) # Pasa la tupla (id, username, rol)
        else:
            messagebox.showerror("Error de Acceso", "Usuario o contraseña incorrectos.")
            self.pass_entry.delete(0, tk.END)
