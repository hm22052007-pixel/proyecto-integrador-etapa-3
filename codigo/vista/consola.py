ANCHO = 78
def _linea(caracter="="):
    return caracter * ANCHO
def _tabla(encabezados, filas, alineaciones=None):
    if not filas:
        print("  (sin registros para mostrar)")
        return
    filas_texto = [[str(celda) for celda in fila] for fila in filas]
    anchos = [len(str(encabezado)) for encabezado in encabezados]
    for fila in filas_texto:
        for i, celda in enumerate(fila):
            anchos[i] = max(anchos[i], len(celda))
    if alineaciones is None:
        alineaciones = ["<"] * len(encabezados)
    def formatear(celdas):
        partes = []
        for celda, ancho, alineacion in zip(celdas, anchos, alineaciones):
            if alineacion == ">":
                partes.append(celda.rjust(ancho))
            elif alineacion == "^":
                partes.append(celda.center(ancho))
            else:
                partes.append(celda.ljust(ancho))
        return "  ".join(partes).rstrip()
    print(formatear(encabezados))
    print("-" * len(formatear(encabezados)))
    for fila in filas_texto:
        print(formatear(fila))
def pedir_texto(mensaje):
    return input(mensaje).strip()
def pedir_si_no(mensaje):
    respuesta = input(mensaje).strip().lower()
    return respuesta.startswith("s")
def pausar(mensaje="\nPresione Enter para continuar..."):
    input(mensaje)
def mostrar_titulo(titulo):
    print()
    print(_linea())
    print(titulo.center(ANCHO))
    print(_linea())
def mostrar_info(mensaje):
    print(f"[INFO] {mensaje}")
def mostrar_exito(mensaje):
    print(f"[OK] {mensaje}")
def mostrar_error(mensaje):
    print(f"[ERROR] {mensaje}")
def mostrar_menu_principal():
    print()
    print(_linea())
    print("DISTRIBUIDORA INDUSTRIAL DEL PACÍFICO S.A.".center(ANCHO))
    print("SISTEMA DE INVENTARIOS Y PUNTO DE VENTA".center(ANCHO))
    print(_linea())
    print("1. Registrar producto / recibir pedido")
    print("2. Actualizar stock")
    print("3. Realizar venta")
    print("4. Generar alertas")
    print("5. Consultar inventario")
    print("6. Consultar ventas")
    print("7. Reporte de calidad")
    print("8. Generar reportes gráficos")
    print("9. Salir")
    print("-" * ANCHO)
def mostrar_inventario(productos, titulo="INVENTARIO ACTUAL"):
    print()
    print(titulo)
    print(_linea("-"))
    filas = [
        (
            p.codigo,
            p.nombre,
            p.categoria,
            p.stock,
            p.stock_minimo,
            f"₡{p.precio_compra:,.2f}",
            f"₡{p.precio_venta:,.2f}",
            p.fecha_vencimiento or "-",
        )
        for p in productos
    ]
    _tabla(
        ["Código", "Nombre", "Categoría", "Stock", "Mín.", "Compra", "Venta", "Vence"],
        filas,
        ["<", "<", "<", ">", ">", ">", ">", "<"],
    )
    print(f"\nTotal de productos mostrados: {len(productos)}")
def mostrar_resumen_venta(lineas):
    print()
    print("RESUMEN DE LA VENTA")
    print(_linea("-"))
    filas = [
        (
            linea["codigo"],
            linea["nombre"],
            linea["cantidad"],
            f"₡{linea['precio_unitario']:,.2f}",
            f"₡{linea['subtotal']:,.2f}",
        )
        for linea in lineas
    ]
    _tabla(
        ["Código", "Producto", "Cant.", "Precio unit.", "Subtotal"],
        filas,
        ["<", "<", ">", ">", ">"],
    )
    subtotal = sum(l["subtotal"] for l in lineas)
    impuestos = round(subtotal * 0.13, 2)
    print(f"\nSubtotal:  ₡{subtotal:,.2f}")
    print(f"IVA (13%): ₡{impuestos:,.2f}")
    print(f"TOTAL:     ₡{subtotal + impuestos:,.2f}")
