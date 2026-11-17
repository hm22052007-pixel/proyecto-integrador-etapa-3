"""CONTROLADOR - Ventas: facturación, registro y datos para los gráficos."""

from datetime import datetime

from modelo import persistencia
from modelo.venta import Venta
from controlador import inventario_ctrl

# IVA de Costa Rica (coincide con los datos de ventas.csv: 325 / 2500 = 13%).
TASA_IMPUESTO = 0.13
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


#
# Facturación
#
def calcular_montos(precio_unitario, cantidad):
    """Devuelve (subtotal, impuestos, total) redondeados a 2 decimales."""
    subtotal = round(precio_unitario * cantidad, 2)
    impuestos = round(subtotal * TASA_IMPUESTO, 2)
    total = round(subtotal + impuestos, 2)
    return subtotal, impuestos, total


def generar_numero_factura(ventas_crudas):
    """Siguiente número consecutivo según las ventas ya registradas.

    Ignora filas con número ilegible para no fallar con datos sucios."""
    mayor = 0
    for fila in ventas_crudas:
        try:
            mayor = max(mayor, int(str(fila.get("numero_factura", "")).strip()))
        except ValueError:
            continue
    return mayor + 1


def _validar_cantidad(cantidad):
    """Convierte la cantidad a entero positivo o lanza ValueError."""
    try:
        numero = int(str(cantidad).strip())
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero.")
    if numero <= 0:
        raise ValueError("La cantidad debe ser mayor a cero.")
    return numero


def _formatear_fila_venta(venta):
    """Convierte la venta a diccionario y deja los montos con 2 decimales."""
    fila = venta.to_dict()
    for campo in ("subtotal", "impuestos", "total"):
        fila[campo] = f"{fila[campo]:.2f}"
    return fila


def preparar_linea(codigo_producto, cantidad, lineas_actuales):
    """Valida un producto y devuelve la línea lista para la factura."""
    codigo = str(codigo_producto or "").strip()
    if not codigo:
        raise ValueError("Debe indicar el código del producto.")
    cantidad = _validar_cantidad(cantidad)

    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    producto = inventario_ctrl.buscar_producto(productos, codigo)
    if producto is None:
        raise ValueError(f"No existe un producto con el código '{codigo}'.")
    if producto.precio_venta <= 0:
        raise ValueError(
            f"El producto '{producto.nombre}' no tiene un precio de venta válido."
        )

    ya_agregado = sum(
        l["cantidad"] for l in lineas_actuales if l["codigo"] == producto.codigo
    )
    disponible = producto.stock - ya_agregado
    if cantidad > disponible:
        raise ValueError(
            f"Stock insuficiente de '{producto.nombre}': "
            f"disponible {disponible}, solicitado {cantidad}."
        )

    return {
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "precio_unitario": producto.precio_venta,
        "cantidad": cantidad,
        "subtotal": round(cantidad * producto.precio_venta, 2),
    }


def registrar_venta(lineas):
    """Registra una venta con una o varias líneas y descuenta el stock."""

    if not lineas:
        raise ValueError("La venta no tiene productos.")

    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)

    # 1. Validar contra el inventario actual y calcular montos por línea
    for linea in lineas:
        producto = inventario_ctrl.buscar_producto(productos, linea["codigo"])
        if producto is None:
            raise ValueError(f"El producto '{linea['codigo']}' ya no existe.")
        if linea["cantidad"] > producto.stock:
            raise ValueError(
                f"Stock insuficiente de '{producto.nombre}': "
                f"disponible {producto.stock}, solicitado {linea['cantidad']}."
            )
        linea["nombre"] = producto.nombre
        linea["precio_unitario"] = producto.precio_venta
        linea["subtotal"] = round(linea["cantidad"] * producto.precio_venta, 2)

    # 2. Totales de la factura
    subtotal = round(sum(l["subtotal"] for l in lineas), 2)
    impuestos = round(subtotal * TASA_IMPUESTO, 2)
    total = round(subtotal + impuestos, 2)

    # 3. Repartir el IVA entre las líneas, para que el csv cuadre
    for linea in lineas:
        proporcion = linea["subtotal"] / subtotal if subtotal else 0
        linea["impuestos"] = round(impuestos * proporcion, 2)
        linea["total"] = round(linea["subtotal"] + linea["impuestos"], 2)

    # 4. Descontar stock en memoria
    for linea in lineas:
        producto = inventario_ctrl.buscar_producto(productos, linea["codigo"])
        producto.stock -= linea["cantidad"]

    # 5. Armar la venta
    ventas_crudas = persistencia.cargar_ventas()
    venta = Venta(
        numero_factura=generar_numero_factura(ventas_crudas),
        fecha=datetime.now().strftime(FORMATO_FECHA),
        lineas=lineas,
        subtotal=subtotal,
        impuestos=impuestos,
        total=total,
    )

    # 6. Guardar: si falla la venta, se devuelve el stock (igual que antes)
    persistencia.guardar_inventario(productos)
    try:
        persistencia.guardar_ventas(ventas_crudas + venta.a_filas())
    except Exception:
        for linea in lineas:
            producto = inventario_ctrl.buscar_producto(productos, linea["codigo"])
            producto.stock += linea["cantidad"]
        persistencia.guardar_inventario(productos)
        raise
    return venta


