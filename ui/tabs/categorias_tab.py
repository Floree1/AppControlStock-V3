import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class CategoriasTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Datos de la Categoría", padding=10)
        input_frame.pack(fill="x", pady=10)

        ttk.Label(input_frame, text="Nombre:").pack(side="left", padx=5)
        self.nombre_entry = ttk.Entry(input_frame, width=40)
        self.nombre_entry.pack(side="left", padx=5)

        button_frame = ttk.Frame(main_frame, padding=(0, 10))
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Agregar", command=self.agregar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)

        tree_frame = ttk.Frame(main_frame, padding=(0, 10))
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=100)
        self.tree.heading("Nombre", text="Nombre de la Categoría")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_categoria)

    def cargar_categorias(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for cat in self.db.obtener_categorias():
            self.tree.insert("", "end", values=cat)
        self.limpiar_campos()

    def agregar_categoria(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Campo Vacío", "El nombre de la categoría no puede estar vacío.")
            return
        if self.db.agregar_registro('categorias', {'nombre': nombre}):
            messagebox.showinfo("Éxito", "Categoría agregada.")
            self.cargar_categorias()
        else:
            messagebox.showerror("Error", "La categoría ya existe o hubo un error al guardarla.")

    def actualizar_categoria(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Campo Vacío", "El nombre de la categoría no puede estar vacío.")
            return
        if self.db.actualizar_registro('categorias', {'nombre': nombre}, item_id):
            messagebox.showinfo("Éxito", "Categoría actualizada.")
            self.cargar_categorias()

    def eliminar_categoria(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        
        productos_count = self.db.productos_en_categoria(item_id)
        if productos_count > 0:
            messagebox.showerror("Error", f"No se puede eliminar la categoría porque {productos_count} producto(s) la están usando.")
            return

        if messagebox.askyesno("Confirmar", "¿Eliminar esta categoría?"):
            if self.db.eliminar_registro('categorias', item_id):
                messagebox.showinfo("Éxito", "Categoría eliminada.")
                self.cargar_categorias()

    def seleccionar_categoria(self, event):
        item = self.tree.focus()
        if not item: return
        values = self.tree.item(item, 'values')
        self.limpiar_campos(clear_selection=False)
        self.nombre_entry.insert(0, values[1])

    def limpiar_campos(self, clear_selection=True):
        self.nombre_entry.delete(0, tk.END)
        if clear_selection and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def obtener_id_seleccionado(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Sin Selección", "Seleccione una categoría de la lista.")
            return None
        return self.tree.item(item, 'values')[0]


