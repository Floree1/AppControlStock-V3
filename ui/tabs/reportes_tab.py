import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv

class ReportesTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        filtros_frame = ttk.LabelFrame(self, text="Filtros de Ventas", padding=10)
        filtros_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(filtros_frame, text="Desde (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fecha_inicio_entry = ttk.Entry(filtros_frame)
        self.fecha_inicio_entry.grid(row=0, column=1, padx=5, pady=5)
        self.fecha_inicio_entry.insert(0, (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Label(filtros_frame, text="Hasta (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.fecha_fin_entry = ttk.Entry(filtros_frame)
        self.fecha_fin_entry.grid(row=0, column=3, padx=5, pady=5)
        self.fecha_fin_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        ttk.Label(filtros_frame, text="Categoría:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.category_filter_combo = ttk.Combobox(filtros_frame, state="readonly", width=20)
        self.category_filter_combo.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(filtros_frame, text="Aplicar Filtros", command=self.aplicar_filtros).grid(row=0, column=6, padx=10, pady=5)
        ttk.Button(filtros_frame, text="Exportar a CSV", command=self.exportar_a_csv).grid(row=0, column=7, padx=10, pady=5)
        
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)
        ventas_frame = ttk.LabelFrame(paned_window, text="Listado de Ventas", padding=10)
        paned_window.add(ventas_frame, weight=2)
        self.tree_ventas = ttk.Treeview(ventas_frame, columns=("ID", "Fecha", "Cliente", "Total", "Método", "Vendedor"), show="headings")
        self.tree_ventas.heading("ID", text="ID"); self.tree_ventas.column("ID", width=50, anchor="center")
        self.tree_ventas.heading("Fecha", text="Fecha"); self.tree_ventas.column("Fecha", width=150)
        self.tree_ventas.heading("Cliente", text="Cliente"); self.tree_ventas.column("Cliente", width=200)
        self.tree_ventas.heading("Total", text="Total ($)"); self.tree_ventas.column("Total", width=100, anchor="e")
        self.tree_ventas.heading("Método", text="Método Pago"); self.tree_ventas.column("Método", width=100, anchor="center")
        self.tree_ventas.heading("Vendedor", text="Vendedor"); self.tree_ventas.column("Vendedor", width=100, anchor="center")
        self.tree_ventas.pack(fill="both", expand=True)
        self.tree_ventas.bind("<<TreeviewSelect>>", self.mostrar_detalles_venta)
        
        detalles_frame = ttk.LabelFrame(paned_window, text="Detalles de la Venta Seleccionada", padding=10)
        paned_window.add(detalles_frame, weight=1)
        self.tree_detalles = ttk.Treeview(detalles_frame, columns=("Producto", "Cant", "P. Unit", "Subtotal"), show="headings")
        self.tree_detalles.heading("Producto", text="Producto"); self.tree_detalles.column("Producto", width=120)
        self.tree_detalles.heading("Cant", text="Cant."); self.tree_detalles.column("Cant", width=40, anchor="center")
        self.tree_detalles.heading("P. Unit", text="P. Unit ($)"); self.tree_detalles.column("P. Unit", width=70, anchor="e")
        self.tree_detalles.heading("Subtotal", text="Subtotal ($)"); self.tree_detalles.column("Subtotal", width=70, anchor="e")
        self.tree_detalles.pack(fill="both", expand=True)

    def cargar_filtros(self):
        categorias = self.db.obtener_categorias()
        self.category_map = {nombre: id for id, nombre in categorias}
        self.category_filter_combo['values'] = ["Todas"] + list(self.category_map.keys())
        self.category_filter_combo.set("Todas")
        self.aplicar_filtros()

    def aplicar_filtros(self):
        fecha_inicio, fecha_fin = self.fecha_inicio_entry.get() + " 00:00:00", self.fecha_fin_entry.get() + " 23:59:59"
        try:
            datetime.datetime.strptime(self.fecha_inicio_entry.get(), "%Y-%m-%d")
            datetime.datetime.strptime(self.fecha_fin_entry.get(), "%Y-%m-%d")
        except ValueError: messagebox.showerror("Error de Formato", "Use el formato YYYY-MM-DD para las fechas."); return
        
        categoria_nombre = self.category_filter_combo.get()
        categoria_id = self.category_map.get(categoria_nombre) if categoria_nombre != "Todas" else None

        for item in self.tree_ventas.get_children(): self.tree_ventas.delete(item)
        for venta in self.db.obtener_ventas_con_cliente(fecha_inicio, fecha_fin, categoria_id):
            valores = (venta[0], venta[1], venta[2], f"{venta[3]:.2f}", venta[4], venta[5])
            self.tree_ventas.insert("", "end", values=valores)
        for item in self.tree_detalles.get_children(): self.tree_detalles.delete(item)
        
    def mostrar_detalles_venta(self, event):
        item_seleccionado = self.tree_ventas.focus()
        if not item_seleccionado: return
        venta_id = self.tree_ventas.item(item_seleccionado, 'values')[0]
        for item in self.tree_detalles.get_children(): self.tree_detalles.delete(item)
        for detalle in self.db.obtener_detalles_venta(venta_id):
            nombre, cant, p_unit, subtotal, c_unit, descuento = detalle
            valores = (nombre, cant, f"{p_unit:.2f}", f"{subtotal:.2f}")
            self.tree_detalles.insert("", "end", values=valores)

    def exportar_a_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
        if not filepath: return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID Venta", "Fecha", "Cliente", "Total", "Metodo de Pago", "Vendedor"])
                for item_id in self.tree_ventas.get_children():
                    writer.writerow(self.tree_ventas.item(item_id, 'values'))
            messagebox.showinfo("Éxito", f"Datos exportados a\n{filepath}")
        except IOError as e: messagebox.showerror("Error de Exportación", f"No se pudo guardar el archivo: {e}")

