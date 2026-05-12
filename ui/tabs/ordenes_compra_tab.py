import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class OrdenesCompraTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        crear_frame = ttk.LabelFrame(self, text="Crear Nueva Orden de Compra", padding=10)
        crear_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(crear_frame, text="Proveedor:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.proveedor_combo = ttk.Combobox(crear_frame, state="readonly", width=30)
        self.proveedor_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        ttk.Label(crear_frame, text="Producto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.producto_combo = ttk.Combobox(crear_frame, state="readonly", width=40)
        self.producto_combo.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        ttk.Label(crear_frame, text="Cantidad:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.cantidad_entry = ttk.Entry(crear_frame, width=10)
        self.cantidad_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.cantidad_entry.insert(0, "1")
        ttk.Button(crear_frame, text="Agregar al Pedido", command=self.agregar_al_pedido).grid(row=1, column=4, padx=10, pady=5)
        self.tree_pedido = ttk.Treeview(crear_frame, columns=("ID", "Producto", "Cantidad"), show="headings", height=4)
        self.tree_pedido.grid(row=2, column=0, columnspan=5, sticky="we", pady=5)
        self.tree_pedido.heading("ID", text="ID"); self.tree_pedido.column("ID", width=50, anchor="center")
        self.tree_pedido.heading("Producto", text="Producto"); self.tree_pedido.column("Producto", width=300)
        self.tree_pedido.heading("Cantidad", text="Cantidad"); self.tree_pedido.column("Cantidad", width=100, anchor="center")
        botones_pedido_frame = ttk.Frame(crear_frame)
        botones_pedido_frame.grid(row=3, column=0, columnspan=5, pady=5)
        ttk.Button(botones_pedido_frame, text="Generar Orden de Compra", command=self.generar_orden).pack(side="left", padx=10)
        ttk.Button(botones_pedido_frame, text="Limpiar Pedido", command=self.limpiar_pedido).pack(side="left")
        historial_frame = ttk.LabelFrame(self, text="Historial de Órdenes", padding=10)
        historial_frame.pack(fill="both", expand=True, padx=10, pady=10)
        paned_window = ttk.PanedWindow(historial_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)
        ordenes_frame = ttk.Frame(paned_window)
        paned_window.add(ordenes_frame, weight=2)
        self.tree_ordenes = ttk.Treeview(ordenes_frame, columns=("ID", "Fecha", "Proveedor", "Estado", "F. Recep."), show="headings")
        self.tree_ordenes.pack(fill="both", expand=True)
        self.tree_ordenes.heading("ID", text="ID"); self.tree_ordenes.column("ID", width=50, anchor="center")
        self.tree_ordenes.heading("Fecha", text="Fecha Creación"); self.tree_ordenes.column("Fecha", width=150)
        self.tree_ordenes.heading("Proveedor", text="Proveedor"); self.tree_ordenes.column("Proveedor", width=200)
        self.tree_ordenes.heading("Estado", text="Estado"); self.tree_ordenes.column("Estado", width=100, anchor="center")
        self.tree_ordenes.heading("F. Recep.", text="Fecha Recepción"); self.tree_ordenes.column("F. Recep.", width=150)
        self.tree_ordenes.bind("<<TreeviewSelect>>", self.mostrar_detalles_orden)
        detalles_frame = ttk.Frame(paned_window)
        paned_window.add(detalles_frame, weight=1)
        self.tree_detalles = ttk.Treeview(detalles_frame, columns=("Producto", "Cantidad"), show="headings")
        self.tree_detalles.pack(fill="both", expand=True)
        self.tree_detalles.heading("Producto", text="Producto"); self.tree_detalles.column("Producto", width=200)
        self.tree_detalles.heading("Cantidad", text="Cantidad Recibida"); self.tree_detalles.column("Cantidad", width=120, anchor="center")
        ttk.Button(historial_frame, text="Marcar como Recibida", command=self.recibir_orden).pack(pady=10)

    def cargar_datos(self):
        proveedores = self.db.ejecutar_query("SELECT id, nombre FROM proveedores ORDER BY nombre", fetchall=True)
        self.proveedor_map = {f"{id} - {nombre}": id for id, nombre in proveedores}
        self.proveedor_combo['values'] = list(self.proveedor_map.keys())
        productos = self.db.ejecutar_query("SELECT id, nombre, sku FROM productos ORDER BY nombre", fetchall=True)
        self.producto_map = {f"{nombre} (SKU: {sku})": id for id, nombre, sku in productos}
        self.producto_combo['values'] = list(self.producto_map.keys())
        self.cargar_ordenes()

    def agregar_al_pedido(self):
        producto_sel = self.producto_combo.get()
        if not producto_sel: messagebox.showwarning("Sin Selección", "Debe seleccionar un producto."); return
        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0: raise ValueError
        except ValueError: messagebox.showerror("Error de Cantidad", "La cantidad debe ser un número entero positivo."); return
        producto_id = self.producto_map[producto_sel]
        nombre_producto = producto_sel.split(" (SKU:")[0]
        self.tree_pedido.insert("", "end", values=(producto_id, nombre_producto, cantidad))

    def limpiar_pedido(self):
        for item in self.tree_pedido.get_children(): self.tree_pedido.delete(item)
        self.proveedor_combo.set(''); self.producto_combo.set('')
        self.cantidad_entry.delete(0, tk.END); self.cantidad_entry.insert(0, "1")

    def generar_orden(self):
        proveedor_sel = self.proveedor_combo.get()
        if not proveedor_sel: messagebox.showwarning("Sin Proveedor", "Debe seleccionar un proveedor."); return
        items_pedido = self.tree_pedido.get_children()
        if not items_pedido: messagebox.showwarning("Pedido Vacío", "No hay productos en el pedido."); return
        orden_data = {'proveedor_id': self.proveedor_map[proveedor_sel], 'fecha_creacion': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'estado': 'Pendiente'}
        orden_id = self.db.agregar_registro('ordenes_compra', orden_data)
        if orden_id:
            for item in items_pedido:
                values = self.tree_pedido.item(item, 'values')
                detalle_data = {'orden_id': orden_id, 'producto_id': values[0], 'cantidad': values[2]}
                self.db.agregar_registro('detalles_orden_compra', detalle_data)
            messagebox.showinfo("Éxito", f"Orden de compra #{orden_id} generada.");
            self.limpiar_pedido(); self.cargar_ordenes()

    def cargar_ordenes(self):
        for item in self.tree_ordenes.get_children(): self.tree_ordenes.delete(item)
        for orden in self.db.obtener_ordenes_con_proveedor():
            self.tree_ordenes.insert("", "end", values=orden)

    def mostrar_detalles_orden(self, event):
        item_sel = self.tree_ordenes.focus()
        if not item_sel: return
        orden_id = self.tree_ordenes.item(item_sel, 'values')[0]
        for item in self.tree_detalles.get_children(): self.tree_detalles.delete(item)
        for detalle in self.db.obtener_detalles_orden(orden_id):
            self.tree_detalles.insert("", "end", values=detalle)

    def recibir_orden(self):
        item_sel = self.tree_ordenes.focus()
        if not item_sel: messagebox.showwarning("Sin Selección", "Seleccione una orden para recibir."); return
        values = self.tree_ordenes.item(item_sel, 'values')
        orden_id, estado = values[0], values[3]
        if estado == 'Recibida':
            messagebox.showinfo("Información", "Esta orden ya ha sido recibida."); return
        if messagebox.askyesno("Confirmar Recepción", f"¿Confirmar la recepción de la orden #{orden_id}? Esta acción actualizará el stock."):
            if self.db.recibir_orden_compra(orden_id):
                messagebox.showinfo("Éxito", "Stock actualizado correctamente."); self.cargar_ordenes()

