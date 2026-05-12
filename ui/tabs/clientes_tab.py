import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from ui.tabs.ventana_cuenta_corriente import CuentaClienteWindow

class ClientesTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        search_frame = ttk.LabelFrame(top_frame, text="Buscar Cliente", padding=(10,5))
        search_frame.pack(fill="x", expand=True, side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.cargar_clientes())
        ttk.Label(search_frame, text="Buscar por Nombre:").pack(side="left", padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", padx=5, fill="x", expand=True)

        actions_frame = ttk.Frame(top_frame)
        actions_frame.pack(side="left", padx=20)
        self.manage_account_button = ttk.Button(actions_frame, text="Gestionar Cuenta Corriente", command=self.gestionar_cuenta, state="disabled")
        self.manage_account_button.pack(pady=5)

        input_frame = ttk.LabelFrame(self, text="Datos del Cliente", padding=(10, 10))
        input_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(input_frame, text="Nombre Completo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_entry = ttk.Entry(input_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="we")
        ttk.Label(input_frame, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.telefono_entry = ttk.Entry(input_frame, width=20)
        self.telefono_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="Email:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(input_frame, width=30)
        self.email_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="Dirección:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.direccion_entry = ttk.Entry(input_frame, width=40)
        self.direccion_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="we")
        
        button_frame = ttk.Frame(self, padding=(10, 5))
        button_frame.pack(fill="x", padx=10)
        ttk.Button(button_frame, text="Agregar", command=self.agregar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)
        
        tree_frame = ttk.Frame(self, padding=(10, 10))
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Teléfono", "Email", "Dirección", "Saldo"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40, anchor="center")
        self.tree.heading("Nombre", text="Nombre"); self.tree.column("Nombre", width=200)
        self.tree.heading("Teléfono", text="Teléfono"); self.tree.column("Teléfono", width=120)
        self.tree.heading("Email", text="Email"); self.tree.column("Email", width=200)
        self.tree.heading("Dirección", text="Dirección"); self.tree.column("Dirección", width=250)
        self.tree.heading("Saldo", text="Saldo Deudor ($)"); self.tree.column("Saldo", width=120, anchor="e")
        
        self.tree.tag_configure('debt', background='#ffdddd')
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

    def cargar_clientes(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for cliente in self.db.obtener_registros('clientes', self.search_var.get()):
            saldo = cliente[5]
            tags = ('debt',) if saldo > 0 else ()
            valores = (cliente[0], cliente[1], cliente[2], cliente[3], cliente[4], f"{saldo:.2f}")
            self.tree.insert("", "end", values=valores, tags=tags)
        self.manage_account_button.config(state="disabled")

    def agregar_cliente(self):
        if not self.nombre_entry.get(): messagebox.showwarning("Campo Obligatorio", "El nombre es obligatorio."); return
        data = {'nombre': self.nombre_entry.get(), 'telefono': self.telefono_entry.get(), 'email': self.email_entry.get(), 'direccion': self.direccion_entry.get()}
        if self.db.agregar_registro('clientes', data):
            messagebox.showinfo("Éxito", "Cliente agregado."); self.limpiar_campos(); self.cargar_clientes()

    def actualizar_cliente(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        data = {'nombre': self.nombre_entry.get(), 'telefono': self.telefono_entry.get(), 'email': self.email_entry.get(), 'direccion': self.direccion_entry.get()}
        if self.db.actualizar_registro('clientes', data, item_id):
            messagebox.showinfo("Éxito", "Cliente actualizado."); self.limpiar_campos(); self.cargar_clientes()

    def eliminar_cliente(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente? Todas sus ventas y deudas asociadas se eliminarán."):
            if self.db.eliminar_registro('clientes', item_id):
                messagebox.showinfo("Éxito", "Cliente eliminado."); self.limpiar_campos(); self.cargar_clientes()

    def seleccionar_cliente(self, event):
        item = self.tree.focus()
        if not item: 
            self.manage_account_button.config(state="disabled")
            return
        
        self.manage_account_button.config(state="normal")
        values = self.tree.item(item, 'values')
        self.limpiar_campos()
        self.nombre_entry.insert(0, values[1]); self.telefono_entry.insert(0, values[2])
        self.email_entry.insert(0, values[3]); self.direccion_entry.insert(0, values[4])

    def limpiar_campos(self):
        for entry in [self.nombre_entry, self.telefono_entry, self.email_entry, self.direccion_entry]:
            entry.delete(0, tk.END)
        self.nombre_entry.focus()
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.manage_account_button.config(state="disabled")
        
    def obtener_id_seleccionado(self):
        item = self.tree.focus()
        if not item: messagebox.showwarning("Sin Selección", "Seleccione un cliente de la lista."); return None
        return self.tree.item(item, 'values')[0]

    def gestionar_cuenta(self):
        cliente_id = self.obtener_id_seleccionado()
        if not cliente_id: return
        
        CuentaClienteWindow(self, self.db, cliente_id)

