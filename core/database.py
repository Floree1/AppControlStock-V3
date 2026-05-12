import sqlite3
import datetime
import hashlib
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, List, Dict, Tuple, Any

class Database:
    """Maneja las operaciones de base de datos SQLite para la aplicación."""

    def __init__(self, db_name: str = 'AppControlStock.db'):
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.crear_tablas()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a la base de datos: {e}")
            raise e

    def crear_tablas(self) -> None:
        """Crea todas las tablas necesarias si no existen."""
        # --- Tabla Promociones ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS promociones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL, -- 'porcentaje', 'fijo'
                valor REAL NOT NULL,
                aplicable_a TEXT NOT NULL, -- 'producto', 'categoria', 'total_venta'
                id_aplicable INTEGER 
            )
        ''')

        # --- Tabla Categorías ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')

        # --- Tabla Usuarios ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'Vendedor'
            )
        ''')
        self._verificar_y_agregar_columna('usuarios', 'rol', "TEXT NOT NULL DEFAULT 'Vendedor'")

        # --- Tabla Productos con categoría ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                stock_minimo INTEGER NOT NULL DEFAULT 0,
                costo REAL NOT NULL DEFAULT 0,
                categoria_id INTEGER,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
            )
        ''')
        self._verificar_y_agregar_columna('productos', 'stock_minimo', 'INTEGER NOT NULL DEFAULT 0')
        self._verificar_y_agregar_columna('productos', 'costo', 'REAL NOT NULL DEFAULT 0')
        self._verificar_y_agregar_columna('productos', 'categoria_id', 'INTEGER', foreign_key='REFERENCES categorias(id) ON DELETE SET NULL')

        # --- Tabla Clientes con Saldo Deudor ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                saldo_deudor REAL NOT NULL DEFAULT 0
            )
        ''')
        self._verificar_y_agregar_columna('clientes', 'saldo_deudor', 'REAL NOT NULL DEFAULT 0')

        # --- Tabla Ventas con Método de Pago y Usuario ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                metodo_pago TEXT NOT NULL DEFAULT 'Contado',
                descuento_total REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            )
        ''')
        self._verificar_y_agregar_columna('ventas', 'metodo_pago', "TEXT NOT NULL DEFAULT 'Contado'")
        self._verificar_y_agregar_columna('ventas', 'usuario_id', 'INTEGER', foreign_key='REFERENCES usuarios(id) ON DELETE SET NULL')
        self._verificar_y_agregar_columna('ventas', 'descuento_total', 'REAL NOT NULL DEFAULT 0')


        # --- Tabla Detalles de Venta ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                costo_unitario REAL NOT NULL DEFAULT 0,
                descuento_aplicado REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
            )
        ''')
        self._verificar_y_agregar_columna('detalles_venta', 'costo_unitario', 'REAL NOT NULL DEFAULT 0')
        self._verificar_y_agregar_columna('detalles_venta', 'descuento_aplicado', 'REAL NOT NULL DEFAULT 0')

        # --- Tabla Pagos de Clientes ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos_clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                monto REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            )
        ''')

        # --- Tablas de Proveedores y Órdenes de Compra ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT,
                email TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes_compra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_recepcion TEXT,
                estado TEXT NOT NULL,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_orden_compra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (orden_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
            )
        ''')
        
        self.conn.commit()
        self._asegurar_admin()

    def _verificar_y_agregar_columna(self, tabla: str, columna: str, tipo: str, foreign_key: Optional[str] = None) -> None:
        self.cursor.execute(f"PRAGMA table_info({tabla})")
        columnas_existentes = [c[1] for c in self.cursor.fetchall()]
        if columna not in columnas_existentes:
            alter_query = f'ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}'
            if foreign_key:
                alter_query += f' {foreign_key}'
            self.cursor.execute(alter_query)

    def _asegurar_admin(self) -> None:
        admin_pass_hash = self._hash_password("admin")
        self.cursor.execute("SELECT id FROM usuarios WHERE username = ?", ('admin',))
        admin_user = self.cursor.fetchone()
        if admin_user:
            self.cursor.execute("UPDATE usuarios SET password_hash = ?, rol = ? WHERE id = ?", (admin_pass_hash, 'Administrador', admin_user[0]))
        else:
            self.cursor.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)", ('admin', admin_pass_hash, 'Administrador'))
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def agregar_usuario(self, username: str, password: str, rol: str) -> bool:
        password_hash = self._hash_password(password)
        try:
            self.cursor.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)", (username, password_hash, rol))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def actualizar_usuario(self, user_id: int, username: str, password: str, rol: str) -> bool:
        try:
            if password and password != "(sin cambiar)":
                password_hash = self._hash_password(password)
                self.cursor.execute("UPDATE usuarios SET username = ?, password_hash = ?, rol = ? WHERE id = ?", (username, password_hash, rol, user_id))
            else:
                self.cursor.execute("UPDATE usuarios SET username = ?, rol = ? WHERE id = ?", (username, rol, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo actualizar el usuario: {e}")
            return False

    def verificar_usuario_y_obtener_rol(self, username: str, password: str) -> Optional[Tuple]:
        password_hash = self._hash_password(password)
        self.cursor.execute("SELECT id, username, rol FROM usuarios WHERE username = ? AND password_hash = ?", (username, password_hash))
        return self.cursor.fetchone()

    def obtener_usuarios(self) -> List[Tuple]:
        return self.ejecutar_query("SELECT id, username, rol FROM usuarios ORDER BY username", fetchall=True)

    def ejecutar_query(self, query: str, parameters: tuple = (), fetchone: bool = False, fetchall: bool = False) -> Any:
        try:
            self.cursor.execute(query, parameters)
            if fetchone: return self.cursor.fetchone()
            if fetchall: return self.cursor.fetchall()
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error de Query", f"Error al ejecutar la consulta: {e}")
            return False
            
    def obtener_registros(self, tabla: str, busqueda: str = "", columna_busqueda: str = "nombre") -> List[Tuple]:
        query = f"SELECT * FROM {tabla} WHERE {columna_busqueda} LIKE ? ORDER BY nombre ASC"
        return self.ejecutar_query(query, (f'%{busqueda}%',), fetchall=True)
        
    def obtener_producto_por_sku(self, sku: str) -> Optional[Tuple]:
        query = "SELECT id, nombre, cantidad, precio, categoria_id FROM productos WHERE sku = ?"
        return self.ejecutar_query(query, (sku,), fetchone=True)
        
    def obtener_producto_id_por_sku(self, sku: str) -> Optional[Tuple]:
        return self.ejecutar_query("SELECT id FROM productos WHERE sku = ?", (sku,), fetchone=True)

    def obtener_o_crear_categoria_id(self, nombre_categoria: str) -> Optional[int]:
        if not nombre_categoria:
            return None
        
        categoria = self.ejecutar_query("SELECT id FROM categorias WHERE nombre = ?", (nombre_categoria,), fetchone=True)
        if categoria:
            return categoria[0]
        else:
            return self.agregar_registro('categorias', {'nombre': nombre_categoria})

    def agregar_registro(self, tabla: str, data: Dict[str, Any]) -> int:
        columnas = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
        self.ejecutar_query(query, tuple(data.values()))
        return self.cursor.lastrowid

    def actualizar_registro(self, tabla: str, data: Dict[str, Any], record_id: int) -> bool:
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {tabla} SET {set_clause} WHERE id = ?"
        return self.ejecutar_query(query, tuple(data.values()) + (record_id,))

    def eliminar_registro(self, tabla: str, record_id: int) -> bool:
        return self.ejecutar_query(f"DELETE FROM {tabla} WHERE id = ?", (record_id,))
        
    def generar_factura_transaccion(self, venta_data: Dict[str, Any], detalles_data: List[Dict[str, Any]]) -> Optional[int]:
        try:
            self.cursor.execute("INSERT INTO ventas (cliente_id, usuario_id, fecha, total, metodo_pago, descuento_total) VALUES (?, ?, ?, ?, ?, ?)", 
                               (venta_data['cliente_id'], venta_data['usuario_id'], venta_data['fecha'], venta_data['total'], venta_data['metodo_pago'], venta_data['descuento_total']))
            venta_id = self.cursor.lastrowid
            
            if venta_data['metodo_pago'] == 'Credito':
                self.cursor.execute("UPDATE clientes SET saldo_deudor = saldo_deudor + ? WHERE id = ?", 
                                   (venta_data['total'], venta_data['cliente_id']))

            for detalle in detalles_data:
                self.cursor.execute("""
                    INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal, costo_unitario, descuento_aplicado) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (venta_id, detalle['producto_id'], detalle['cantidad'], detalle['precio_unitario'], detalle['subtotal'], detalle['costo_unitario'], detalle['descuento_aplicado']))
                self.cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", 
                                   (detalle['cantidad'], detalle['producto_id']))
            self.conn.commit()
            return venta_id
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error de Transacción", f"No se pudo completar la venta: {e}")
            return None

    def obtener_ventas_con_cliente(self, fecha_inicio: str, fecha_fin: str, categoria_id: Optional[int] = None) -> List[Tuple]:
        base_query = """
            SELECT DISTINCT v.id, v.fecha, c.nombre, v.total, v.metodo_pago, IFNULL(u.username, 'N/A')
            FROM ventas v 
            JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            JOIN detalles_venta dv ON v.id = dv.venta_id
            JOIN productos p ON dv.producto_id = p.id
            WHERE v.fecha BETWEEN ? AND ?
        """
        params = [fecha_inicio, fecha_fin]
        if categoria_id:
            base_query += " AND p.categoria_id = ?"
            params.append(categoria_id)
        
        base_query += " ORDER BY v.fecha DESC"
        return self.ejecutar_query(base_query, tuple(params), fetchall=True)

    def obtener_detalles_venta(self, venta_id: int) -> List[Tuple]:
        query = "SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal, dv.costo_unitario, dv.descuento_aplicado FROM detalles_venta dv JOIN productos p ON dv.producto_id = p.id WHERE dv.venta_id = ?"
        return self.ejecutar_query(query, (venta_id,), fetchall=True)
        
    def obtener_datos_grafico_ventas(self, fecha_inicio: str, fecha_fin: str, categoria_id: Optional[int] = None) -> List[Tuple]:
        base_query = """
            SELECT DATE(v.fecha), SUM(v.total) 
            FROM ventas v
            JOIN detalles_venta dv ON v.id = dv.venta_id
            JOIN productos p ON dv.producto_id = p.id
            WHERE v.fecha BETWEEN ? AND ?
        """
        params = [fecha_inicio, fecha_fin]
        if categoria_id:
            base_query += " AND p.categoria_id = ?"
            params.append(categoria_id)
        
        base_query += " GROUP BY DATE(v.fecha) ORDER BY DATE(v.fecha) ASC"
        return self.ejecutar_query(base_query, tuple(params), fetchall=True)

    def obtener_metricas_dashboard(self, fecha_inicio: str, fecha_fin: str, categoria_id: Optional[int] = None) -> Dict[str, Any]:
        params = [fecha_inicio, fecha_fin]
        cat_join = ""
        cat_where = ""
        if categoria_id:
            cat_join = """
                JOIN detalles_venta dv_cat ON v.id = dv_cat.venta_id
                JOIN productos p_cat ON dv_cat.producto_id = p_cat.id
            """
            cat_where = f" AND p_cat.categoria_id = {categoria_id}"
            params.append(categoria_id)
        
        total_query = f"""
            SELECT SUM(v.total) FROM ventas v
            {cat_join}
            WHERE v.fecha BETWEEN ? AND ? {cat_where.replace('p_cat.', 'p.') if categoria_id else ''}
        """
        ingresos = self.ejecutar_query(total_query, tuple(params) if categoria_id else (fecha_inicio, fecha_fin), fetchone=True)[0] or 0.0

        cmv_query = "SELECT SUM(dv.cantidad * dv.costo_unitario) FROM detalles_venta dv JOIN ventas v ON dv.venta_id = v.id JOIN productos p ON dv.producto_id = p.id WHERE v.fecha BETWEEN ? AND ?"
        params_cmv = [fecha_inicio, fecha_fin]
        if categoria_id:
            cmv_query += " AND p.categoria_id = ?"
            params_cmv.append(categoria_id)
        cmv = self.ejecutar_query(cmv_query, tuple(params_cmv), fetchone=True)[0] or 0.0
        
        ganancia = ingresos - cmv

        prod_query = "SELECT p.nombre, SUM(dv.cantidad) as total_vendido FROM detalles_venta dv JOIN productos p ON dv.producto_id = p.id JOIN ventas v ON dv.venta_id = v.id WHERE v.fecha BETWEEN ? AND ?"
        params_prod = [fecha_inicio, fecha_fin]
        if categoria_id:
            prod_query += " AND p.categoria_id = ?"
            params_prod.append(categoria_id)
        prod_query += " GROUP BY p.nombre ORDER BY total_vendido DESC LIMIT 1"
        prod_mas_vendido = self.ejecutar_query(prod_query, tuple(params_prod), fetchone=True)

        cliente_query = f"SELECT c.nombre, SUM(v.total) as total_comprado FROM ventas v JOIN clientes c ON v.cliente_id = c.id {cat_join} WHERE v.fecha BETWEEN ? AND ? {cat_where.replace('p_cat.', 'p.') if categoria_id else ''} GROUP BY c.nombre ORDER BY total_comprado DESC LIMIT 1"
        mejor_cliente = self.ejecutar_query(cliente_query, tuple(params) if categoria_id else (fecha_inicio, fecha_fin), fetchone=True)

        cat_vendida_query = "SELECT cat.nombre, SUM(dv.cantidad) as total_vendido FROM detalles_venta dv JOIN productos p ON dv.producto_id = p.id JOIN categorias cat ON p.categoria_id = cat.id JOIN ventas v ON dv.venta_id = v.id WHERE v.fecha BETWEEN ? AND ? GROUP BY cat.nombre ORDER BY total_vendido DESC LIMIT 1"
        cat_mas_vendida = self.ejecutar_query(cat_vendida_query, (fecha_inicio, fecha_fin), fetchone=True)

        vendedor_query = "SELECT u.username, COUNT(v.id) as total_ventas FROM ventas v JOIN usuarios u ON v.usuario_id = u.id WHERE v.fecha BETWEEN ? AND ? GROUP BY u.username ORDER BY total_ventas DESC LIMIT 1"
        mejor_vendedor = self.ejecutar_query(vendedor_query, (fecha_inicio, fecha_fin), fetchone=True)

        descuento_query = "SELECT SUM(descuento_total) FROM ventas WHERE fecha BETWEEN ? AND ?"
        total_descuentos = self.ejecutar_query(descuento_query, (fecha_inicio, fecha_fin), fetchone=True)[0] or 0.0

        return {
            "ingresos_totales": ingresos, "cmv": cmv, "ganancia_bruta": ganancia,
            "producto_mas_vendido": prod_mas_vendido[0] if prod_mas_vendido else "N/A", 
            "mejor_cliente": mejor_cliente[0] if mejor_cliente else "N/A",
            "categoria_mas_vendida": cat_mas_vendida[0] if cat_mas_vendida else "N/A",
            "mejor_vendedor": mejor_vendedor[0] if mejor_vendedor else "N/A",
            "total_descuentos": total_descuentos
        }

    def obtener_productos_bajo_stock(self) -> List[Tuple]:
        query = "SELECT id, nombre, sku, cantidad, stock_minimo FROM productos WHERE cantidad <= stock_minimo AND stock_minimo > 0 ORDER BY nombre ASC"
        return self.ejecutar_query(query, fetchall=True)

    def recibir_orden_compra(self, orden_id: int) -> bool:
        try:
            detalles = self.ejecutar_query("SELECT producto_id, cantidad FROM detalles_orden_compra WHERE orden_id = ?", (orden_id,), fetchall=True)
            if not detalles: raise sqlite3.Error("La orden no tiene productos.")
            for producto_id, cantidad in detalles:
                self.cursor.execute("UPDATE productos SET cantidad = cantidad + ? WHERE id = ?", (cantidad, producto_id))
            fecha_recepcion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE ordenes_compra SET estado = 'Recibida', fecha_recepcion = ? WHERE id = ?", (fecha_recepcion, orden_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error de Transacción", f"No se pudo recibir la orden: {e}")
            return False

    def obtener_ordenes_con_proveedor(self) -> List[Tuple]:
        query = "SELECT o.id, o.fecha_creacion, p.nombre, o.estado, o.fecha_recepcion FROM ordenes_compra o JOIN proveedores p ON o.proveedor_id = p.id ORDER BY o.fecha_creacion DESC"
        return self.ejecutar_query(query, fetchall=True)

    def obtener_detalles_orden(self, orden_id: int) -> List[Tuple]:
        query = "SELECT p.nombre, d.cantidad FROM detalles_orden_compra d JOIN productos p ON d.producto_id = p.id WHERE d.orden_id = ?"
        return self.ejecutar_query(query, (orden_id,), fetchall=True)

    def backup_database(self) -> None:
        self.conn.close()
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Archivos de Base de Datos", "*.db"), ("Todos los archivos", "*.*")],
            initialfile=f"backup-{datetime.datetime.now().strftime('%Y-%m-%d')}.db"
        )
        if backup_path:
            try:
                shutil.copyfile(self.db_name, backup_path)
                messagebox.showinfo("Copia de Seguridad Exitosa", f"La base de datos se ha guardado en:\n{backup_path}")
            except Exception as e:
                messagebox.showerror("Error en Copia de Seguridad", f"No se pudo crear la copia de seguridad: {e}")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def restore_database(self) -> bool:
        restore_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Base de Datos", "*.db"), ("Todos los archivos", "*.*")]
        )
        if restore_path and messagebox.askyesno("Confirmar Restauración", 
            "¿Está seguro de que desea restaurar la base de datos desde este archivo?\n"
            "TODOS LOS DATOS ACTUALES SE PERDERÁN Y LA APLICACIÓN SE REINICIARÁ."):
            self.conn.close()
            try:
                shutil.copyfile(restore_path, self.db_name)
                messagebox.showinfo("Restauración Exitosa", "La base de datos ha sido restaurada.\nLa aplicación se cerrará ahora. Por favor, vuelva a abrirla.")
                return True
            except Exception as e:
                messagebox.showerror("Error de Restauración", f"No se pudo restaurar la base de datos: {e}")
                self.conn = sqlite3.connect(self.db_name)
                self.cursor = self.conn.cursor()
        return False

    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Tuple]:
        return self.ejecutar_query("SELECT * FROM clientes WHERE id = ?", (cliente_id,), fetchone=True)

    def obtener_historial_ventas_cliente(self, cliente_id: int) -> List[Tuple]:
        query = "SELECT id, fecha, total, metodo_pago FROM ventas WHERE cliente_id = ? ORDER BY fecha DESC"
        return self.ejecutar_query(query, (cliente_id,), fetchall=True)

    def obtener_historial_pagos_cliente(self, cliente_id: int) -> List[Tuple]:
        query = "SELECT id, fecha, monto FROM pagos_clientes WHERE cliente_id = ? ORDER BY fecha DESC"
        return self.ejecutar_query(query, (cliente_id,), fetchall=True)

    def registrar_pago(self, cliente_id: int, monto: float) -> bool:
        try:
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO pagos_clientes (cliente_id, fecha, monto) VALUES (?, ?, ?)", (cliente_id, fecha, monto))
            self.cursor.execute("UPDATE clientes SET saldo_deudor = saldo_deudor - ? WHERE id = ?", (monto, cliente_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error de Transacción", f"No se pudo registrar el pago: {e}")
            return False

    def obtener_categorias(self) -> List[Tuple]:
        return self.ejecutar_query("SELECT * FROM categorias ORDER BY nombre", fetchall=True)

    def productos_en_categoria(self, categoria_id: int) -> int:
        return self.ejecutar_query("SELECT COUNT(*) FROM productos WHERE categoria_id = ?", (categoria_id,), fetchone=True)[0]

    def obtener_productos_con_categoria(self, busqueda: str = "", categoria_id: Optional[int] = None) -> List[Tuple]:
        query = """
            SELECT p.id, p.nombre, p.sku, p.costo, p.precio, p.cantidad, p.stock_minimo, IFNULL(c.nombre, 'Sin Categoría')
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
        """
        params = []
        where_clauses = []
        
        if busqueda:
            where_clauses.append("p.nombre LIKE ?")
            params.append(f'%{busqueda}%')
        
        if categoria_id:
            where_clauses.append("p.categoria_id = ?")
            params.append(categoria_id)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY p.nombre ASC"
        return self.ejecutar_query(query, tuple(params), fetchall=True)

    def close(self) -> None:
        self.conn.close()
