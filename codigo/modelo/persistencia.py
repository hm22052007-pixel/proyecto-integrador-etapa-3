"""MODELO - Persistencia de datos"""

import csv
import os

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_CODIGO = os.path.dirname(CARPETA_ACTUAL)
CARPETA_DATOS = os.path.join(CARPETA_CODIGO, "datos")

RUTA_INVENTARIO = os.path.join(CARPETA_DATOS, "inventario.csv")
RUTA_VENTAS = os.path.join(CARPETA_DATOS, "ventas.csv")

ENCABEZADOS_INVENTARIO = [
    "codigo",
    "nombre",
    "categoria",
    "stock",
    "stock_minimo",
    "precio_compra",
    "precio_venta",
    "fecha_vencimiento"
]
ENCABEZADOS_VENTAS = [
    "numero_factura",
    "fecha",
    "codigo_producto",
    "cantidad",
    "subtotal",
    "impuestos",
    "total"
]


def crear_archivo_si_no_existe(ruta, encabezados):
    """Crea un archivo CSV con encabezados si todavia no existe.
    Devuelve True si lo creo y False si ya existía."""
    if os.path.exists(ruta):
        return False
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)
    return True

def inicializar_archivos():
    """Crea inventario.csv y ventas.csv con encabezados si no existen.
    Devuelve la lista de archivos que creó."""
    creados = []
    if crear_archivo_si_no_existe(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO):
        creados.append("inventario.csv")
    if crear_archivo_si_no_existe(RUTA_VENTAS, ENCABEZADOS_VENTAS):
        creados.append("ventas.csv")
    return creados

def _escribir_csv_atomico(ruta_destino, encabezados, filas):
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    ruta_temporal = ruta_destino + ".tmp"
    with open(ruta_temporal, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=encabezados)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(fila)
    os.replace(ruta_temporal, ruta_destino)   # reemplazo atómico del original


def cargar_inventario():
    """Lee inventario.csv y devuelve una lista de diccionarios en bruto."""
    crear_archivo_si_no_existe(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO)
    filas = []
    with open(RUTA_INVENTARIO, mode="r", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            filas.append(fila)
    return filas


def guardar_inventario(lista_productos):
    """Escribe la lista de productos en inventario.csv (escritura atómica)."""
    filas = []
    for producto in lista_productos:
        fila = producto.to_dict() if hasattr(producto, "to_dict") else producto
        filas.append(fila)
    _escribir_csv_atomico(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO, filas)


def cargar_ventas():
    """Lee ventas.csv y devuelve una lista de diccionarios en bruto."""
    crear_archivo_si_no_existe(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    filas = []
    with open(RUTA_VENTAS, mode="r", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            filas.append(fila)
    return filas


def guardar_ventas(lista_ventas):
    """Escribe la lista de ventas en ventas.csv (escritura atómica)."""
    filas = []
    for venta in lista_ventas:
        fila = venta.to_dict() if hasattr(venta, "to_dict") else venta
        filas.append(fila)
    _escribir_csv_atomico(RUTA_VENTAS, ENCABEZADOS_VENTAS, filas)
