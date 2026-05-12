import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class DashboardTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.crear_widgets()

    def crear_widgets(self):
        filtros_frame = ttk.LabelFrame(self, text="Filtros del Dashboard", padding=10)
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
        
        self.crear_dashboard_metrics(self)
        
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(self.chart_frame, text="Matplotlib no está instalado. No se pueden mostrar gráficos.\nInstálalo con: pip install matplotlib", foreground="red").pack()

    def cargar_filtros(self):
        categorias = self.db.obtener_categorias()
        self.category_map = {nombre: id for id, nombre in categorias}
        self.category_filter_combo['values'] = ["Todas"] + list(self.category_map.keys())
        self.category_filter_combo.set("Todas")
        self.aplicar_filtros()

    def crear_dashboard_metrics(self, parent_frame):
        dashboard_frame = ttk.Frame(parent_frame)
        dashboard_frame.pack(fill="x", padx=10, pady=10)
        
        def crear_metrica(parent, texto, variable):
            frame = ttk.Frame(parent, borderwidth=2, relief="groove")
            frame.pack(side="left", fill="x", expand=True, padx=5)
            ttk.Label(frame, text=texto, style="Metric.TLabel").pack(pady=(5,0))
            label = ttk.Label(frame, textvariable=variable, style="MetricValue.TLabel")
            label.pack(pady=(0,5))
            return label

        self.ingresos_var = tk.StringVar(value="$0.00")
        self.cmv_var = tk.StringVar(value="$0.00")
        self.ganancia_var = tk.StringVar(value="$0.00")
        self.prod_var = tk.StringVar(value="N/A")
        self.cliente_var = tk.StringVar(value="N/A")
        self.categoria_var = tk.StringVar(value="N/A")
        self.vendedor_var = tk.StringVar(value="N/A")
        self.descuentos_var = tk.StringVar(value="$0.00")

        crear_metrica(dashboard_frame, "Ingresos Totales", self.ingresos_var)
        crear_metrica(dashboard_frame, "Costo Mercadería", self.cmv_var)
        crear_metrica(dashboard_frame, "Ganancia Bruta", self.ganancia_var)
        crear_metrica(dashboard_frame, "Total Descontado", self.descuentos_var)
        crear_metrica(dashboard_frame, "Producto Más Vendido", self.prod_var)
        crear_metrica(dashboard_frame, "Mejor Cliente", self.cliente_var)
        crear_metrica(dashboard_frame, "Categoría Más Vendida", self.categoria_var)
        crear_metrica(dashboard_frame, "Mejor Vendedor", self.vendedor_var)

    def aplicar_filtros(self):
        fecha_inicio, fecha_fin = self.fecha_inicio_entry.get() + " 00:00:00", self.fecha_fin_entry.get() + " 23:59:59"
        try:
            datetime.datetime.strptime(self.fecha_inicio_entry.get(), "%Y-%m-%d")
            datetime.datetime.strptime(self.fecha_fin_entry.get(), "%Y-%m-%d")
        except ValueError: messagebox.showerror("Error de Formato", "Use el formato YYYY-MM-DD para las fechas."); return
        
        categoria_nombre = self.category_filter_combo.get()
        categoria_id = self.category_map.get(categoria_nombre) if categoria_nombre != "Todas" else None

        metricas = self.db.obtener_metricas_dashboard(fecha_inicio, fecha_fin, categoria_id)
        self.ingresos_var.set(f"${metricas['ingresos_totales']:.2f}")
        self.cmv_var.set(f"${metricas['cmv']:.2f}")
        self.ganancia_var.set(f"${metricas['ganancia_bruta']:.2f}")
        self.prod_var.set(metricas['producto_mas_vendido'])
        self.cliente_var.set(metricas['mejor_cliente'])
        self.categoria_var.set(metricas['categoria_mas_vendida'])
        self.vendedor_var.set(metricas['mejor_vendedor'])
        self.descuentos_var.set(f"${metricas['total_descuentos']:.2f}")
        
        if MATPLOTLIB_AVAILABLE:
            self.actualizar_grafico(fecha_inicio, fecha_fin, categoria_id)

    def actualizar_grafico(self, fecha_inicio, fecha_fin, categoria_id=None):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        datos_ventas = self.db.obtener_datos_grafico_ventas(fecha_inicio, fecha_fin, categoria_id)
        
        if not datos_ventas:
            ttk.Label(self.chart_frame, text="No hay datos de ventas en el período seleccionado.").pack()
            return

        fechas = [datetime.datetime.strptime(d[0], "%Y-%m-%d").strftime("%d/%m") for d in datos_ventas]
        totales = [d[1] for d in datos_ventas]

        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.bar(fechas, totales, color='skyblue')
        ax.set_title('Ingresos por Día')
        ax.set_ylabel('Total Vendido ($)')
        ax.set_xlabel('Fecha')
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

