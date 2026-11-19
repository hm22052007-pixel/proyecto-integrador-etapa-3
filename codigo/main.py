from controlador import inventario_ctrl, ventas_ctrl, reportes_ctrl
from modelo import persistencia
from vista import consola
def opcion_registrar_producto():
    consola.mostrar_titulo("REGISTRAR PRODUCTO / RECIBIR PEDIDO")
    consola.mostrar_info("Para sumar unidades a un producto que ya existe use la opción 2.")
    producto = inventario_ctrl.agregar_producto(
        consola.pedir_texto("Código del producto: "),
        consola.pedir_texto("Nombre: "),
        consola.pedir_texto("Categoría: "),
        consola.pedir_texto("Stock inicial: "),
        consola.pedir_texto("Stock mínimo: "),
        consola.pedir_texto("Precio de compra: "),
        consola.pedir_texto("Precio de venta: "),
        consola.pedir_texto("Fecha de vencimiento (AAAA-MM-DD, vacío si no vence): "),
    )
    consola.mostrar_exito(f"Nuevo producto registrado: {producto.nombre} ({producto.codigo}).")
def opcion_actualizar_stock():
    consola.mostrar_titulo("ACTUALIZAR STOCK")
    producto = inventario_ctrl.actualizar_stock(
        consola.pedir_texto("Código del producto: "),
        consola.pedir_texto("Unidades a sumar (use un número negativo para restar): "),
    )
    consola.mostrar_exito(
        f"Stock actualizado: '{producto.nombre}' ahora tiene {producto.stock} unidades."
    )
def opcion_realizar_venta():
    consola.mostrar_titulo("REALIZAR VENTA")
    lineas = []
    continuar = True
    while continuar:
        codigo = consola.pedir_texto("Código del producto: ")
        cantidad = consola.pedir_texto("Cantidad: ")
        try:
            linea = ventas_ctrl.preparar_linea(codigo, cantidad, lineas)
        except ValueError as error:
            consola.mostrar_error(str(error))
        else:
            lineas.append(linea)
            consola.mostrar_exito(
                f"Agregado: {linea['nombre']} x{linea['cantidad']} "
                f"= ₡{linea['subtotal']:,.2f}"
            )
        continuar = consola.pedir_si_no("¿Agregar otro producto? (s/n): ")
    if not lineas:
        consola.mostrar_info("No se agregó ningún producto. Venta cancelada.")
        return
    consola.mostrar_resumen_venta(lineas)
    if not consola.pedir_si_no("¿Confirmar la venta? (s/n): "):
        consola.mostrar_info("Venta cancelada. El inventario no fue modificado.")
        return
    venta = ventas_ctrl.registrar_venta(lineas)
    consola.mostrar_factura(venta)
    consola.mostrar_exito("Venta registrada y stock actualizado.")
def opcion_generar_alertas():
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    consola.mostrar_alertas(reportes_ctrl.generar_reporte_stock(productos))
def opcion_consultar_inventario():
    consola.mostrar_titulo("CONSULTAR INVENTARIO")
    print("1. Ver todo el inventario")
    print("2. Filtrar (categoría, rango de precio o estado del stock)")
    print("3. Ordenar (nombre, stock o precio)")
    eleccion = consola.pedir_texto("Seleccione una opción: ")
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    if eleccion == "1":
        consola.mostrar_inventario(productos)
    elif eleccion == "2":
        consola.mostrar_info("Deje vacío el dato que no quiera usar como filtro.")
        filtrados = inventario_ctrl.filtrar_productos(
            productos,
            consola.pedir_texto("Categoría: ") or None,
            consola.pedir_texto("Precio de venta mínimo: ") or None,
            consola.pedir_texto("Precio de venta máximo: ") or None,
            consola.pedir_texto("Estado del stock (disponible / bajo / agotado): ").lower() or None,
        )
        consola.mostrar_inventario(
            filtrados, f"RESULTADO DEL FILTRO ({len(filtrados)} productos)"
        )
    elif eleccion == "3":
        criterio = consola.pedir_texto("Ordenar por (nombre / stock / precio): ").lower()
        orden = consola.pedir_texto("Orden (ascendente / descendente): ").lower()
        ordenados = inventario_ctrl.ordenar_productos(productos, criterio, orden)
        consola.mostrar_inventario(
            ordenados, f"INVENTARIO ORDENADO POR {criterio.upper()} ({orden})"
        )
    else:
        raise ValueError("Opción no válida en el submenú.")
def opcion_consultar_ventas():
    consola.mostrar_ventas(ventas_ctrl.clasificar_ventas())
def opcion_reporte_calidad(reporte_inicial):
    reporte_inventario = inventario_ctrl.generar_reporte_calidad(reporte_inicial)
    reporte_inventario["mensajes"] = reporte_inicial.get("mensajes", [])
    reporte_inventario["duplicados_consolidados"] = reporte_inicial.get(
        "duplicados_consolidados", 0
    )
    consola.mostrar_reporte_calidad(reporte_inventario, ventas_ctrl.reporte_calidad_ventas())
def opcion_graficos():
    consola.mostrar_titulo("GENERAR REPORTES GRÁFICOS")
    mostrar = consola.pedir_si_no("¿Desea verlos también en pantalla? (s/n): ")
    rutas = reportes_ctrl.generar_reporte_grafico(mostrar=mostrar)
    consola.mostrar_rutas_graficos(rutas)
    consola.mostrar_info("Las ventas atípicas no se grafican; vea la opción 7 para el detalle.")
    consola.mostrar_exito("Gráficos generados correctamente.")
def main():
    try:
        creados = persistencia.inicializar_archivos()
        if creados:
            consola.mostrar_info("Archivos de datos creados: " + ", ".join(creados) + ".")
        _, reporte_inicial = inventario_ctrl.cargar_inventario_limpio()
    except OSError as error:
        consola.mostrar_error(f"No se pudieron leer o guardar los archivos de datos: {error}")
        return
    consola.mostrar_info(
        f"Datos cargados: {reporte_inicial['total_filas_leidas']} filas leídas, "
        f"{reporte_inicial['registros_corregidos']} corregidas, "
        f"{reporte_inicial['registros_marcados']} marcadas, "
        f"{reporte_inicial['registros_descartados']} descartadas. "
        "Vea la opción 7 para el detalle."
    )
    acciones = {
        "1": opcion_registrar_producto,
        "2": opcion_actualizar_stock,
        "3": opcion_realizar_venta,
        "4": opcion_generar_alertas,
        "5": opcion_consultar_inventario,
        "6": opcion_consultar_ventas,
        "7": lambda: opcion_reporte_calidad(reporte_inicial),
        "8": opcion_graficos,
    }
    while True:
        consola.mostrar_menu_principal()
        try:
            eleccion = consola.pedir_texto("Seleccione una opción: ")
            if eleccion == "9":
                consola.mostrar_info("Gracias por usar el sistema. ¡Hasta pronto!")
                break
            accion = acciones.get(eleccion)
            if accion is None:
                consola.mostrar_error("Opción no válida. Elija un número del 1 al 9.")
            else:
                accion()
        except ValueError as error:
            consola.mostrar_error(str(error))
        except OSError as error:
            consola.mostrar_error(f"Problema con los archivos de datos: {error}")
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