#
# Datos para los gráficos
#
def _venta_valida(fila):
    try:
        cantidad = int(str(fila["cantidad"]).strip())
        total = float(str(fila["total"]).strip())
        codigo = str(fila["codigo_producto"].strip())
    except (KeyError, TypeError, ValueError):
        return None
    if cantidad <= 0 or total <= 0 or not codigo:
        return None
    return codigo, total


def obtener_ventas_por_categoria(productos, ventas_crudas):
    categoria_de = {p.codigo: p.categoria for p in productos}

    totales = {}
    descartadas = 0
    for fila in ventas_crudas:
        valida = _venta_valida(fila)
        if valida is None:
            descartadas += 1
            continue
        codigo, total = valida
        categoria = categoria_de.get(codigo, "Sin categoría")
        totales[categoria] = totales.get(categoria, 0.0) + total

    ordenado = dict(sorted(totales.items(), key=lambda par: par[1], reverse=True))
    return ordenado, descartadas


def obtener_todas_las_categorias(productos):
    return sorted({p.categoria for p in productos} | {"Sin categoría"})


def obtener_stock_critico(productos):
    criticos = [
        {
            "codigo": p.codigo,
            "nombre": p.nombre,
            "stock": p.stock,
            "stock_minimo": p.stock_minimo,
        }
        for p in productos if p.stock <= p.stock_minimo
    ]
    criticos.sort(key=lambda d: d["stock"] - d["stock_minimo"])
    return criticos


def obtener_ventas():
    """Devuelve las ventas del CSV tal como están (las lee el modelo)."""
    return persistencia.cargar_ventas()


def clasificar_ventas(filas=None):
    """Marca cada venta como 'valida', 'atipica' (cantidad o total <= 0) o 'ilegible'."""
    if filas is None:
        filas = obtener_ventas()
    resultado = []
    for fila in filas:
        try:
            cantidad = int(str(fila["cantidad"]).strip())
            total = float(str(fila["total"]).strip())
        except (KeyError, TypeError, ValueError):
            estado = "ilegible"
        else:
            estado = "atipica" if (cantidad <= 0 or total <= 0) else "valida"
        resultado.append({"fila": fila, "estado": estado})
    return resultado


def reporte_calidad_ventas(filas=None):
    """Resume cuántas ventas son válidas, atípicas (marcadas) e ilegibles."""
    clasificadas = clasificar_ventas(filas)
    mensajes = []
    for numero, item in enumerate(clasificadas, start=2):
        factura = str(item["fila"].get("numero_factura") or "?").strip()
        if item["estado"] == "atipica":
            mensajes.append(
                f"Fila {numero} (factura {factura}): cantidad o total menor o "
                "igual a cero; se marcó para revisión."
            )
        elif item["estado"] == "ilegible":
            mensajes.append(
                f"Fila {numero} (factura {factura}): datos ilegibles o incompletos."
            )
    return {
        "total_ventas_leidas": len(clasificadas),
        "ventas_validas": sum(i["estado"] == "valida" for i in clasificadas),
        "ventas_marcadas": sum(i["estado"] == "atipica" for i in clasificadas),
        "ventas_ilegibles": sum(i["estado"] == "ilegible" for i in clasificadas),
        "mensajes": mensajes,
    }
