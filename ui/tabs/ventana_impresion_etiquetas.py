import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from core.utils import generar_etiquetas_pdf
import os

class LabelPrintWindow(tk.Toplevel):
    def __init__(self, parent, productos):
        super().__init__(parent)
        self.productos = productos
        self.entries = {}
        
        self.title("Imprimir Etiquetas de Productos")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Especifique la cantidad de etiquetas para cada producto:", font=("Helvetica", 11, "bold")).pack(pady=(0, 10))

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, prod in enumerate(self.productos):
            prod_id, nombre, sku, _, precio, _, _, _ = prod
            
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill="x", pady=5)
            
            label_text = f"{nombre[:30]}... (SKU: {sku})" if len(nombre) > 30 else f"{nombre} (SKU: {sku})"
            ttk.Label(row_frame, text=label_text).pack(side="left", expand=True, fill="x", padx=5)
            
            qty_entry = ttk.Entry(row_frame, width=5)
            qty_entry.insert(0, "1")
            qty_entry.pack(side="right")
            self.entries[prod_id] = (qty_entry, prod)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(self, text="Generar PDF de Etiquetas", command=self.generar_pdf).pack(pady=10)

    def generar_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('Archivos PDF', '*.pdf'), ('Todos', '*.*')], initialfile=f"etiquetas-{datetime.datetime.now().strftime('%Y-%m-%d')}.pdf")
        if not filepath: return
        productos_cantidades = []
        for prod_id, (qty_entry, prod) in self.entries.items():
            try: cant = int(qty_entry.get())
            except: cant = 0
            productos_cantidades.append((cant, prod))
        if generar_etiquetas_pdf(productos_cantidades, filepath):
            messagebox.showinfo('Éxito', f'PDF generado en:\n{filepath}')
        self.destroy()
