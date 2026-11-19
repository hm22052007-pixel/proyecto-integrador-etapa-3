from controlador import inventario_ctrl, ventas_ctrl, reportes_ctrl
from vista import consola, graficos
def menu_ventas():
    while True:
        consola.mostrar_submenu_ventas()
        opcion = consola.pedir_texto("Seleccione una opcion")
        try:
            if opcion == "6.1":
                numero = consola.pedir_entero("Numero de factura")
                filas = ventas_ctrl.buscar_factura(numero)
                consola.mostrar_factura(filas)
            elif opcion == "6.2":
                return
            else:
                consola.mostrar_error("Opcion no valida.")
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
def consultar_inventario():
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    consola.mostrar_inventario(productos)
def reporte_calidad():
    _, reporte_inv = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    reporte = inventario_ctrl.generar_reporte_calidad(reporte_inv)
    consola.mostrar_reporte_calidad(reporte)
    consola.mostrar_reporte_calidad(ventas_ctrl.reporte_calidad_ventas())
def generar_graficos():
    rutas = reportes_ctrl.generar_reporte_grafico()
    for ruta in rutas:
        consola.mostrar_exito(f"Grafico guardado en {ruta}")
def main():
    acciones = {
        "1": registrar_producto,
        "2": actualizar_stock,
        "3": realizar_venta,
        "4": generar_alertas,
        "5": consultar_inventario,
        "6": menu_ventas,
        "7": reporte_calidad,
        "8": generar_graficos,
    }
    while True:
        consola.mostrar_menu_principal()
        try:
            eleccion = consola.pedir_texto("Seleccione una opcion")
            if eleccion == "9":
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