def mostrar_factura(venta):
    print()
    print(_linea())
    print(f"FACTURA N° {venta.numero_factura}".center(ANCHO))
    print(f"Fecha: {venta.fecha}".center(ANCHO))
    print(_linea())
    filas = [
        (
            linea["codigo"],
            linea["nombre"],
            linea["cantidad"],
            f"₡{linea['precio_unitario']:,.2f}",
            f"₡{linea['subtotal']:,.2f}",
        )
        for linea in venta.lineas
    ]
    _tabla(
        ["Código", "Producto", "Cant.", "Precio unit.", "Subtotal"],
        filas,
        ["<", "<", ">", ">", ">"],
    )
    print(_linea("-"))
    print(f"Subtotal:  ₡{venta.subtotal:,.2f}")
    print(f"IVA (13%): ₡{venta.impuestos:,.2f}")
    print(f"TOTAL:     ₡{venta.total:,.2f}")
    print(_linea())
def mostrar_ventas(clasificadas):
    print()
    print("HISTORIAL DE VENTAS")
    print(_linea("-"))
    filas = []
    for item in clasificadas:
        fila = item["fila"]
        estado = item["estado"]
        marca = ""
        if estado == "atipica":
            marca = "<-- ATÍPICA"
        elif estado == "ilegible":
            marca = "<-- ILEGIBLE"
        filas.append((
            fila.get("numero_factura", "?"),
            fila.get("fecha", "?"),
            fila.get("codigo_producto", "?"),
            fila.get("cantidad", "?"),
            fila.get("total", "?"),
            marca,
        ))
    _tabla(
        ["Factura", "Fecha", "Producto", "Cant.", "Total", "Observación"],
        filas,
        ["<", "<", "<", ">", ">", "<"],
    )
    print(f"\nTotal de filas: {len(clasificadas)}")
def mostrar_alertas(reporte):
    print()
    print("ALERTAS DE INVENTARIO")
    print(_linea("-"))
    print(f"Total de productos:     {reporte['total_productos']}")
    print(f"Disponibles:            {reporte['productos_disponibles']}")
    print(f"Con stock bajo:         {reporte['productos_stock_bajo']}")
    print(f"Agotados:               {reporte['productos_agotados']}")
    print()
    if not reporte["alertas"]:
        print("No hay alertas: todos los productos tienen stock suficiente.")
        return
    for alerta in reporte["alertas"]:
        tipo = "AGOTADO" if alerta["tipo_alerta"] == "agotado" else "STOCK BAJO"
        print(f"  [{tipo}] {alerta['mensaje']}")
def mostrar_reporte_calidad(reporte_inventario, reporte_ventas):
    print()
    print("REPORTE DE CALIDAD DE DATOS")
    print(_linea("="))
    print("INVENTARIO")
    print(_linea("-"))
    print(f"Filas leídas:            {reporte_inventario['total_filas_leidas']}")
    print(f"Registros corregidos:    {reporte_inventario['registros_corregidos']}")
    print(f"Registros descartados:   {reporte_inventario['registros_descartados']}")
    print(f"Registros marcados:      {reporte_inventario['registros_marcados']}")
    print(f"Duplicados detectados:   {reporte_inventario['duplicados_detectados']}")
    print(f"Duplicados consolidados: {reporte_inventario.get('duplicados_consolidados', 0)}")
    print()
    print("VENTAS")
    print(_linea("-"))
    print(f"Filas leídas:   {reporte_ventas['total_ventas_leidas']}")
    print(f"Válidas:        {reporte_ventas['ventas_validas']}")
    print(f"Marcadas:       {reporte_ventas['ventas_marcadas']}")
    print(f"Ilegibles:      {reporte_ventas['ventas_ilegibles']}")
    mensajes = reporte_inventario.get("mensajes", []) + reporte_ventas.get("mensajes", [])
    if mensajes:
        print()
        print("DETALLE DE OBSERVACIONES")
        print(_linea("-"))
        for mensaje in mensajes:
            print(f"  - {mensaje}")
def mostrar_rutas_graficos(rutas):
    print()
    print("GRÁFICOS GENERADOS")
    print(_linea("-"))
    for ruta in rutas:
        print(f"  {ruta}")