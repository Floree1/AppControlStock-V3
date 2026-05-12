import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from PIL import Image, ImageTk
import os
from ui.tabs.stock_tab import StockTab
from ui.tabs.clientes_tab import ClientesTab
from ui.tabs.facturacion_tab import FacturacionTab
from ui.tabs.proveedores_tab import ProveedoresTab
from ui.tabs.ordenes_compra_tab import OrdenesCompraTab
from ui.tabs.alertas_tab import AlertasTab
from ui.tabs.reportes_tab import ReportesTab
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.admin_tab import AdminTab
from ui.tabs.categorias_tab import CategoriasTab

class AppGestion:
    def __init__(self, root, db, user_data, config_manager):
        self.root, self.db, self.config_manager = root, db, config_manager
        self.user_id, self.username, self.user_role = user_data
        
        self.root.title(f"Sistema de Gestión Integrado v3.0 - Usuario: {self.username} ({self.user_role})")
        self.root.geometry("1300x850")
        self.configurar_estilos()
        self.crear_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.check_low_stock_alerts()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Helvetica", 11)); style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)
        style.configure("TEntry", padding=5); style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        style.configure("Treeview", rowheight=25, font=("Helvetica", 10)); style.configure("Footer.TLabel", font=("Helvetica", 9), foreground="gray")
        style.configure("Total.TLabel", font=("Helvetica", 14, "bold")); style.configure("Metric.TLabel", font=("Helvetica", 10))
        style.configure("MetricValue.TLabel", font=("Helvetica", 16, "bold")); style.configure("LowStock.Treeview", background="#ffdddd")
        style.configure("Alert.TNotebook.Tab", foreground="red", font=("Helvetica", 10, "bold"))
        style.configure("Debt.Treeview", background="#ffe4e1") # Estilo para clientes con deuda

    def crear_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill="both")

        # --- Cabecera con Logo ---
        header_frame = ttk.Frame(main_frame, style="Header.TFrame", height=60)
        header_frame.pack(fill="x", padx=10, pady=5)
        self.logo_label = ttk.Label(header_frame)
        self.logo_label.pack(side="left", padx=10, pady=5)
        self.load_and_display_logo()

        self.notebook = ttk.Notebook(main_frame, padding=(10, 10))
        self.notebook.pack(expand=True, fill="both")

        self.facturacion_tab = FacturacionTab(self.notebook, self.db, self)
        self.notebook.add(self.facturacion_tab, text="Facturación / POS")
        
        self.stock_tab = StockTab(self.notebook, self.db)
        self.notebook.add(self.stock_tab, text="Gestión de Stock")

        self.clientes_tab = ClientesTab(self.notebook, self.db)
        self.notebook.add(self.clientes_tab, text="Gestión de Clientes")

        if self.user_role == 'Administrador':
            self.dashboard_tab = DashboardTab(self.notebook, self.db)
            self.notebook.add(self.dashboard_tab, text="Dashboard")
            
            self.categorias_tab = CategoriasTab(self.notebook, self.db)
            self.notebook.add(self.categorias_tab, text="Categorías")

            self.proveedores_tab = ProveedoresTab(self.notebook, self.db)
            self.notebook.add(self.proveedores_tab, text="Proveedores")
            
            self.ordenes_compra_tab = OrdenesCompraTab(self.notebook, self.db)
            self.notebook.add(self.ordenes_compra_tab, text="Órdenes de Compra")
            
            self.alertas_tab = AlertasTab(self.notebook, self.db)
            self.notebook.add(self.alertas_tab, text="Alertas de Inventario")

            self.reportes_tab = ReportesTab(self.notebook, self.db)
            self.notebook.add(self.reportes_tab, text="Reportes")
            
            self.admin_tab = AdminTab(self.notebook, self.db, self.root, self)
            self.notebook.add(self.admin_tab, text="Administración")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        footer_frame = ttk.Frame(self.root, style="TFrame")
        footer_frame.pack(side="bottom", fill="x", pady=(0, 5))
        current_year = datetime.date.today().year
        copyright_text = f"Sistema v3.0 | © {current_year} MauroDEV. Todos los derechos reservados."
        footer_label = ttk.Label(footer_frame, text=copyright_text, style="Footer.TLabel", anchor="center")
        footer_label.pack(fill="x")
        self.cargar_datos_iniciales()

    def load_and_display_logo(self):
        logo_path = self.config_manager.get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((180, 50))
                self.logo_photo = ImageTk.PhotoImage(img)
                self.logo_label.config(image=self.logo_photo)
            except Exception as e:
                self.logo_label.config(image=None)
                print(f"Error al cargar el logo principal: {e}")
        else:
            self.logo_label.config(image=None)


    def on_tab_changed(self, event):
        selected_tab_index = event.widget.index(event.widget.select())
        tab_text = self.notebook.tab(selected_tab_index, "text").split(" (")[0]

        if tab_text == "Facturación / POS": 
            self.facturacion_tab.cargar_comboboxes()
            self.facturacion_tab.sku_entry.focus_set()
        elif tab_text == "Gestión de Stock": self.stock_tab.cargar_datos()
        elif tab_text == "Gestión de Clientes": self.clientes_tab.cargar_clientes()
        
        if self.user_role == 'Administrador':
            if tab_text == "Dashboard": self.dashboard_tab.cargar_filtros()
            elif tab_text == "Reportes": self.reportes_tab.cargar_filtros()
            elif tab_text == "Alertas de Inventario": self.alertas_tab.cargar_alertas()
            elif tab_text == "Órdenes de Compra": self.ordenes_compra_tab.cargar_datos()
            elif tab_text == "Administración": self.admin_tab.cargar_usuarios()
            elif tab_text == "Categorías": self.categorias_tab.cargar_categorias()
            self.check_low_stock_alerts()

    def cargar_datos_iniciales(self):
        self.stock_tab.cargar_datos()
        self.clientes_tab.cargar_clientes()
        self.facturacion_tab.cargar_comboboxes()
        if self.user_role == 'Administrador':
            self.proveedores_tab.cargar_proveedores()
            self.reportes_tab.cargar_filtros()
            self.alertas_tab.cargar_alertas()
            self.ordenes_compra_tab.cargar_datos()
            self.admin_tab.cargar_usuarios()
            self.dashboard_tab.cargar_filtros()
            self.categorias_tab.cargar_categorias()

    def check_low_stock_alerts(self):
        if self.user_role == 'Administrador':
            alert_products = self.db.obtener_productos_bajo_stock()
            alert_count = len(alert_products)
            
            alert_tab_index = None
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text").startswith("Alertas"):
                    alert_tab_index = i
                    break
            
            if alert_tab_index is None: return

            if alert_count > 0:
                self.notebook.tab(alert_tab_index, text=f"Alertas ({alert_count})")
            else:
                self.notebook.tab(alert_tab_index, text="Alertas de Inventario")
        
    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.db.close()
            self.root.destroy()

