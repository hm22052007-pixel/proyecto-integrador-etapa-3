import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from controlador import inventario_ctrl, ventas_ctrl, reportes_ctrl
from vista import consola, graficos
def buscar_factura():
    numero = consola.pedir_entero("Numero de factura")
    if numero is None:
        consola.mostrar_advertencia("No se ingreso ningun numero.")
        return
    filas = ventas_ctrl.buscar_factura(numero)
    consola.mostrar_factura(filas)
def ver_historial_ventas():
    filas = ventas_ctrl.consultar_ventas_dia()
    consola.mostrar_ventas(filas)
def ver_ventas_periodo():
    periodo = consola.pedir_texto("Periodo (dia / semana / mes)").lower()
    inicio, hoy, filas = ventas_ctrl.consultar_ventas_periodo(periodo)
    titulo = f"Ventas del {inicio.isoformat()} al {hoy.isoformat()}"
    consola.mostrar_ventas(filas, titulo)
def reiniciar_ventas():
    if not consola.pedir_confirmacion("Se respaldaran y borraran las ventas. Continuar?"):
        consola.mostrar_info("Operacion cancelada.")
        return
    destino = ventas_ctrl.reiniciar_ventas()
    consola.mostrar_exito(f"Ventas reiniciadas. Respaldo en {destino}")
def menu_ventas():
    acciones = {
        "1": buscar_factura,
        "2": ver_historial_ventas,
        "3": ver_ventas_periodo,
        "4": reiniciar_ventas,
        "5": None,
    }
    while True:
        consola.mostrar_submenu_ventas()
        try:
            opcion = consola.pedir_texto("Seleccione una opcion")
            if opcion == "5":
                return
            accion = acciones.get(opcion)
            if accion is None:
                consola.mostrar_error("Opcion no valida.")
            else:
                accion()
        except ValueError as error:
            consola.mostrar_error(str(error))
        consola.pausar()
def ver_inventario():
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    consola.mostrar_inventario(productos)
def filtrar_inventario():
    consola.mostrar_titulo("Filtrar productos")
    categoria = consola.pedir_texto("Categoria (Enter para omitir)")
    precio_min = consola.pedir_texto("Precio minimo (Enter para omitir)")
    precio_max = consola.pedir_texto("Precio maximo (Enter para omitir)")
    estado = consola.pedir_texto("Estado: disponible / bajo / agotado (Enter para omitir)")
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    resultado = inventario_ctrl.filtrar_productos(
        productos,
        categoria=categoria or None,
        precio_min=precio_min or None,
        precio_max=precio_max or None,
        estado=estado or None,
    )
    consola.mostrar_inventario(resultado)
def ordenar_inventario():
    consola.mostrar_titulo("Ordenar productos")
    criterio = consola.pedir_texto("Criterio: nombre / stock / precio").lower()
    orden = consola.pedir_texto("Orden: ascendente / descendente").lower()
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    resultado = inventario_ctrl.ordenar_productos(
        productos, criterio=criterio or "nombre", orden=orden or "ascendente",
    )
    consola.mostrar_inventario(resultado)
def consultar_inventario():
    acciones = {
        "1": ver_inventario,
        "2": filtrar_inventario,
        "3": ordenar_inventario,
        "4": None,
    }
    while True:
        consola.mostrar_submenu_inventario()
        try:
            opcion = consola.pedir_texto("Seleccione una opcion")
            if opcion == "4":
                return
            accion = acciones.get(opcion)
            if accion is None:
                consola.mostrar_error("Opcion no valida.")
            else:
                accion()
        except ValueError as error:
            consola.mostrar_error(str(error))
        consola.pausar()
def registrar_producto():
    consola.mostrar_titulo("Registrar producto")
    codigo = consola.pedir_texto("Codigo")
    nombre = consola.pedir_texto("Nombre")
    categoria = consola.pedir_texto("Categoria")
    stock = consola.pedir_entero("Stock inicial")
    stock_minimo = consola.pedir_entero("Stock minimo")
    precio_compra = consola.pedir_decimal("Precio de compra")
    precio_venta = consola.pedir_decimal("Precio de venta")
    fecha = consola.pedir_texto("Fecha de vencimiento (opcional)")
    producto = inventario_ctrl.agregar_producto(
        codigo, nombre, categoria, stock, stock_minimo,
        precio_compra, precio_venta, fecha,
    )
    consola.mostrar_exito(f"Producto {producto.codigo} registrado correctamente.")
