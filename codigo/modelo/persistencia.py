import csv
import os
from datetime import datetime
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_CODIGO = os.path.dirname(CARPETA_ACTUAL)
CARPETA_DATOS = os.path.join(CARPETA_CODIGO, "datos")
CARPETA_RESPALDO = os.path.join(CARPETA_CODIGO, "datos_respaldo")
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
    if os.path.exists(ruta):
        return False
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)
    return True
def inicializar_archivos():
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
    os.replace(ruta_temporal, ruta_destino)
def cargar_inventario():
    crear_archivo_si_no_existe(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO)
    filas = []
    with open(RUTA_INVENTARIO, mode="r", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            filas.append(fila)
    return filas
def guardar_inventario(lista_productos):
    filas = []
    for producto in lista_productos:
        fila = producto.to_dict() if hasattr(producto, "to_dict") else producto
        filas.append(fila)
    _escribir_csv_atomico(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO, filas)
def cargar_ventas():
    crear_archivo_si_no_existe(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    filas = []
    with open(RUTA_VENTAS, mode="r", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            filas.append(fila)
    return filas
def guardar_ventas(lista_ventas):
    filas = []
    for venta in lista_ventas:
        fila = venta.to_dict() if hasattr(venta, "to_dict") else venta
        filas.append(fila)
    _escribir_csv_atomico(RUTA_VENTAS, ENCABEZADOS_VENTAS, filas)
def respaldar_y_vaciar_ventas():
    os.makedirs(CARPETA_RESPALDO, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(CARPETA_RESPALDO, f"ventas_{marca}.csv")
    if os.path.exists(RUTA_VENTAS):
        os.replace(RUTA_VENTAS, destino)
    crear_archivo_si_no_existe(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    return destino