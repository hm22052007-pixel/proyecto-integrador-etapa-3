from modelo.producto import Producto
from modelo import persistencia
CAMPOS_NUMERICOS = ["stock", "stock_minimo", "precio_compra", "precio_venta"]
CAMPOS_TEXTO = ["codigo", "nombre", "categoria"]
def _esta_vacio(valor):
    return valor is None or str(valor).strip() == ""
def _a_entero(valor, defecto=0):
    try:
        return int(float(str(valor).strip()))
    except (TypeError, ValueError):
        return defecto
def _a_decimal(valor, defecto=0.0):
    try:
        return round(float(str(valor).strip()), 2)
    except (TypeError, ValueError):
        return defecto
def _normalizar_fila(fila):
    producto = {}
    corregido = False
    for campo in CAMPOS_TEXTO:
        original = fila.get(campo, "")
        limpio = str(original).strip() if original is not None else ""
        if campo == "codigo":
            limpio = limpio.upper()
        if limpio != original:
            corregido = True
        producto[campo] = limpio
    for campo in CAMPOS_NUMERICOS:
        original = fila.get(campo)
        if campo in ("stock", "stock_minimo"):
            valor = _a_entero(original, defecto=0)
        else:
            valor = _a_decimal(original, defecto=0.0)
        if str(valor) != str(original).strip():
            corregido = True
        producto[campo] = valor
    fecha = fila.get("fecha_vencimiento")
    producto["fecha_vencimiento"] = "" if _esta_vacio(fecha) else str(fecha).strip()
    return producto, corregido
def _clave_duplicado(producto):
    return producto["codigo"]
def consolidar_duplicados(productos):
    consolidados = {}
    duplicados = 0
    for producto in productos:
        clave = _clave_duplicado(producto)
        if clave in consolidados:
            consolidados[clave]["stock"] += producto["stock"]
            consolidados[clave]["stock_minimo"] = max(
                consolidados[clave]["stock_minimo"], producto["stock_minimo"]
            )
            duplicados += 1
        else:
            consolidados[clave] = dict(producto)
    return list(consolidados.values()), duplicados
def cargar_inventario_limpio(guardar=True):
    filas = persistencia.cargar_inventario()
    reporte = {
        "total_filas_leidas": len(filas),
        "registros_corregidos": 0,
        "registros_descartados": 0,
        "registros_marcados": 0,
        "duplicados_detectados": 0,
        "duplicados_consolidados": 0,
        "mensajes": [],
    }
    productos = []
    for numero, fila in enumerate(filas, start=1):
        limpio, corregido = _normalizar_fila(fila)
        if corregido:
            reporte["registros_corregidos"] += 1
            reporte["mensajes"].append(f"Fila {numero}: datos corregidos.")
        if not limpio["codigo"] or not limpio["nombre"]:
            reporte["registros_descartados"] += 1
            reporte["mensajes"].append(
                f"Fila {numero}: descartada por falta de código o nombre."
            )
            continue
        if limpio["precio_venta"] < limpio["precio_compra"]:
            reporte["registros_marcados"] += 1
            reporte["mensajes"].append(
                f"Fila {numero}: el precio de venta es menor que el de compra."
            )
        if limpio["stock"] < 0:
            reporte["registros_marcados"] += 1
            reporte["mensajes"].append(f"Fila {numero}: stock negativo.")
        productos.append(limpio)
    reporte["duplicados_detectados"] = len(productos) - len(
        {p["codigo"] for p in productos}
    )
    productos, consolidados = consolidar_duplicados(productos)
    reporte["duplicados_consolidados"] = consolidados
    if consolidados:
        reporte["mensajes"].append(f"Se consolidaron {consolidados} duplicados.")
    if guardar:
        persistencia.guardar_inventario(productos)
    return productos, reporte
def buscar_producto(productos, codigo):
    codigo = str(codigo).strip().upper()
    for producto in productos:
        if producto["codigo"] == codigo:
            return producto
    return None
