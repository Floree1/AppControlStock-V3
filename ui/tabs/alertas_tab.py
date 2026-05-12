import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class AlertasTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.LabelFrame(self, text="Productos con Stock Bajo", padding=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Actualizar Lista", command=self.cargar_alertas).pack()
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)
        self.tree_alertas = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "SKU", "Cant. Actual", "Cant. Mínima"), show="headings")
        self.tree_alertas.heading("ID", text="ID"); self.tree_alertas.column("ID", width=50, anchor="center")
        self.tree_alertas.heading("Nombre", text="Nombre"); self.tree_alertas.column("Nombre", width=300)
        self.tree_alertas.heading("SKU", text="SKU"); self.tree_alertas.column("SKU", width=150, anchor="center")
        self.tree_alertas.heading("Cant. Actual", text="Cant. Actual"); self.tree_alertas.column("Cant. Actual", width=100, anchor="center")
        self.tree_alertas.heading("Cant. Mínima", text="Cant. Mínima"); self.tree_alertas.column("Cant. Mínima", width=100, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscrollcommand=scrollbar.set)
        self.tree_alertas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")

    def cargar_alertas(self):
        for item in self.tree_alertas.get_children(): self.tree_alertas.delete(item)
        for prod in self.db.obtener_productos_bajo_stock():
            self.tree_alertas.insert("", "end", values=prod)

