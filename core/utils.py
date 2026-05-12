import os
import datetime
from tkinter import messagebox

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False


def generar_ticket_pdf(venta_info: dict, filepath: str) -> bool:
    """Genera un ticket de venta en PDF."""
    if not FPDF_AVAILABLE:
        messagebox.showerror("Librería Faltante", "La librería FPDF es necesaria para generar PDFs.\nInstálala con: pip install fpdf")
        return False

    try:
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'Ticket de Venta', 0, 1, 'C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Venta ID: {venta_info['venta_id']}", 0, 1, 'L')
        pdf.cell(0, 8, f"Fecha: {venta_info['fecha']}", 0, 1, 'L')
        pdf.cell(0, 8, f"Cliente: {venta_info['cliente']}", 0, 1, 'L')
        pdf.cell(0, 8, f"Atendido por: {venta_info['vendedor']}", 0, 1, 'L')
        pdf.cell(0, 8, f"Metodo de Pago: {venta_info['metodo_pago']}", 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(80, 10, 'Producto', 1, 0, 'C')
        pdf.cell(30, 10, 'Cantidad', 1, 0, 'C')
        pdf.cell(40, 10, 'Precio Unit.', 1, 0, 'C')
        pdf.cell(40, 10, 'Subtotal', 1, 1, 'C')
        
        pdf.set_font("Arial", '', 10)
        for item in venta_info['detalles']:
            pdf.cell(80, 10, item[0], 1, 0)
            pdf.cell(30, 10, str(item[1]), 1, 0, 'C')
            pdf.cell(40, 10, f"${float(item[2]):.2f}", 1, 0, 'R')
            pdf.cell(40, 10, f"${float(item[3]):.2f}", 1, 1, 'R')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Total: ${venta_info['total']:.2f}", 0, 1, 'R')

        pdf.output(filepath)
        return True
    except Exception as e:
        messagebox.showerror("Error al generar PDF", f"No se pudo crear el archivo PDF: {e}")
        return False


def generar_etiquetas_pdf(productos_cantidades: list, filepath: str) -> bool:
    """
    Genera un PDF con etiquetas de código de barras.
    productos_cantidades es una lista de tuplas: (cantidad, (id, nombre, sku, categoria, precio, costo, min))
    """
    if not FPDF_AVAILABLE or not BARCODE_AVAILABLE:
        messagebox.showerror("Librerías Faltantes", "Las librerías FPDF y python-barcode son necesarias.\nInstálalas con: pip install fpdf python-barcode pillow")
        return False

    temp_barcode_files = []
    try:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        label_width = 65
        label_height = 25
        margin_top = 10
        margin_left = 7.5
        gap_x = 0
        gap_y = 0
        
        x = margin_left
        y = margin_top

        for cantidad, prod in productos_cantidades:
            if cantidad <= 0: continue
            
            for _ in range(cantidad):
                if y + label_height > 297: # Salto de página
                    pdf.add_page()
                    x = margin_left
                    y = margin_top

                prod_id, nombre, sku, categoria, precio, _, _ = prod
                Code128 = barcode.get_barcode_class('code128')
                writer_options = {'module_height': 8.0, 'font_size': 8, 'text_distance': 3.0, 'quiet_zone': 2.0}
                code = Code128(sku, writer=ImageWriter())
                barcode_filename = f"temp_barcode_{sku}"
                barcode_path = code.save(barcode_filename, options=writer_options)
                temp_barcode_files.append(barcode_path)

                pdf.set_font('Arial', '', 8)
                pdf.set_xy(x + 2, y + 2)
                pdf.cell(label_width - 4, 5, nombre[:35], 0, 1)

                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(x + 2, y + 7)
                pdf.cell(label_width - 4, 6, f"${float(precio):.2f}", 0, 1)

                pdf.image(barcode_path, x + 2, y + 14, w=label_width - 5)
                
                x += label_width + gap_x
                if x + label_width > 210: # Salto de línea
                    x = margin_left
                    y += label_height + gap_y

        pdf.output(filepath)
        return True
    except Exception as e:
        messagebox.showerror("Error al Generar PDF", f"No se pudo crear el archivo de etiquetas: {e}")
        return False
    finally:
        for f in temp_barcode_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
