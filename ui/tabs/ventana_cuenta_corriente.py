import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

class CuentaClienteWindow(tk.Toplevel):
    def __init__(self, parent, db, cliente_id):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.cliente_id = cliente_id
        
        self.title("Gestión de Cuenta Corriente")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Info del cliente y saldo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Cliente", padding=10)
        info_frame.pack(fill="x", pady=5)
        self.nombre_label = ttk.Label(info_frame, text="Cliente: ", font=("Helvetica", 12, "bold"))
        self.nombre_label.pack(side="left", padx=10)
        self.saldo_label = ttk.Label(info_frame, text="Saldo Deudor: $0.00", font=("Helvetica", 12, "bold"), foreground="red")
        self.saldo_label.pack(side="right", padx=10)

        # Paned window para historiales
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True, pady=10)

        # Historial de Ventas
        ventas_frame = ttk.LabelFrame(paned_window, text="Historial de Compras", padding=10)
        self.tree_ventas = ttk.Treeview(ventas_frame, columns=("ID", "Fecha", "Total", "Método"), show="headings")
        self.tree_ventas.heading("ID", text="ID Venta"); self.tree_ventas.column("ID", width=80)
        self.tree_ventas.heading("Fecha", text="Fecha"); self.tree_ventas.column("Fecha", width=150)
        self.tree_ventas.heading("Total", text="Total ($)"); self.tree_ventas.column("Total", width=100, anchor="e")
        self.tree_ventas.heading("Método", text="Método de Pago"); self.tree_ventas.column("Método", width=120)
        self.tree_ventas.pack(fill="both", expand=True)
        paned_window.add(ventas_frame, weight=1)

        # Historial de Pagos
        pagos_frame = ttk.LabelFrame(paned_window, text="Historial de Pagos", padding=10)
        self.tree_pagos = ttk.Treeview(pagos_frame, columns=("ID", "Fecha", "Monto"), show="headings")
        self.tree_pagos.heading("ID", text="ID Pago"); self.tree_pagos.column("ID", width=80)
        self.tree_pagos.heading("Fecha", text="Fecha"); self.tree_pagos.column("Fecha", width=150)
        self.tree_pagos.heading("Monto", text="Monto Pagado ($)"); self.tree_pagos.column("Monto", width=120, anchor="e")
        self.tree_pagos.pack(fill="both", expand=True)
        paned_window.add(pagos_frame, weight=1)

        # Registrar Pago
        registrar_pago_frame = ttk.LabelFrame(main_frame, text="Registrar Nuevo Pago", padding=10)
        registrar_pago_frame.pack(fill="x", pady=5)
        ttk.Label(registrar_pago_frame, text="Monto a Pagar: $").pack(side="left", padx=5)
        self.monto_pago_entry = ttk.Entry(registrar_pago_frame, width=15)
        self.monto_pago_entry.pack(side="left", padx=5)
        ttk.Button(registrar_pago_frame, text="Registrar Pago", command=self.registrar_pago).pack(side="left", padx=10)

    def cargar_datos(self):
        cliente = self.db.obtener_cliente_por_id(self.cliente_id)
        if not cliente:
            messagebox.showerror("Error", "No se pudo encontrar al cliente.")
            self.destroy()
            return

        self.nombre_label.config(text=f"Cliente: {cliente[1]}")
        self.saldo_label.config(text=f"Saldo Deudor: ${cliente[5]:.2f}")
        
        # Cargar historial de ventas
        for item in self.tree_ventas.get_children(): self.tree_ventas.delete(item)
        for venta in self.db.obtener_historial_ventas_cliente(self.cliente_id):
            valores = (venta[0], venta[1], f"{venta[2]:.2f}", venta[3])
            self.tree_ventas.insert("", "end", values=valores)

        # Cargar historial de pagos
        for item in self.tree_pagos.get_children(): self.tree_pagos.delete(item)
        for pago in self.db.obtener_historial_pagos_cliente(self.cliente_id):
            valores = (pago[0], pago[1], f"{pago[2]:.2f}")
            self.tree_pagos.insert("", "end", values=valores)

    def registrar_pago(self):
        try:
            monto = float(self.monto_pago_entry.get())
            if monto <= 0:
                messagebox.showwarning("Monto Inválido", "El monto a pagar debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error de Formato", "Por favor, ingrese un monto numérico válido.")
            return

        cliente = self.db.obtener_cliente_por_id(self.cliente_id)
        if monto > cliente[5]:
            messagebox.showwarning("Monto Excesivo", "El monto a pagar no puede ser mayor que la deuda actual.")
            return

        if self.db.registrar_pago(self.cliente_id, monto):
            messagebox.showinfo("Éxito", "Pago registrado correctamente.")
            self.monto_pago_entry.delete(0, tk.END)
            self.cargar_datos()
            # Actualizar la lista de clientes en la pestaña principal
            self.parent.cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo registrar el pago.")

