"""
Script de carga de datos de prueba para AppControlStock v3.0.
Inserta categorías, productos típicos argentinos, clientes,
proveedores y ventas de ejemplo.

Ejecutar: python seed_data.py
"""

import sqlite3
import hashlib
import datetime
import random

DB_NAME = "AppControlStock.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed():
    # Usamos nuestra clase Database para asegurar que las tablas existen
    from core.database import Database
    db = Database(DB_NAME)
    conn = db.conn
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")

    # =========================================================================
    # CATEGORÍAS
    # =========================================================================
    categorias = [
        "Almacén",
        "Bebidas",
        "Lácteos",
        "Panadería y Galletitas",
        "Carnes y Fiambres",
        "Limpieza",
        "Higiene Personal",
        "Golosinas",
        "Congelados",
        "Verdulería",
    ]

    cat_ids = {}
    for cat in categorias:
        try:
            c.execute("INSERT INTO categorias (nombre) VALUES (?)", (cat,))
            cat_ids[cat] = c.lastrowid
        except sqlite3.IntegrityError:
            c.execute("SELECT id FROM categorias WHERE nombre = ?", (cat,))
            cat_ids[cat] = c.fetchone()[0]

    # =========================================================================
    # PRODUCTOS TÍPICOS ARGENTINOS (nombre, sku, cantidad, precio, costo, stock_minimo, categoria)
    # =========================================================================
    productos = [
        # Almacén
        ("Yerba Mate Playadito 1kg", "7790070406903", 85, 4500, 3200, 15, "Almacén"),
        ("Yerba Mate Taragüi 500g", "7790387010107", 60, 2800, 1900, 10, "Almacén"),
        ("Azúcar Ledesma 1kg", "7790290003005", 100, 1200, 850, 20, "Almacén"),
        ("Harina 000 Cañuelas 1kg", "7790310001008", 70, 980, 650, 15, "Almacén"),
        ("Aceite Girasol Natura 1.5L", "7790070416101", 45, 3800, 2700, 10, "Almacén"),
        ("Aceite de Oliva Cocinero 500ml", "7790070416200", 30, 5200, 3800, 5, "Almacén"),
        ("Arroz Gallo Oro 1kg", "7790070418006", 55, 2100, 1500, 10, "Almacén"),
        ("Fideos Matarazzo Tallarín 500g", "7790070407009", 80, 1600, 1100, 15, "Almacén"),
        ("Fideos Lucchetti Tirabuzón 500g", "7790070417009", 65, 1450, 980, 10, "Almacén"),
        ("Polenta Presto Pronta 500g", "7790070430008", 40, 1100, 750, 8, "Almacén"),
        ("Puré de Tomate Arcor 520g", "7790580050009", 90, 890, 600, 20, "Almacén"),
        ("Salsa Filetto Knorr 340g", "7794000524002", 35, 1350, 900, 8, "Almacén"),
        ("Dulce de Leche La Serenísima 400g", "7790310001503", 50, 3200, 2300, 10, "Almacén"),
        ("Mermelada BC La Campagnola 454g", "7790070404503", 30, 2400, 1700, 5, "Almacén"),
        ("Café Torrado La Virginia 250g", "7790387020106", 40, 3500, 2500, 8, "Almacén"),
        ("Sal Fina Celusal 500g", "7790070415005", 60, 650, 400, 15, "Almacén"),

        # Bebidas
        ("Coca-Cola 2.25L", "7790895000607", 120, 2800, 2000, 25, "Bebidas"),
        ("Coca-Cola Zero 1.5L", "7790895002205", 60, 2400, 1700, 15, "Bebidas"),
        ("Sprite 2.25L", "7790895000706", 50, 2600, 1850, 15, "Bebidas"),
        ("Fanta Naranja 2.25L", "7790895000805", 40, 2500, 1800, 10, "Bebidas"),
        ("Agua Mineral Villavicencio 1.5L", "7790895010002", 80, 1200, 800, 20, "Bebidas"),
        ("Cerveza Quilmes Lata 473ml", "7792798001002", 150, 1400, 950, 30, "Bebidas"),
        ("Cerveza Brahma Lata 473ml", "7792798002002", 100, 1200, 850, 20, "Bebidas"),
        ("Vino Tinto Estancia Mendoza 750ml", "7790895050001", 35, 3800, 2700, 5, "Bebidas"),
        ("Fernet Branca 750ml", "8003610000109", 25, 12500, 9500, 5, "Bebidas"),
        ("Jugo Cepita Naranja 1L", "7792798010001", 45, 2200, 1500, 10, "Bebidas"),
        ("Soda Ivess 2L", "7790895060002", 60, 950, 600, 15, "Bebidas"),
        ("Gatorade Pomelo 500ml", "7792798020002", 30, 2100, 1500, 8, "Bebidas"),

        # Lácteos
        ("Leche Entera La Serenísima 1L", "7790310010000", 100, 1600, 1100, 25, "Lácteos"),
        ("Leche Descremada SanCor 1L", "7790310020001", 60, 1700, 1200, 15, "Lácteos"),
        ("Yogur Ser Natural 190g", "7790310030002", 40, 1200, 850, 10, "Lácteos"),
        ("Queso Cremoso Punta del Agua 1kg", "7790310040003", 20, 8500, 6200, 5, "Lácteos"),
        ("Manteca La Paulina 200g", "7790310050004", 35, 2800, 2000, 8, "Lácteos"),
        ("Crema de Leche La Serenísima 200ml", "7790310060005", 30, 1900, 1350, 8, "Lácteos"),

        # Panadería y Galletitas
        ("Pan Lactal Bimbo 350g", "7790200004001", 50, 2200, 1600, 10, "Panadería y Galletitas"),
        ("Galletitas Pepitos 119g", "7790200005002", 70, 1600, 1100, 15, "Panadería y Galletitas"),
        ("Galletitas Oreo 117g", "7622300290108", 65, 1800, 1250, 15, "Panadería y Galletitas"),
        ("Bizcochos Don Satur Salados 200g", "7790200006003", 45, 1400, 950, 10, "Panadería y Galletitas"),
        ("Criollitas Bagley 300g", "7622300200004", 55, 1500, 1000, 12, "Panadería y Galletitas"),
        ("Medialunas Congeladas x6", "7790200007004", 25, 3200, 2300, 5, "Panadería y Galletitas"),

        # Carnes y Fiambres
        ("Jamón Cocido Paladini 200g", "7790200010007", 35, 3800, 2800, 8, "Carnes y Fiambres"),
        ("Queso Tybo en Fetas 200g", "7790200011008", 30, 3200, 2300, 8, "Carnes y Fiambres"),
        ("Salame Milán Cagnoli 300g", "7790200012009", 20, 4500, 3200, 5, "Carnes y Fiambres"),
        ("Salchichas Patyviena x6", "7790200013010", 40, 2800, 2000, 10, "Carnes y Fiambres"),

        # Limpieza
        ("Lavandina Ayudín 1L", "7790300001001", 60, 950, 600, 15, "Limpieza"),
        ("Detergente Magistral 500ml", "7790300002002", 50, 1800, 1200, 12, "Limpieza"),
        ("Jabón en Polvo Skip 800g", "7790300003003", 35, 4200, 3000, 8, "Limpieza"),
        ("Suavizante Vivere 900ml", "7790300004004", 40, 2800, 2000, 10, "Limpieza"),
        ("Papel Higiénico Elegante x4", "7790300005005", 55, 2500, 1800, 12, "Limpieza"),
        ("Bolsas de Residuos x10", "7790300006006", 45, 1200, 800, 10, "Limpieza"),

        # Higiene Personal
        ("Jabón Dove Original 90g", "7790400001001", 50, 1200, 850, 10, "Higiene Personal"),
        ("Shampoo Sedal Rizos 340ml", "7790400002002", 30, 3500, 2500, 8, "Higiene Personal"),
        ("Pasta Dental Colgate 90g", "7790400003003", 60, 1800, 1200, 15, "Higiene Personal"),
        ("Desodorante Rexona Roll-On 50ml", "7790400004004", 40, 2800, 2000, 10, "Higiene Personal"),

        # Golosinas
        ("Alfajor Havanna 65g", "7790500001001", 80, 1800, 1200, 20, "Golosinas"),
        ("Alfajor Cachafaz Triple 75g", "7790500002002", 70, 1500, 1000, 15, "Golosinas"),
        ("Alfajor Jorgito Negro 55g", "7790500003003", 90, 900, 600, 20, "Golosinas"),
        ("Caramelos Sugus x10", "7790500004004", 50, 600, 400, 10, "Golosinas"),
        ("Chicles Beldent x10", "7790500005005", 60, 800, 550, 12, "Golosinas"),
        ("Chocolate Águila 150g", "7790500006006", 35, 3500, 2500, 8, "Golosinas"),
        ("Turrones Arcor x6", "7790500007007", 25, 2200, 1600, 5, "Golosinas"),

        # Congelados
        ("Empanadas La Salteña Carne x12", "7790600001001", 30, 5800, 4200, 8, "Congelados"),
        ("Milanesas de Pollo Granja Del Sol x4", "7790600002002", 25, 6200, 4500, 5, "Congelados"),
        ("Helado Freddo Dulce de Leche 1L", "7790600003003", 15, 7500, 5500, 3, "Congelados"),
        ("Papas Fritas McCain 400g", "7790600004004", 35, 3200, 2300, 8, "Congelados"),

        # Verdulería
        ("Papa x1kg", "PAPA001KG", 50, 1200, 800, 15, "Verdulería"),
        ("Cebolla x1kg", "CEBO001KG", 40, 1000, 650, 10, "Verdulería"),
        ("Tomate Redondo x1kg", "TOMA001KG", 35, 2500, 1800, 10, "Verdulería"),
        ("Lechuga Criolla x1", "LECH001UN", 30, 800, 500, 8, "Verdulería"),
        ("Banana Ecuador x1kg", "BANA001KG", 45, 1800, 1200, 10, "Verdulería"),
        ("Limón x1kg", "LIMO001KG", 30, 1500, 1000, 8, "Verdulería"),
    ]

    for nombre, sku, cant, precio, costo, stock_min, cat in productos:
        try:
            c.execute("""
                INSERT INTO productos (nombre, sku, cantidad, precio, costo, stock_minimo, categoria_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, sku, cant, precio, costo, stock_min, cat_ids[cat]))
        except sqlite3.IntegrityError:
            print(f"  [!] Producto '{nombre}' (SKU: {sku}) ya existe, se omitio.")

    # =========================================================================
    # CLIENTES
    # =========================================================================
    clientes = [
        ("Consumidor Final", "", "", ""),
        ("Juan Carlos Pérez", "1145678901", "jcperez@gmail.com", "Av. Rivadavia 3500, CABA"),
        ("María Laura González", "1156789012", "mlgonzalez@hotmail.com", "Calle San Martín 1200, Avellaneda"),
        ("Roberto Alejandro Díaz", "1167890123", "radiaz@yahoo.com.ar", "Mitre 850, Quilmes"),
        ("Silvia Beatriz Fernández", "1178901234", "sbfernandez@gmail.com", "Belgrano 2300, Lomas de Zamora"),
        ("Carlos Alberto Rodríguez", "1189012345", "carodriguez@outlook.com", "Av. Hipólito Yrigoyen 4500, Lanús"),
        ("Ana María López", "1190123456", "amlopez@gmail.com", "25 de Mayo 670, Banfield"),
        ("Diego Martín Romero", "1134567890", "dmromero@hotmail.com", "Av. Corrientes 1800, CABA"),
        ("Panadería Don José", "1123456789", "donjose.panaderia@gmail.com", "Calle Italia 450, Adrogué"),
        ("Kiosco El Trébol", "1112345678", "kioscoeltrebol@gmail.com", "Av. Mitre 2200, Avellaneda"),
        ("Restaurante La Esquina", "1198765432", "laesquina.resto@gmail.com", "Córdoba 3100, CABA"),
    ]

    cliente_ids = {}
    for nombre, tel, email, dir in clientes:
        try:
            c.execute("INSERT INTO clientes (nombre, telefono, email, direccion) VALUES (?, ?, ?, ?)", (nombre, tel, email, dir))
            cliente_ids[nombre] = c.lastrowid
        except sqlite3.IntegrityError:
            c.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre,))
            row = c.fetchone()
            if row:
                cliente_ids[nombre] = row[0]

    # =========================================================================
    # PROVEEDORES
    # =========================================================================
    proveedores = [
        ("Distribuidora Sur S.A.", "Marcelo Gómez", "1143210987", "ventas@distribuidorasur.com.ar"),
        ("Marolio Distribuciones", "Laura Sánchez", "1154321098", "pedidos@marolio.com.ar"),
        ("Coca-Cola FEMSA Argentina", "Atención Comercial", "0800-333-2652", "clientes@coca-cola.com.ar"),
        ("Arcor S.A.I.C.", "Departamento Ventas", "0800-333-2727", "ventas@arcor.com"),
        ("Molinos Río de la Plata", "Ana Martínez", "1176543210", "comercial@molinos.com.ar"),
        ("Cervecería Quilmes", "Soporte Comercial", "0800-222-7845", "distribuidores@quilmes.com.ar"),
    ]

    for nombre, contacto, tel, email in proveedores:
        try:
            c.execute("INSERT INTO proveedores (nombre, contacto, telefono, email) VALUES (?, ?, ?, ?)", (nombre, contacto, tel, email))
        except sqlite3.IntegrityError:
            print(f"  [!] Proveedor '{nombre}' ya existe, se omitio.")

    # =========================================================================
    # USUARIO VENDEDOR DE PRUEBA
    # =========================================================================
    try:
        c.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)", 
                  ("vendedor1", hash_password("vendedor1"), "Vendedor"))
    except sqlite3.IntegrityError:
        pass

    # =========================================================================
    # VENTAS DE EJEMPLO (últimos 30 días)
    # =========================================================================
    c.execute("SELECT id FROM usuarios WHERE username = 'admin'")
    admin_id = c.fetchone()[0]

    # Obtener IDs de productos
    c.execute("SELECT id, nombre, precio, costo FROM productos")
    all_products = c.fetchall()

    if all_products and cliente_ids:
        clientes_nombres = [n for n in cliente_ids.keys() if n != "Consumidor Final"]
        
        for days_ago in range(30, 0, -1):
            # Entre 1 y 4 ventas por día
            num_ventas = random.randint(1, 4)
            fecha_base = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            for _ in range(num_ventas):
                hora = random.randint(8, 20)
                minuto = random.randint(0, 59)
                fecha = fecha_base.replace(hour=hora, minute=minuto).strftime("%Y-%m-%d %H:%M:%S")
                
                # Cliente aleatorio (60% consumidor final, 40% cliente registrado)
                if random.random() < 0.6:
                    cliente_id = cliente_ids.get("Consumidor Final", 1)
                else:
                    cliente_nombre = random.choice(clientes_nombres)
                    cliente_id = cliente_ids[cliente_nombre]
                
                metodo = random.choice(["Contado", "Contado", "Contado", "Transferencia", "Credito"])
                
                # Entre 1 y 5 productos por venta
                num_items = random.randint(1, 5)
                items = random.sample(all_products, min(num_items, len(all_products)))
                
                total_venta = 0
                detalles = []
                for prod_id, prod_nombre, prod_precio, prod_costo in items:
                    cant = random.randint(1, 3)
                    subtotal = cant * prod_precio
                    total_venta += subtotal
                    detalles.append((prod_id, cant, prod_precio, subtotal, prod_costo))
                
                # Insertar venta
                c.execute("""
                    INSERT INTO ventas (cliente_id, usuario_id, fecha, total, metodo_pago, descuento_total) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cliente_id, admin_id, fecha, total_venta, metodo, 0))
                venta_id = c.lastrowid
                
                # Insertar detalles
                for prod_id, cant, precio, subtotal, costo in detalles:
                    c.execute("""
                        INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal, costo_unitario, descuento_aplicado) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (venta_id, prod_id, cant, precio, subtotal, costo, 0))
                
                # Si es crédito, actualizar saldo del cliente
                if metodo == "Credito" and cliente_id != cliente_ids.get("Consumidor Final", 1):
                    c.execute("UPDATE clientes SET saldo_deudor = saldo_deudor + ? WHERE id = ?", (total_venta, cliente_id))

    conn.commit()
    conn.close()

    print("\n[OK] Datos de prueba cargados exitosamente:")
    print(f"   - {len(categorias)} categorias")
    print(f"   - {len(productos)} productos")
    print(f"   - {len(clientes)} clientes")
    print(f"   - {len(proveedores)} proveedores")
    print(f"   - 1 usuario vendedor de prueba (vendedor1 / vendedor1)")
    print(f"   - ~90 ventas de ejemplo (ultimos 30 dias)")
    print(f"\n   Listo para probar!")


if __name__ == "__main__":
    seed()
