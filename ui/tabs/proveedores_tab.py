import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class ProveedoresTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        search_frame = ttk.LabelFrame(self, text="Buscar Proveedor", padding=(10,5))
        search_frame.pack(fill="x", padx=10, pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.cargar_proveedores())
        ttk.Label(search_frame, text="Buscar por Nombre:").pack(side="left", padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        
        input_frame = ttk.LabelFrame(self, text="Datos del Proveedor", padding=(10, 10))
        input_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(input_frame, text="Nombre Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_entry = ttk.Entry(input_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="we")
        ttk.Label(input_frame, text="Contacto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.contacto_entry = ttk.Entry(input_frame, width=40)
        self.contacto_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="Teléfono:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.telefono_entry = ttk.Entry(input_frame, width=20)
        self.telefono_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(input_frame, width=40)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="we")

        button_frame = ttk.Frame(self, padding=(10, 5))
        button_frame.pack(fill="x", padx=10)
        ttk.Button(button_frame, text="Agregar", command=self.agregar_proveedor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_proveedor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_proveedor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)
        
        tree_frame = ttk.Frame(self, padding=(10, 10))
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Contacto", "Teléfono", "Email"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40, anchor="center")
        self.tree.heading("Nombre", text="Nombre Empresa"); self.tree.column("Nombre", width=250)
        self.tree.heading("Contacto", text="Contacto"); self.tree.column("Contacto", width=200)
        self.tree.heading("Teléfono", text="Teléfono"); self.tree.column("Teléfono", width=120)
        self.tree.heading("Email", text="Email"); self.tree.column("Email", width=200)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_proveedor)

    def cargar_proveedores(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for prov in self.db.obtener_registros('proveedores', self.search_var.get()):
            self.tree.insert("", "end", values=prov)

    def agregar_proveedor(self):
        if not self.nombre_entry.get(): messagebox.showwarning("Campo Obligatorio", "El nombre de la empresa es obligatorio."); return
        data = {'nombre': self.nombre_entry.get(), 'contacto': self.contacto_entry.get(), 'telefono': self.telefono_entry.get(), 'email': self.email_entry.get()}
        if self.db.agregar_registro('proveedores', data):
            messagebox.showinfo("Éxito", "Proveedor agregado."); self.limpiar_campos(); self.cargar_proveedores()

    def actualizar_proveedor(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        data = {'nombre': self.nombre_entry.get(), 'contacto': self.contacto_entry.get(), 'telefono': self.telefono_entry.get(), 'email': self.email_entry.get()}
        if self.db.actualizar_registro('proveedores', data, item_id):
            messagebox.showinfo("Éxito", "Proveedor actualizado."); self.limpiar_campos(); self.cargar_proveedores()

    def eliminar_proveedor(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este proveedor?"):
            if self.db.eliminar_registro('proveedores', item_id):
                messagebox.showinfo("Éxito", "Proveedor eliminado."); self.limpiar_campos(); self.cargar_proveedores()

    def seleccionar_proveedor(self, event):
        item = self.tree.focus()
        if not item: return
        values = self.tree.item(item, 'values')
        self.limpiar_campos()
        self.nombre_entry.insert(0, values[1]); self.contacto_entry.insert(0, values[2])
        self.telefono_entry.insert(0, values[3]); self.email_entry.insert(0, values[4])

    def limpiar_campos(self):
        for entry in [self.nombre_entry, self.contacto_entry, self.telefono_entry, self.email_entry]:
            entry.delete(0, tk.END)
        self.nombre_entry.focus()
        
    def obtener_id_seleccionado(self):
        item = self.tree.focus()
        if not item: messagebox.showwarning("Sin Selección", "Seleccione un proveedor de la lista."); return None
        return self.tree.item(item, 'values')[0]

