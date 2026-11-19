import os
import colorama
from colorama import Fore, Style
colorama.init()
ANCHO = 70
def _linea(caracter="="):
    print(caracter * ANCHO)
def _centrar(texto):
    return texto.center(ANCHO)
def mostrar_menu_principal():
    _linea()
    print(_centrar("DISTRIBUIDORA INDUSTRIAL DEL PACIFICO S.A."))
    print(_centrar("SISTEMA DE INVENTARIOS Y PUNTO DE VENTA"))
    _linea()
    print("1. Registrar producto")
    print("2. Actualizar stock")
    print("3. Realizar venta")
    print("4. Generar alertas")
    print("5. Consultar inventario")
    print("6. Eliminar producto")
    print("7. Consultar ventas")
    print("8. Reporte de calidad de datos")
    print("9. Generar reportes graficos")
    print("10. Salir")
    _linea("-")
def mostrar_submenu_inventario():
    _linea("-")
    print("CONSULTAR INVENTARIO")
    print("1. Ver inventario completo")
    print("2. Filtrar productos")
    print("3. Ordenar productos")
    print("4. Volver al menu principal")
    _linea("-")
def mostrar_submenu_ventas():
    _linea("-")
    print("CONSULTAR VENTAS")
    print("1. Buscar factura por numeracion")
    print("2. Historial de ventas")
    print("3. Ventas por periodo (dia / semana / mes)")
    print("4. Reiniciar ventas")
    print("5. Volver al menu principal")
    _linea("-")
def pedir_texto(mensaje):
    return input(f"{mensaje}: ").strip()
def pedir_entero(mensaje):
    while True:
        valor = pedir_texto(mensaje)
        if not valor:
            return None
        try:
            return int(valor)
        except ValueError:
            mostrar_error("Debe ingresar un numero entero.")
def pedir_decimal(mensaje):
    while True:
        try:
            return float(pedir_texto(mensaje))
        except ValueError:
            mostrar_error("Debe ingresar un numero valido.")
def pedir_confirmacion(mensaje):
    respuesta = pedir_texto(f"{mensaje} (s/n)").lower()
    return respuesta == "s"
def mostrar_info(mensaje):
    print(Fore.CYAN + str(mensaje) + Style.RESET_ALL)
def mostrar_exito(mensaje):
    print(Fore.GREEN + str(mensaje) + Style.RESET_ALL)
def mostrar_advertencia(mensaje):
    print(Fore.YELLOW + str(mensaje) + Style.RESET_ALL)
def mostrar_error(mensaje):
    print(Fore.RED + str(mensaje) + Style.RESET_ALL)
def mostrar_titulo(texto):
    _linea()
    print(Fore.CYAN + Style.BRIGHT + texto.upper() + Style.RESET_ALL)
    _linea("-")
def mostrar_tabla(encabezados, filas, anchos=None):
    if anchos is None:
        anchos = [
            max([len(str(h))] + [len(str(f[i])) for f in filas])
            for i, h in enumerate(encabezados)
        ]
    formato = " ".join(f"{{:<{a}}}" for a in anchos)
    print(Fore.CYAN + formato.format(*encabezados) + Style.RESET_ALL)
    print("-" * (sum(anchos) + len(anchos) - 1))
    for fila in filas:
        print(formato.format(*[str(c) for c in fila]))
def mostrar_factura(filas):
    if not filas:
        mostrar_error("No se encontro la factura.")
        return
    primera = filas[0]
    mostrar_titulo(f"Factura {primera['numero_factura']}")
    print(f"Fecha: {primera['fecha']}")
    _linea("-")
    datos = []
    for fila in filas:
        datos.append((
            fila.get("codigo_producto", ""),
            fila.get("cantidad", ""),
            f"{float(fila.get('subtotal', 0)):.2f}",
            f"{float(fila.get('impuestos', 0)):.2f}",
            f"{float(fila.get('total', 0)):.2f}",
        ))
    mostrar_tabla(["Producto", "Cant.", "Subtotal", "Impuestos", "Total"], datos)
    total = sum(float(f.get("total", 0)) for f in filas)
    print(Fore.GREEN + f"TOTAL DE LA FACTURA: {total:.2f}" + Style.RESET_ALL)
def mostrar_ventas(filas, titulo="Historial de ventas"):
    mostrar_titulo(titulo)
    if not filas:
        mostrar_info("No hay ventas registradas.")
        return
    datos = []
    for fila in filas:
        datos.append((
            fila.get("numero_factura", ""),
            fila.get("fecha", ""),
            fila.get("codigo_producto", ""),
            fila.get("cantidad", ""),
            f"{float(fila.get('total', 0)):.2f}",
        ))
    mostrar_tabla(["Factura", "Fecha", "Producto", "Cant.", "Total"], datos)
    total = sum(float(f.get("total", 0)) for f in filas)
    print(Fore.GREEN + f"Total de filas: {len(filas)}   Monto: {total:.2f}" + Style.RESET_ALL)
def mostrar_inventario(productos):
    mostrar_titulo("Inventario actual")
    if not productos:
        mostrar_info("No hay productos registrados.")
        return
    filas = [
        (p["codigo"], p["nombre"], p["categoria"], p["stock"], p["stock_minimo"],
         f"{p['precio_compra']:.2f}", f"{p['precio_venta']:.2f}")
        for p in productos
    ]
    mostrar_tabla(
        ["Codigo", "Nombre", "Categoria", "Stock", "Min", "Compra", "Venta"],
        filas,
    )
    negativos = [p for p in productos if p["stock"] < 0]
    if negativos:
        mostrar_advertencia(
            "Atencion: hay productos con stock negativo. "
            "Corrija el dato con la opcion 2 o elimine el producto con la opcion 6."
        )
def mostrar_alertas(reporte):
    mostrar_titulo("Alertas de stock")
    if not reporte["alertas"]:
        mostrar_exito("Todos los productos tienen stock suficiente.")
        return
    for alerta in reporte["alertas"]:
        if alerta["tipo_alerta"] == "agotado":
            mostrar_error(alerta["mensaje"])
        else:
            mostrar_advertencia(alerta["mensaje"])
def mostrar_reporte_calidad(reporte, titulo="Reporte de calidad de datos"):
    mostrar_titulo(titulo)
    print(f"Registros leidos: {reporte.get('total_filas_leidas', 0)}")
    print(f"Registros corregidos: {reporte.get('registros_corregidos', 0)}")
    print(f"Registros descartados: {reporte.get('registros_descartados', 0)}")
    print(f"Registros marcados: {reporte.get('registros_marcados', 0)}")
    print(f"Duplicados consolidados: {reporte.get('duplicados_consolidados', 0)}")
    for mensaje in reporte.get("mensajes", []):
        mostrar_advertencia(f" - {mensaje}")
def mostrar_reporte_calidad_ventas(reporte):
    mostrar_titulo("Reporte de calidad de ventas")
    print(f"Ventas leidas: {reporte.get('total_ventas_leidas', 0)}")
    print(f"Ventas validas: {reporte.get('ventas_validas', 0)}")
    print(f"Ventas marcadas (atipicas): {reporte.get('ventas_marcadas', 0)}")
    print(f"Ventas ilegibles: {reporte.get('ventas_ilegibles', 0)}")
    for mensaje in reporte.get("mensajes", []):
        mostrar_advertencia(f" - {mensaje}")
def pausar():
    input(Fore.CYAN + "\nPresione Enter para continuar..." + Style.RESET_ALL)
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")