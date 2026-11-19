from datetime import date
from modelo.venta import venta
from modelo import persistencia
from controlador import inventario_ctrl
IMPUESTO = 0.13
def _siguiente_numero_factura(filas):
    numeros = []
    for fila in filas:
        try:
            numeros.append(int(fila.get("numero_factura", 0)))
        except (TypeError, ValueError):
            continue
    return max(numeros, default=0) + 1
def preparar_linea(codigo, cantidad, lineas):
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    producto = inventario_ctrl.buscar_producto(productos, codigo)
    if producto is None:
        raise ValueError(f"No existe un producto con el codigo {codigo}.")
    cantidad = inventario_ctrl._a_entero(cantidad)
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser un entero mayor que cero.")
    ya_pedido = sum(l["cantidad"] for l in lineas if l["codigo"] == producto["codigo"])
    if producto["stock"] - ya_pedido < cantidad:
        raise ValueError(
            f"Stock insuficiente de '{producto['nombre']}': "
            f"disponible {producto['stock'] - ya_pedido}."
        )
    subtotal = round(producto["precio_venta"] * cantidad, 2)
    return {
        "codigo": producto["codigo"],
        "nombre": producto["nombre"],
        "precio_unitario": producto["precio_venta"],
        "cantidad": cantidad,
        "subtotal": subtotal,
        "impuestos": round(subtotal * IMPUESTO, 2),
        "total": round(subtotal * (1 + IMPUESTO), 2),
    }
def registrar_venta(lineas):
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    for linea in lineas:
        producto = inventario_ctrl.buscar_producto(productos, linea["codigo"])
        if producto is None:
            raise ValueError(f"El producto {linea['codigo']} ya no existe.")
        if producto["stock"] < linea["cantidad"]:
            raise ValueError(
                f"Stock insuficiente de '{producto['nombre']}' "
                f"(quedan {producto['stock']})."
            )
    filas = persistencia.cargar_ventas()
    subtotal = round(sum(l["subtotal"] for l in lineas), 2)
    impuestos = round(sum(l["impuestos"] for l in lineas), 2)
    venta = venta(
        numero_factura=_siguiente_numero_factura(filas),
        fecha=date.today().isoformat(),
        lineas=lineas,
        subtotal=subtotal,
        impuestos=impuestos,
        total=round(subtotal + impuestos, 2),
    )
    for linea in lineas:
        producto = inventario_ctrl.buscar_producto(productos, linea["codigo"])
        producto["stock"] -= linea["cantidad"]
    persistencia.guardar_inventario(productos)
    filas.extend(venta.a_filas())
    persistencia.guardar_ventas(filas)
    return venta
def clasificar_ventas():
    filas = persistencia.cargar_ventas()
    clasificadas = []
    for fila in filas:
        estado = "valida"
        try:
            int(fila.get("numero_factura", ""))
            int(fila.get("cantidad", ""))
            float(fila.get("total", ""))
            if float(fila.get("total", 0)) <= 0:
                estado = "atipica"
        except (TypeError, ValueError):
            estado = "ilegible"
        clasificadas.append({"fila": fila, "estado": estado})
    return clasificadas
def buscar_factura(numero):
    numero = str(numero).strip()
    filas = []
    for item in clasificar_ventas():
        if str(item["fila"].get("numero_factura", "")).strip() == numero:
            filas.append(item["fila"])
    return filas
def consultar_ventas_dia(fecha=None):
    fecha = str(fecha).strip() if fecha else date.today().isoformat()
    filas = []
    for item in clasificar_ventas():
        if str(item["fila"].get("fecha", "")).startswith(fecha):
            filas.append(item["fila"])
    return filas
def reporte_calidad_ventas():
    clasificadas = clasificar_ventas()
    return {
        "total_ventas_leidas": len(clasificadas),
        "ventas_validas": sum(1 for c in clasificadas if c["estado"] == "valida"),
        "ventas_marcadas": sum(1 for c in clasificadas if c["estado"] == "atipica"),
        "ventas_ilegibles": sum(1 for c in clasificadas if c["estado"] == "ilegible"),
        "mensajes": [
            f"Factura {c['fila'].get('numero_factura', '?')}: registro {c['estado']}."
            for c in clasificadas
            if c["estado"] != "valida"
        ],
    }