# AppControlStock v3.0
## Sistema de Gestión Integrado para Comercios (POS/ERP)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Version](https://img.shields.io/badge/Versión-3.0-green?style=for-the-badge)

Sistema de escritorio desarrollado en Python con Tkinter para la gestión integral de inventario, ventas, clientes y reportes. Diseñado para ser una solución robusta y fácil de usar para pequeñas y medianas empresas.

---

## 📜 Descripción

Este proyecto es una aplicación de escritorio multifuncional que centraliza las operaciones clave de un negocio. Permite llevar un control detallado del stock, gestionar una base de datos de clientes (incluyendo cuentas corrientes), realizar ventas a través de una interfaz de Punto de Venta (POS) y analizar el rendimiento del negocio mediante un dashboard y reportes detallados.

La aplicación utiliza una base de datos local SQLite, lo que la hace portable y fácil de instalar sin necesidad de un servidor de base de datos externo.

---

## ✨ Características Principales

* **👤 Gestión de Usuarios:**
    * Sistema de inicio de sesión seguro (contraseñas hasheadas con SHA-256).
    * Roles de usuario (Administrador, Vendedor) con distintos niveles de acceso.
    * Panel de administración para gestionar cuentas de usuarios.

* **📦 Gestión de Inventario (Stock):**
    * Creación, actualización y eliminación de productos y categorías.
    * Control de stock, precio de costo, precio de venta y stock mínimo.
    * Búsqueda y filtrado avanzado de productos por nombre y categoría.
    * **Importación y exportación masiva** de productos mediante archivos CSV.
    * Generación e **impresión de etiquetas con códigos de barras** (Code128).

* **🛒 Punto de Venta (POS):**
    * Interfaz rápida para escanear productos por SKU/código de barras.
    * Carrito de compras con actualización en tiempo real.
    * Selección de clientes y métodos de pago (Contado, Crédito, Transferencia).
    * Aplicación de descuentos por artículo.
    * Generación de **tickets de venta en formato PDF**.

* **👥 Gestión de Clientes:**
    * Base de datos de clientes con información de contacto completa.
    * **Manejo de cuentas corrientes** y saldos deudores.
    * Registro de pagos y historial de transacciones por cliente.
    * Indicadores visuales para clientes con deudas pendientes.

* **🚚 Proveedores y Órdenes de Compra:**
    * Gestión de proveedores con datos de contacto.
    * Creación y seguimiento de órdenes de compra para reponer stock.
    * Registro de recepción de mercadería.

* **📊 Dashboard y Reportes:**
    * **Dashboard visual** con métricas clave: ingresos, CMV, ganancia bruta, producto más vendido, mejor cliente, categoría líder y mejor vendedor.
    * Gráficos de ventas por período de tiempo (requiere Matplotlib).
    * Filtrado por rango de fechas y categoría.
    * Generación de reportes de ventas con vista de detalle.
    * Exportación de reportes a CSV.

* **⚙️ Administración:**
    * Sistema de **copia de seguridad (backup) y restauración** de la base de datos.
    * Personalización del logo de la empresa.
    * Panel de **alertas para productos con bajo stock** con contador en tiempo real.

---

## 🏗️ Arquitectura del Proyecto

La versión 3.0 introduce una **arquitectura modular** que separa la lógica de negocio de la interfaz gráfica, mejorando la mantenibilidad y escalabilidad del código:

```
AppControlStock-V3.0/
│
├── main.py                  # Punto de entrada (ligero)
│
├── core/                    # Lógica de negocio y datos
│   ├── __init__.py
│   ├── config.py            # ConfigManager: persistencia de configuración
│   ├── database.py          # Database: toda la interacción con SQLite
│   └── utils.py             # Utilidades: generación de PDFs y códigos de barras
│
├── ui/                      # Interfaz gráfica (Tkinter)
│   ├── __init__.py
│   ├── login.py             # Ventana de inicio de sesión
│   ├── app.py               # Contenedor principal (AppGestion)
│   └── tabs/                # Pestañas modulares
│       ├── facturacion_tab.py
│       ├── stock_tab.py
│       ├── clientes_tab.py
│       ├── dashboard_tab.py
│       ├── categorias_tab.py
│       ├── proveedores_tab.py
│       ├── ordenes_compra_tab.py
│       ├── alertas_tab.py
│       ├── reportes_tab.py
│       ├── admin_tab.py
│       ├── ventana_cuenta_corriente.py
│       └── ventana_impresion_etiquetas.py
│
├── AppControlStock.db       # Base de datos SQLite (se crea automáticamente)
├── config.ini               # Configuración de la aplicación
└── requirements.txt         # Dependencias del proyecto
```

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología |
|---|---|
| **Lenguaje** | Python 3.x |
| **Interfaz Gráfica** | Tkinter / TTK (incluida en Python) |
| **Base de Datos** | SQLite 3 (incluida en Python) |
| **Gráficos** | Matplotlib |
| **Generación de PDF** | FPDF |
| **Códigos de Barras** | python-barcode + Pillow |

---

## 🚀 Puesta en Marcha

### Prerrequisitos

Asegúrate de tener **Python 3.8+** instalado en tu sistema.

### Instalación

1.  **Clona el repositorio:**
    ```sh
    git clone https://github.com/Floree1/AppControlStock-V3.git
    cd AppControlStock-V3
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```sh
    pip install -r requirements.txt
    ```

### Ejecución

```sh
python main.py
```

La primera vez que se inicie, se creará automáticamente el archivo de base de datos `AppControlStock.db` con las tablas necesarias y un usuario administrador por defecto.

**Credenciales de Administrador por defecto:**
| Campo | Valor |
|---|---|
| **Usuario** | `admin` |
| **Contraseña** | `admin` |

> ⚠️ **Se recomienda cambiar la contraseña del administrador** desde el panel de Administración tras el primer inicio de sesión.

---

## 📋 Changelog

### v3.0 — Refactorización Modular (Mayo 2026)
* **Arquitectura completamente reestructurada**: migración del archivo monolítico (~2400 líneas) a una estructura modular con separación de responsabilidades (`core/`, `ui/`, `ui/tabs/`).
* **Nuevo punto de entrada ligero** (`main.py` < 30 líneas).
* **Capa de datos desacoplada**: clase `Database` con type hints, docstrings y manejo de errores mejorado.
* **Utilidades extraídas**: funciones de generación de PDFs y códigos de barras centralizadas en `core/utils.py`.
* **Importaciones condicionales**: la aplicación funciona correctamente incluso sin Matplotlib o python-barcode instalados, informando al usuario.

### v2.5 — Versión Original
* Versión inicial con todas las funcionalidades de POS/ERP en un único archivo.

---

## 📄 Licencia

Este proyecto está bajo la licencia incluida en el archivo [LICENSE](LICENSE).

---

<p align="center">
  <b>Desarrollado por MauroDEV</b><br>
  Sistema v3.0 | © 2026
</p>
