import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
from ui.tabs.ventana_impresion_etiquetas import LabelPrintWindow

try:
    import barcode
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

class StockTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", padx=10, pady=5)

        search_frame = ttk.LabelFrame(top_frame, text="Buscar y Filtrar", padding=(10,5))
        search_frame.pack(fill="x", expand=True, side="left")
        
        ttk.Label(search_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.cargar_productos())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(search_frame, text="Categoría:").grid(row=0, column=2, padx=5, pady=2)
        self.category_filter_combo = ttk.Combobox(search_frame, state="readonly", width=25)
        self.category_filter_combo.grid(row=0, column=3, padx=5, pady=2)
        self.category_filter_combo.bind("<<ComboboxSelected>>", self.cargar_productos)
        
        actions_frame = ttk.Frame(top_frame)
        actions_frame.pack(side="left", padx=20, fill="y")
        self.print_labels_button = ttk.Button(actions_frame, text="Imprimir Etiquetas", command=self.abrir_ventana_impresion, state="disabled")
        self.print_labels_button.pack(pady=5)

        input_frame = ttk.LabelFrame(main_frame, text="Datos del Producto", padding=(10, 10))
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_entry = ttk.Entry(input_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3)
        
        ttk.Label(input_frame, text="SKU / Código de Barras:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sku_entry = ttk.Entry(input_frame, width=20)
        self.sku_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Categoría:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.category_combo = ttk.Combobox(input_frame, state="readonly", width=20)
        self.category_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Costo ($):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.costo_entry = ttk.Entry(input_frame, width=15)
        self.costo_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Precio Venta ($):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.precio_entry = ttk.Entry(input_frame, width=15)
        self.precio_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Cantidad Actual:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.cantidad_entry = ttk.Entry(input_frame, width=15)
        self.cantidad_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(input_frame, text="Stock Mínimo:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.stock_minimo_entry = ttk.Entry(input_frame, width=15)
        self.stock_minimo_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        button_frame = ttk.Frame(main_frame, padding=(10, 5))
        button_frame.pack(fill="x", padx=10)
        ttk.Button(button_frame, text="Agregar", command=self.agregar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)
        
        # --- Frame de Operaciones Masivas ---
        massive_ops_frame = ttk.LabelFrame(main_frame, text="Operaciones Masivas", padding=(10, 10))
        massive_ops_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(massive_ops_frame, text="Exportar Plantilla (CSV)", command=self.exportar_plantilla_csv).pack(side="left", padx=5)
        ttk.Button(massive_ops_frame, text="Importar y Actualizar desde CSV", command=self.importar_productos_csv).pack(side="left", padx=5)

        tree_frame = ttk.Frame(main_frame, padding=(10, 10))
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "SKU", "Categoría", "Precio", "Cantidad", "Stock Mínimo"), show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40, anchor="center")
        self.tree.heading("Nombre", text="Nombre"); self.tree.column("Nombre", width=280)
        self.tree.heading("SKU", text="SKU / Cód. Barras"); self.tree.column("SKU", width=120, anchor="center")
        self.tree.heading("Categoría", text="Categoría"); self.tree.column("Categoría", width=150)
        self.tree.heading("Precio", text="Precio ($)"); self.tree.column("Precio", width=80, anchor="e")
        self.tree.heading("Cantidad", text="Cant."); self.tree.column("Cantidad", width=60, anchor="center")
        self.tree.heading("Stock Mínimo", text="S. Mín."); self.tree.column("Stock Mínimo", width=80, anchor="center")
        
        self.tree.tag_configure('lowstock', background='#ffdddd')
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
    def cargar_datos(self):
        self.cargar_categorias()
        self.cargar_productos()

    def cargar_categorias(self):
        categorias = self.db.obtener_categorias()
        self.category_map = {nombre: id for id, nombre in categorias}
        
        # Filtro
        self.category_filter_combo['values'] = ["Todas"] + list(self.category_map.keys())
        self.category_filter_combo.set("Todas")
        
        # Formulario
        self.category_combo['values'] = list(self.category_map.keys())

    def on_item_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            self.print_labels_button.config(state="normal")
            if len(selected_items) == 1:
                item = self.tree.item(selected_items[0], 'values')
                self.limpiar_campos(clear_selection=False)
                self.nombre_entry.insert(0, item[1])
                self.sku_entry.insert(0, item[2])
                self.category_combo.set(item[3])
                self.precio_entry.insert(0, item[4])
                self.cantidad_entry.insert(0, item[5])
                self.stock_minimo_entry.insert(0, item[6])
                # Cargar el costo (que no está en la vista del árbol)
                costo = self.db.ejecutar_query("SELECT costo FROM productos WHERE id = ?", (item[0],), fetchone=True)
                if costo: self.costo_entry.insert(0, f"{costo[0]:.2f}")
        else:
            self.print_labels_button.config(state="disabled")

    def cargar_productos(self, event=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        search_term = self.search_var.get()
        categoria_nombre = self.category_filter_combo.get()
        categoria_id = self.category_map.get(categoria_nombre) if categoria_nombre != "Todas" else None

        for prod in self.db.obtener_productos_con_categoria(search_term, categoria_id):
            tags = ('lowstock',) if prod[5] <= prod[6] and prod[6] > 0 else ()
            valores = (prod[0], prod[1], prod[2], prod[7], f"{prod[4]:.2f}", prod[5], prod[6])
            self.tree.insert("", "end", values=valores, tags=tags)
        self.print_labels_button.config(state="disabled")

    def agregar_producto(self):
        campos = [self.nombre_entry, self.sku_entry, self.cantidad_entry, self.precio_entry, self.stock_minimo_entry, self.costo_entry]
        if not all(e.get() for e in campos): messagebox.showwarning("Campos Vacíos", "Todos los campos son obligatorios."); return
        
        categoria_nombre = self.category_combo.get()
        if not categoria_nombre:
            messagebox.showwarning("Campo Obligatorio", "Debe seleccionar una categoría.")
            return
        categoria_id = self.category_map[categoria_nombre]

        try:
            data = {
                'nombre': self.nombre_entry.get(), 
                'sku': self.sku_entry.get(), 
                'cantidad': int(self.cantidad_entry.get()), 
                'precio': float(self.precio_entry.get()), 
                'stock_minimo': int(self.stock_minimo_entry.get()), 
                'costo': float(self.costo_entry.get()),
                'categoria_id': categoria_id
            }
        except ValueError: messagebox.showerror("Error de Formato", "Costo, Precio, Cantidad y Stock Mínimo deben ser números."); return
        if self.db.agregar_registro('productos', data): messagebox.showinfo("Éxito", "Producto agregado."); self.limpiar_campos(); self.cargar_productos()

    def actualizar_producto(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        
        categoria_nombre = self.category_combo.get()
        if not categoria_nombre:
            messagebox.showwarning("Campo Obligatorio", "Debe seleccionar una categoría.")
            return
        categoria_id = self.category_map[categoria_nombre]

        try:
            data = {
                'nombre': self.nombre_entry.get(), 
                'sku': self.sku_entry.get(), 
                'cantidad': int(self.cantidad_entry.get()), 
                'precio': float(self.precio_entry.get()), 
                'stock_minimo': int(self.stock_minimo_entry.get()), 
                'costo': float(self.costo_entry.get()),
                'categoria_id': categoria_id
            }
        except ValueError: messagebox.showerror("Error de Formato", "Costo, Precio, Cantidad y Stock Mínimo deben ser números."); return
        if self.db.actualizar_registro('productos', data, item_id): messagebox.showinfo("Éxito", "Producto actualizado."); self.limpiar_campos(); self.cargar_productos()

    def eliminar_producto(self):
        item_id = self.obtener_id_seleccionado()
        if not item_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            if self.db.eliminar_registro('productos', item_id): messagebox.showinfo("Éxito", "Producto eliminado."); self.limpiar_campos(); self.cargar_productos()

    def limpiar_campos(self, clear_selection=True):
        for entry in [self.nombre_entry, self.sku_entry, self.cantidad_entry, self.precio_entry, self.stock_minimo_entry, self.costo_entry]:
            entry.delete(0, tk.END)
        self.category_combo.set('')
        self.nombre_entry.focus()
        if clear_selection and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        
    def obtener_id_seleccionado(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione un producto de la lista.")
            return None
        if len(selected_items) > 1:
            messagebox.showwarning("Múltiples Selecciones", "Por favor, seleccione solo un producto para esta acción.")
            return None
        return self.tree.item(selected_items[0], 'values')[0]

    def abrir_ventana_impresion(self):
        if not BARCODE_AVAILABLE:
            messagebox.showerror("Librerías Faltantes", "Se necesitan las librerías 'python-barcode' y 'Pillow' para esta función.\nInstálalas con: pip install python-barcode Pillow")
            return
        
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione al menos un producto para imprimir etiquetas.")
            return
        
        productos_a_imprimir = [self.tree.item(item, 'values') for item in selected_items]
        LabelPrintWindow(self, productos_a_imprimir)

    def exportar_plantilla_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            initialfile="plantilla_productos.csv"
        )
        if not filepath: return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(['sku', 'nombre', 'cantidad', 'precio', 'costo', 'stock_minimo', 'categoria'])
            messagebox.showinfo("Éxito", f"Plantilla guardada en:\n{filepath}")
        except IOError as e:
            messagebox.showerror("Error de Exportación", f"No se pudo guardar el archivo: {e}")

    def importar_productos_csv(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if not filepath: return

        if not messagebox.askyesno("Confirmar Importación", 
            "¿Está seguro de que desea importar productos desde este archivo?\n"
            "Los productos con SKU existentes se actualizarán. Los nuevos se crearán."):
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                creados = 0
                actualizados = 0
                errores = 0

                for row in reader:
                    try:
                        sku = row['sku'].strip()
                        if not sku:
                            errores += 1
                            continue
                        
                        categoria_id = self.db.obtener_o_crear_categoria_id(row.get('categoria', '').strip())
                        
                        data = {
                            'nombre': row['nombre'].strip(),
                            'cantidad': int(row['cantidad']),
                            'precio': float(row['precio']),
                            'costo': float(row.get('costo', 0.0)),
                            'stock_minimo': int(row.get('stock_minimo', 0)),
                            'categoria_id': categoria_id
                        }
                        
                        producto_existente = self.db.obtener_producto_id_por_sku(sku)
                        if producto_existente:
                            self.db.actualizar_registro('productos', data, producto_existente[0])
                            actualizados += 1
                        else:
                            data['sku'] = sku
                            self.db.agregar_registro('productos', data)
                            creados += 1
                    except (ValueError, KeyError) as e:
                        errores += 1
                        print(f"Error en fila: {row}. Error: {e}")
                
                summary = f"Proceso de importación completado.\n\n" \
                          f"Productos Nuevos Creados: {creados}\n" \
                          f"Productos Actualizados: {actualizados}\n" \
                          f"Filas con Errores: {errores}"
                messagebox.showinfo("Importación Finalizada", summary)
                self.cargar_datos()

        except Exception as e:
            messagebox.showerror("Error de Importación", f"Ocurrió un error al leer el archivo: {e}")

