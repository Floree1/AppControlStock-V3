import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from core.utils import generar_ticket_pdf

class FacturacionTab(ttk.Frame):
    def __init__(self, parent, db, app_instance):
        super().__init__(parent)
        self.db = db
        self.app = app_instance
        self.last_sale_info = None
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # --- Frame superior para escaneo y selección ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", padx=10, pady=5)

        scan_frame = ttk.LabelFrame(top_frame, text="Escanear Producto (SKU / Código de Barras)", padding=10)
        scan_frame.pack(fill="x", expand=True, side="left", padx=(0, 10))
        self.sku_entry = ttk.Entry(scan_frame, font=("Helvetica", 14))
        self.sku_entry.pack(fill="x", expand=True)
        self.sku_entry.bind("<Return>", self.agregar_producto_escaneado)

        pago_frame = ttk.LabelFrame(top_frame, text="Método de Pago", padding=(10,5))
        pago_frame.pack(side="left")
        self.metodo_pago_var = tk.StringVar(value="Contado")
        ttk.Radiobutton(pago_frame, text="Contado", variable=self.metodo_pago_var, value="Contado").pack(side="left", padx=5)
        ttk.Radiobutton(pago_frame, text="Crédito", variable=self.metodo_pago_var, value="Credito").pack(side="left", padx=5)
        
        # --- Frame para selección manual (secundario) ---
        manual_select_frame = ttk.LabelFrame(main_frame, text="Selección Manual", padding=10)
        manual_select_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(manual_select_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cliente_combo = ttk.Combobox(manual_select_frame, state="readonly", width=30)
        self.cliente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(manual_select_frame, text="Producto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.producto_combo = ttk.Combobox(manual_select_frame, state="readonly", width=40)
        self.producto_combo.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(manual_select_frame, text="Cantidad:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.cantidad_entry = ttk.Entry(manual_select_frame, width=10)
        self.cantidad_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.cantidad_entry.insert(0, "1")
        
        ttk.Button(manual_select_frame, text="Agregar Manualmente", command=self.agregar_producto_manual).grid(row=1, column=4, padx=10, pady=5)

        # --- Carrito y Totales ---
        carrito_frame = ttk.LabelFrame(main_frame, text="Carrito de Compras", padding=10)
        carrito_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_carrito = ttk.Treeview(carrito_frame, columns=("ID", "Producto", "Cantidad", "Precio Unit.", "Subtotal"), show="headings")
        self.tree_carrito.heading("ID", text="ID"); self.tree_carrito.column("ID", width=50, anchor="center")
        self.tree_carrito.heading("Producto", text="Producto"); self.tree_carrito.column("Producto", width=300)
        self.tree_carrito.heading("Cantidad", text="Cantidad"); self.tree_carrito.column("Cantidad", width=100, anchor="center")
        self.tree_carrito.heading("Precio Unit.", text="Precio Unit."); self.tree_carrito.column("Precio Unit.", width=120, anchor="e")
        self.tree_carrito.heading("Subtotal", text="Subtotal"); self.tree_carrito.column("Subtotal", width=120, anchor="e")
        self.tree_carrito.pack(fill="both", expand=True)
        
        total_frame = ttk.Frame(main_frame, padding=10)
        total_frame.pack(fill="x", padx=10, pady=5)
        self.total_label = ttk.Label(total_frame, text="TOTAL: $0.00", style="Total.TLabel")
        self.total_label.pack(side="left", padx=10)
        ttk.Button(total_frame, text="Eliminar Seleccionado", command=self.eliminar_del_carrito).pack(side="left", padx=10)
        
        action_buttons_frame = ttk.Frame(total_frame)
        action_buttons_frame.pack(side="right")
        self.pdf_button = ttk.Button(action_buttons_frame, text="Generar Ticket (PDF)", command=self.generar_pdf, state="disabled")
        self.pdf_button.pack(side="right", padx=10)
        ttk.Button(action_buttons_frame, text="Generar Factura", command=self.generar_factura).pack(side="right")
        ttk.Button(action_buttons_frame, text="Vaciar Carrito", command=self.limpiar_carrito).pack(side="right", padx=10)

    def cargar_comboboxes(self):
        clientes = self.db.ejecutar_query("SELECT id, nombre FROM clientes ORDER BY nombre", fetchall=True)
        self.cliente_map = {f"{id} - {nombre}": id for id, nombre in clientes}
        self.cliente_combo['values'] = list(self.cliente_map.keys())
        productos = self.db.ejecutar_query("SELECT id, nombre, sku FROM productos WHERE cantidad > 0 ORDER BY nombre", fetchall=True)
        self.producto_map = {f"{nombre} (SKU: {sku})": id for id, nombre, sku in productos}
        self.producto_combo['values'] = list(self.producto_map.keys())

    def _agregar_item_al_carrito(self, producto_id, cantidad_a_agregar):
        self.pdf_button.config(state="disabled")
        
        # Verificar si el producto ya está en el carrito
        item_existente = None
        for item in self.tree_carrito.get_children():
            if int(self.tree_carrito.item(item, 'values')[0]) == producto_id:
                item_existente = item
                break
        
        producto_db = self.db.ejecutar_query("SELECT nombre, cantidad, precio FROM productos WHERE id = ?", (producto_id,), fetchone=True)
        if not producto_db: return # No debería pasar si se llama desde SKU o combo

        if item_existente:
            valores_actuales = self.tree_carrito.item(item_existente, 'values')
            cantidad_actual = int(valores_actuales[2])
            nueva_cantidad = cantidad_actual + cantidad_a_agregar
            
            if nueva_cantidad > producto_db[1]:
                messagebox.showwarning("Stock Insuficiente", f"No hay suficiente stock. Disponible: {producto_db[1]}, en carrito: {cantidad_actual}")
                return
            
            nuevo_subtotal = nueva_cantidad * producto_db[2]
            nuevos_valores = (producto_id, producto_db[0], nueva_cantidad, f"{producto_db[2]:.2f}", f"{nuevo_subtotal:.2f}")
            self.tree_carrito.item(item_existente, values=nuevos_valores)
        else:
            if cantidad_a_agregar > producto_db[1]:
                messagebox.showwarning("Stock Insuficiente", f"No hay suficiente stock. Disponible: {producto_db[1]}")
                return
            
            subtotal = cantidad_a_agregar * producto_db[2]
            valores = (producto_id, producto_db[0], cantidad_a_agregar, f"{producto_db[2]:.2f}", f"{subtotal:.2f}")
            self.tree_carrito.insert("", "end", values=valores)
        
        self.actualizar_total_carrito()

    def agregar_producto_escaneado(self, event=None):
        sku = self.sku_entry.get().strip()
        if not sku: return
        
        producto = self.db.obtener_producto_por_sku(sku)
        
        if producto:
            producto_id = producto[0]
            self._agregar_item_al_carrito(producto_id, 1) # Escanear siempre agrega 1 unidad
        else:
            messagebox.showwarning("Producto no Encontrado", f"No se encontró ningún producto con el SKU: {sku}")
        
        self.sku_entry.delete(0, tk.END)

    def agregar_producto_manual(self):
        producto_sel = self.producto_combo.get()
        if not producto_sel:
            messagebox.showwarning("Sin Selección", "Debe seleccionar un producto del menú.")
            return
        
        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error de Cantidad", "La cantidad debe ser un número entero positivo.")
            return
        
        producto_id = self.producto_map[producto_sel]
        self._agregar_item_al_carrito(producto_id, cantidad)

    def eliminar_del_carrito(self):
        selected_item = self.tree_carrito.focus()
        if not selected_item: messagebox.showwarning("Sin Selección", "Seleccione un producto del carrito para eliminar."); return
        self.tree_carrito.delete(selected_item)
        self.actualizar_total_carrito()
        self.pdf_button.config(state="disabled")

    def actualizar_total_carrito(self):
        total = sum(float(self.tree_carrito.item(item, 'values')[4]) for item in self.tree_carrito.get_children())
        self.total_label.config(text=f"TOTAL: ${total:.2f}")

    def limpiar_carrito(self):
        for item in self.tree_carrito.get_children(): self.tree_carrito.delete(item)
        self.actualizar_total_carrito()
        self.cliente_combo.set(''); self.producto_combo.set('')
        self.cantidad_entry.delete(0, tk.END); self.cantidad_entry.insert(0, "1")
        self.pdf_button.config(state="disabled")
        self.last_sale_info = None
        self.sku_entry.focus_set()

    def generar_factura(self):
        cliente_sel = self.cliente_combo.get()
        if not cliente_sel: messagebox.showwarning("Sin Cliente", "Debe seleccionar un cliente."); return
        items_carrito = self.tree_carrito.get_children()
        if not items_carrito: messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito."); return
        
        metodo_pago = self.metodo_pago_var.get()
        confirm_msg = f"¿Generar la factura como '{metodo_pago}'? Esta acción descontará el stock."
        if not messagebox.askyesno("Confirmar Venta", confirm_msg): return
        
        venta_data = {
            'cliente_id': self.cliente_map[cliente_sel], 
            'usuario_id': self.app.user_id,
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            'total': float(self.total_label.cget("text").replace("TOTAL: $", "")),
            'metodo_pago': metodo_pago,
            'descuento_total': 0 # Placeholder for future discount logic
        }
        
        detalles_data = []
        for item in items_carrito:
            values = self.tree_carrito.item(item, 'values')
            producto_id = int(values[0])
            costo_actual = self.db.ejecutar_query("SELECT costo FROM productos WHERE id = ?", (producto_id,), fetchone=True)[0]
            detalles_data.append({
                'producto_id': producto_id, 
                'cantidad': int(values[2]), 
                'precio_unitario': float(values[3]), 
                'subtotal': float(values[4]),
                'costo_unitario': costo_actual,
                'descuento_aplicado': 0 # Placeholder
            })

        venta_id = self.db.generar_factura_transaccion(venta_data, detalles_data)
        if venta_id:
            messagebox.showinfo("Éxito", f"Venta #{venta_id} generada correctamente.")
            
            self.last_sale_info = {
                "venta_id": venta_id,
                "cliente": cliente_sel.split(" - ")[1],
                "vendedor": self.app.username,
                "fecha": venta_data['fecha'],
                "total": venta_data['total'],
                "metodo_pago": metodo_pago,
                "detalles": [(self.tree_carrito.item(item, 'values')[1], 
                              self.tree_carrito.item(item, 'values')[2],
                              self.tree_carrito.item(item, 'values')[3],
                              self.tree_carrito.item(item, 'values')[4]) for item in items_carrito]
            }
            
            self.limpiar_carrito()
            self.cargar_comboboxes()
            self.pdf_button.config(state="normal")

    def generar_pdf(self):
        if not self.last_sale_info:
            messagebox.showwarning('Sin Venta', 'Primero debe generar una factura para poder crear el ticket.')
            return
        filepath = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('Archivos PDF', '*.pdf'), ('Todos', '*.*')], initialfile=f"ticket-venta-{self.last_sale_info['venta_id']}.pdf")
        if filepath:
            if generar_ticket_pdf(self.last_sale_info, filepath):
                messagebox.showinfo('Éxito', f'Ticket PDF generado en:\n{filepath}')