def actualizar_stock():
    consola.mostrar_titulo("Actualizar stock")
    codigo = consola.pedir_texto("Codigo del producto")
    cantidad = consola.pedir_entero("Cantidad a sumar (negativo para restar)")
    if cantidad is None:
        consola.mostrar_advertencia("No se ingreso ninguna cantidad.")
        return
    producto = inventario_ctrl.actualizar_stock(codigo, cantidad)
    consola.mostrar_exito(
        f"Nuevo stock de {producto.nombre}: {producto.stock} unidades."
    )
def realizar_venta():
    consola.mostrar_titulo("Realizar venta")
    lineas = []
    while True:
        codigo = consola.pedir_texto("Codigo del producto (Enter para terminar)")
        if not codigo:
            break
        cantidad = consola.pedir_entero("Cantidad")
        if cantidad is None:
            consola.mostrar_advertencia("Cantidad vacia, se omite la linea.")
            continue
        linea = ventas_ctrl.preparar_linea(codigo, cantidad, lineas)
        lineas.append(linea)
        consola.mostrar_info(
            f"Agregado: {linea['nombre']} x {linea['cantidad']} = {linea['total']:.2f}"
        )
    if not lineas:
        consola.mostrar_advertencia("No se agrego ningun producto.")
        return
    venta = ventas_ctrl.registrar_venta(lineas)
    consola.mostrar_exito(
        f"Venta registrada. Factura {venta.numero_factura}, total {venta.total:.2f}."
    )
def generar_alertas():
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    reporte = reportes_ctrl.generar_reporte_stock(productos)
    consola.mostrar_alertas(reporte)
def eliminar_producto():
    consola.mostrar_titulo("Eliminar producto")
    codigo = consola.pedir_texto("Codigo del producto")
    if not codigo:
        consola.mostrar_advertencia("No se ingreso ningun codigo.")
        return
    producto = inventario_ctrl.eliminar_producto(codigo)
    consola.mostrar_exito(
        f"Producto eliminado: {producto['codigo']} - {producto['nombre']}"
    )
def reporte_calidad():
    _, reporte_inv = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    reporte = inventario_ctrl.generar_reporte_calidad(reporte_inv)
    consola.mostrar_reporte_calidad(reporte, "Reporte de calidad del inventario")
    consola.mostrar_reporte_calidad_ventas(ventas_ctrl.reporte_calidad_ventas())
def generar_graficos():
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    clasificadas = ventas_ctrl.clasificar_ventas()
    totales = ventas_ctrl.totales_por_producto(
        [c["fila"] for c in clasificadas if c["estado"] != "ilegible"],
        productos,
    )
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficos")
    figuras = [
        graficos.grafico_stock(productos, os.path.join(carpeta, "stock.png")),
        graficos.grafico_ventas_por_producto(totales, os.path.join(carpeta, "ventas_producto.png")),
    ]
    consola.mostrar_exito(f"Se generaron {len(figuras)} graficos en {carpeta}")
    if consola.pedir_confirmacion("Desea verlos en pantalla?"):
        graficos.mostrar_todos(figuras)
    graficos.cerrar_todos(figuras)
def main():
    acciones = {
        "1": registrar_producto,
        "2": actualizar_stock,
        "3": realizar_venta,
        "4": generar_alertas,
        "5": consultar_inventario,
        "6": eliminar_producto,
        "7": menu_ventas,
        "8": reporte_calidad,
        "9": generar_graficos,
    }
    while True:
        consola.mostrar_menu_principal()
        try:
            eleccion = consola.pedir_texto("Seleccione una opcion")
            if eleccion == "10":
                consola.mostrar_info("Gracias por usar el sistema. Hasta pronto!")
                break
            accion = acciones.get(eleccion)
            if accion is None:
                consola.mostrar_error("Opcion no valida.")
            else:
                accion()
        except ValueError as error:
            consola.mostrar_error(str(error))
        except OSError as error:
            consola.mostrar_error(f"Problema con los archivos: {error}")
        except (KeyboardInterrupt, EOFError):
            print()
            consola.mostrar_info("Programa cerrado por el usuario.")
            break
        try:
            consola.pausar()
        except (KeyboardInterrupt, EOFError):
            print()
            break
if __name__ == "__main__":
    main()