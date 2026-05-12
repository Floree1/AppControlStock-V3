import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class AdminTab(ttk.Frame):
    def __init__(self, parent, db, root_window, app_instance):
        super().__init__(parent)
        self.db = db
        self.root_window = root_window
        self.app = app_instance
        self.crear_widgets()

    def crear_widgets(self):
        # --- Frame de Gestión de Usuarios ---
        user_management_frame = ttk.LabelFrame(self, text="Gestión de Usuarios", padding=(10, 10))
        user_management_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(user_management_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.user_entry = ttk.Entry(user_management_frame, width=30)
        self.user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(user_management_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pass_entry = ttk.Entry(user_management_frame, width=30, show="*")
        self.pass_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(user_management_frame, text="Rol:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.rol_combo = ttk.Combobox(user_management_frame, state="readonly", values=["Administrador", "Vendedor"])
        self.rol_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.rol_combo.set("Vendedor")

        button_frame = ttk.Frame(user_management_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Agregar", command=self.agregar_usuario).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_usuario).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_usuario).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)

        tree_frame = ttk.Frame(user_management_frame)
        tree_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        user_management_frame.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Rol"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Username", text="Username"); self.tree.column("Username", width=200)
        self.tree.heading("Rol", text="Rol"); self.tree.column("Rol", width=150)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_usuario)

        # --- Frame de Personalización y Backup ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        personalization_frame = ttk.LabelFrame(bottom_frame, text="Personalización", padding=(10, 10))
        personalization_frame.pack(side="left", padx=(0, 10), fill="x", expand=True)
        ttk.Button(personalization_frame, text="Seleccionar Logo de la Empresa", command=self.select_logo).pack(pady=5)

        backup_frame = ttk.LabelFrame(bottom_frame, text="Copia de Seguridad y Restauración", padding=(10, 10))
        backup_frame.pack(side="left", fill="x", expand=True)
        ttk.Button(backup_frame, text="Crear Copia de Seguridad", command=self.db.backup_database).pack(side="left", padx=10, pady=10)
        ttk.Button(backup_frame, text="Restaurar Base de Datos", command=self.restaurar_y_salir).pack(side="left", padx=10, pady=10)

    def select_logo(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de logo",
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.gif"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.app.config_manager.set_logo_path(filepath)
            self.app.load_and_display_logo()
            messagebox.showinfo("Logo Actualizado", "El logo se ha actualizado. Se mostrará la próxima vez que inicie sesión.")

    def restaurar_y_salir(self):
        if self.db.restore_database():
            self.root_window.destroy()

    def cargar_usuarios(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for user in self.db.obtener_usuarios():
            self.tree.insert("", "end", values=user)

    def agregar_usuario(self):
        username, password, rol = self.user_entry.get(), self.pass_entry.get(), self.rol_combo.get()
        if not all([username, password, rol]):
            messagebox.showwarning("Campos Vacíos", "Username, contraseña y rol son obligatorios para agregar un usuario.")
            return
        if self.db.agregar_usuario(username, password, rol):
            messagebox.showinfo("Éxito", "Usuario agregado correctamente.")
            self.limpiar_campos()
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "El nombre de usuario ya existe. Por favor, elija otro.")

    def actualizar_usuario(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        username, password, rol = self.user_entry.get(), self.pass_entry.get(), self.rol_combo.get()
        if not all([username, rol]):
            messagebox.showwarning("Campos Vacíos", "Username y rol son obligatorios para actualizar.")
            return
        if self.db.actualizar_usuario(item_id, username, password, rol):
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
            self.limpiar_campos()
            self.cargar_usuarios()

    def eliminar_usuario(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        if int(item_id) == 1:
            messagebox.showerror("Acción no permitida", "No se puede eliminar al usuario administrador principal.")
            return
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar al usuario '{self.user_entry.get()}'?"):
            if self.db.eliminar_registro('usuarios', item_id):
                messagebox.showinfo("Éxito", "Usuario eliminado.")
                self.limpiar_campos()
                self.cargar_usuarios()

    def seleccionar_usuario(self, event):
        item = self.tree.focus()
        if not item: return
        values = self.tree.item(item, 'values')
        self.limpiar_campos()
        self.user_entry.insert(0, values[1])
        self.rol_combo.set(values[2])
        self.pass_entry.config(show="")
        self.pass_entry.insert(0, "(sin cambiar)")

    def limpiar_campos(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.config(show="*")
        self.rol_combo.set("Vendedor")
        self.user_entry.focus()
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def obtener_id_seleccionado(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un usuario de la lista.")
            return None
        return self.tree.item(item, 'values')[0]