def agregar_producto(codigo, nombre, categoria, stock, stock_minimo,
                     precio_compra, precio_venta, fecha_vencimiento=""):
    productos, _ = cargar_inventario_limpio(guardar=False)
    codigo = str(codigo).strip().upper()
    if not codigo or not str(nombre).strip():
        raise ValueError("El código y el nombre son obligatorios.")
    if buscar_producto(productos, codigo) is not None:
        raise ValueError(
            f"Ya existe un producto con el código {codigo}. "
            "Use la opción 2 para sumarle unidades."
        )
    producto = Producto(
        codigo=codigo,
        nombre=str(nombre).strip(),
        categoria=str(categoria).strip() or "Sin categoría",
        stock=_a_entero(stock),
        stock_minimo=_a_entero(stock_minimo),
        precio_compra=_a_decimal(precio_compra),
        precio_venta=_a_decimal(precio_venta),
        fecha_vencimiento="" if _esta_vacio(fecha_vencimiento) else str(fecha_vencimiento).strip(),
    )
    if producto.stock < 0 or producto.stock_minimo < 0:
        raise ValueError("El stock no puede ser negativo.")
    if producto.precio_compra < 0 or producto.precio_venta < 0:
        raise ValueError("Los precios no pueden ser negativos.")
    if producto.precio_venta < producto.precio_compra:
        raise ValueError("El precio de venta no puede ser menor que el de compra.")
    productos.append(producto.to_dict())
    persistencia.guardar_inventario(productos)
    return producto
def actualizar_stock(codigo, cantidad):
    productos, _ = cargar_inventario_limpio(guardar=False)
    producto = buscar_producto(productos, codigo)
    if producto is None:
        raise ValueError(f"No existe un producto con el código {codigo}.")
    cantidad = _a_entero(cantidad)
    if cantidad == 0:
        raise ValueError("La cantidad debe ser distinta de cero.")
    if producto["stock"] + cantidad < 0:
        raise ValueError(
            f"No hay suficientes unidades: stock actual {producto['stock']}."
        )
    producto["stock"] += cantidad
    persistencia.guardar_inventario(productos)
    return Producto.from_dict(producto)
def filtrar_productos(productos, categoria=None, precio_min=None, precio_max=None, estado=None):
    resultado = []
    for producto in productos:
        if categoria and producto["categoria"].lower() != str(categoria).strip().lower():
            continue
        if precio_min is not None and producto["precio_venta"] < _a_decimal(precio_min):
            continue
        if precio_max is not None and producto["precio_venta"] > _a_decimal(precio_max):
            continue
        if estado:
            estado = estado.lower()
            if estado == "agotado" and producto["stock"] > 0:
                continue
            if estado == "bajo" and not (0 < producto["stock"] <= producto["stock_minimo"]):
                continue
            if estado == "disponible" and producto["stock"] <= producto["stock_minimo"]:
                continue
        resultado.append(producto)
    return resultado
def ordenar_productos(productos, criterio="nombre", orden="ascendente"):
    claves = {
        "nombre": lambda p: p["nombre"].lower(),
        "stock": lambda p: p["stock"],
        "precio": lambda p: p["precio_venta"],
    }
    if criterio not in claves:
        raise ValueError("Criterio de orden no válido: use nombre, stock o precio.")
    descendente = str(orden).strip().lower().startswith("desc")
    return sorted(productos, key=claves[criterio], reverse=descendente)
def generar_reporte_calidad(reporte):
    productos, _ = cargar_inventario_limpio(guardar=False)
    reporte = dict(reporte)
    reporte["total_productos"] = len(productos)
    reporte["productos_con_stock_bajo"] = sum(
        1 for p in productos if 0 < p["stock"] <= p["stock_minimo"]
    )
    reporte["productos_agotados"] = sum(1 for p in productos if p["stock"] == 0)
    reporte["valor_total_inventario"] = round(
        sum(p["stock"] * p["precio_compra"] for p in productos), 2
    )
    return reporte