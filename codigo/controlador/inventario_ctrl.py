"""CONTROLADOR - Inventario: limpieza de datos, consultas y altas."""

from datetime import datetime

from modelo.producto import Producto
from modelo import persistencia


# Valores que se utilizan cuando un campo obligatorio viene vacío o inválido.
VALORES_POR_DEFECTO = {
    "nombre": "Producto sin nombre",
    "categoria": "Sin categoría",
    "stock": 0,
    "stock_minimo": 10,
    "precio_compra": 0.0,
    "precio_venta": 0.0,
}


def _esta_vacio(valor):
    """Indica si un dato viene vacío o contiene solamente espacios."""
    return valor is None or str(valor).strip() == ""


def _convertir_entero(valor, valor_defecto):
    """Convierte un dato a entero no negativo."""
    try:
        numero = int(str(valor).strip())
        if numero < 0:
            return valor_defecto, True
        return numero, False
    except (TypeError, ValueError):
        return valor_defecto, True


def _convertir_decimal(valor, valor_defecto):
    """Convierte un dato a decimal válido y no negativo."""
    try:
        numero = float(str(valor).strip())
        if numero < 0 or numero != numero or numero in (float("inf"), float("-inf")):
            return valor_defecto, True
        return numero, False
    except (TypeError, ValueError):
        return valor_defecto, True


def limpiar_registro(fila, numero_fila):
    """Limpia una fila del CSV y devuelve sus resultados."""
    mensajes = []
    codigo = str(fila.get("codigo") or "").strip()

    if not codigo:
        mensajes.append(
            f"Fila {numero_fila}: registro descartado porque no tiene código."
        )
        return None, False, False, True, mensajes

    producto = {"codigo": codigo}
    corregido = False
    marcado = False

    for campo in ("nombre", "categoria"):
        dato = fila.get(campo)
        if _esta_vacio(dato):
            producto[campo] = VALORES_POR_DEFECTO[campo]
            corregido = True
            mensajes.append(
                f"Fila {numero_fila} ({codigo}): falta {campo}; "
                f"se asignó '{producto[campo]}'."
            )
        else:
            producto[campo] = str(dato).strip()

    # La fecha es opcional: vacía significa que el producto no tiene vencimiento.
    fecha = fila.get("fecha_vencimiento")
    producto["fecha_vencimiento"] = "" if _esta_vacio(fecha) else str(fecha).strip()

    for campo in ("stock", "stock_minimo"):
        dato = fila.get(campo)
        if campo == "stock" and not _esta_vacio(dato):
            try:
                valor = int(str(dato).strip())
                invalido = False
            except (TypeError, ValueError):
                valor, invalido = VALORES_POR_DEFECTO[campo], True
        else:
            valor, invalido = _convertir_entero(
                dato, VALORES_POR_DEFECTO[campo]
            )

        producto[campo] = valor
        if invalido or _esta_vacio(dato):
            corregido = True
            mensajes.append(
                f"Fila {numero_fila} ({codigo}): {campo} vacío o inválido; "
                f"se asignó {valor}."
            )

    for campo in ("precio_compra", "precio_venta"):
        dato = fila.get(campo)
        valor, invalido = _convertir_decimal(
            dato, VALORES_POR_DEFECTO[campo]
        )
        producto[campo] = valor
        if invalido or _esta_vacio(dato):
            corregido = True
            mensajes.append(
                f"Fila {numero_fila} ({codigo}): {campo} vacío o inválido; "
                f"se asignó {valor:.2f}."
            )

    # Los valores atípicos se conservan para que el encargado los pueda revisar.
    if producto["stock"] < 0:
        marcado = True
        mensajes.append(
            f"Fila {numero_fila} ({codigo}): cantidad negativa; "
            "se marcó para revisión."
        )

    if producto["precio_venta"] < producto["precio_compra"]:
        marcado = True
        mensajes.append(
            f"Fila {numero_fila} ({codigo}): el precio de venta es menor "
            "que el precio de compra; se marcó para revisión."
        )

    return producto, corregido, marcado, False, mensajes


def procesar_filas(filas, consolidar_duplicados=True):
    """Revisa filas del CSV, corrige vacíos y detecta códigos repetidos."""
    productos_por_codigo = {}
    corregidos = 0
    descartados = 0
    marcados = 0
    duplicados = 0
    mensajes = []

    for numero_fila, fila in enumerate(filas, start=2):
        datos, corregido, marcado, descartado, avisos = limpiar_registro(
            fila, numero_fila
        )
        mensajes.extend(avisos)

        if descartado:
            descartados += 1
            continue

        if corregido:
            corregidos += 1
        if marcado:
            marcados += 1

        codigo = datos["codigo"]
        if codigo not in productos_por_codigo:
            productos_por_codigo[codigo] = datos
        else:
            duplicados += 1
            if consolidar_duplicados:
                productos_por_codigo[codigo]["stock"] += datos["stock"]
                mensajes.append(
                    f"Se consolidó el código {codigo}: se sumaron "
                    f"{datos['stock']} unidades al stock."
                )
            else:
                marcados += 1
                mensajes.append(
                    f"Fila {numero_fila}: el código {codigo} está duplicado; "
                    "se conservó el primer registro y se marcó la repetición."
                )

    lista_productos = [
        Producto.from_dict(datos) for datos in productos_por_codigo.values()
    ]

    reporte = {
        "total_filas_leidas": len(filas),
        "registros_corregidos": corregidos,
        "registros_descartados": descartados,
        "registros_marcados": marcados,
        "duplicados_detectados": duplicados,
        "duplicados_consolidados": duplicados if consolidar_duplicados else 0,
        "mensajes": mensajes,
    }
    return lista_productos, reporte


def cargar_inventario_limpio(consolidar_duplicados=True, guardar=True):
    """Carga el inventario, limpia los datos y guarda los cambios si se solicita."""
    filas = persistencia.cargar_inventario()
    productos, reporte = procesar_filas(filas, consolidar_duplicados)

    if guardar:
        persistencia.guardar_inventario(productos)

    return productos, reporte


def buscar_producto(productos, codigo):
    """Devuelve el producto con ese código, o None si no existe."""
    buscado = str(codigo or "").strip()
    return next((p for p in productos if p.codigo == buscado), None)


def filtrar_productos(productos, categoria=None, precio_min=None,
                      precio_max=None, estado_stock=None):
    """Filtra por categoría, precio de venta y estado del inventario.

    Los estados disponibles son: disponible, agotado y bajo.
    """
    resultado = list(productos)

    if categoria and categoria.strip().lower() not in ("todas", "todos"):
        resultado = [
            p for p in resultado
            if p.categoria.lower() == categoria.strip().lower()
        ]

    if precio_min not in (None, ""):
        try:
            minimo = float(precio_min)
        except (TypeError, ValueError):
            raise ValueError("El precio mínimo debe ser un número.")
        resultado = [p for p in resultado if p.precio_venta >= minimo]

    if precio_max not in (None, ""):
        try:
            maximo = float(precio_max)
        except (TypeError, ValueError):
            raise ValueError("El precio máximo debe ser un número.")
        resultado = [p for p in resultado if p.precio_venta <= maximo]

    if estado_stock == "disponible":
        resultado = [p for p in resultado if p.stock > p.stock_minimo]
    elif estado_stock == "agotado":
        resultado = [p for p in resultado if p.stock <= 0]
    elif estado_stock == "bajo":
        resultado = [p for p in resultado if 0 < p.stock <= p.stock_minimo]
    elif estado_stock not in (None, ""):
        raise ValueError("El estado debe ser disponible, agotado o bajo.")

    return resultado


def ordenar_productos(productos, criterio="nombre", orden="ascendente"):
    """Ordena los productos por nombre, stock o precio de venta."""
    if criterio == "nombre":
        clave = lambda p: p.nombre.lower()
    elif criterio == "stock":
        clave = lambda p: p.stock
    elif criterio == "precio":
        clave = lambda p: p.precio_venta
    else:
        raise ValueError("El criterio debe ser nombre, stock o precio.")

    if orden not in ("ascendente", "descendente"):
        raise ValueError("El orden debe ser ascendente o descendente.")

    return sorted(productos, key=clave, reverse=(orden == "descendente"))


def generar_reporte_calidad(datos_calidad):
    """Devuelve el resumen de calidad de datos como diccionario.

    La vista (consola.py) es la encargada de darle formato para mostrarlo.
    """
    return {
        "total_filas_leidas": datos_calidad["total_filas_leidas"],
        "registros_corregidos": datos_calidad["registros_corregidos"],
        "registros_descartados": datos_calidad["registros_descartados"],
        "registros_marcados": datos_calidad["registros_marcados"],
        "duplicados_detectados": datos_calidad["duplicados_detectados"],
    }


def agregar_producto(codigo, nombre, categoria, stock, stock_minimo,
                     precio_compra, precio_venta, fecha_vencimiento=""):
    """Valida y registra un producto nuevo. Devuelve el Producto."""
    codigo = str(codigo or "").strip()
    nombre = str(nombre or "").strip()
    categoria = str(categoria or "").strip()
    if not (codigo and nombre and categoria):
        raise ValueError("Código, nombre y categoría son obligatorios.")
    try:
        stock = int(stock)
        stock_minimo = int(stock_minimo)
        precio_compra = float(precio_compra)
        precio_venta = float(precio_venta)
    except (TypeError, ValueError):
        raise ValueError("Stock y precios deben ser números.")
    if stock < 0 or stock_minimo < 0 or precio_compra <= 0 or precio_venta <= 0:
        raise ValueError(
            "El stock no puede ser negativo y los precios deben ser mayores que cero."
        )
    if precio_venta < precio_compra:
        raise ValueError("El precio de venta no puede ser menor que el de compra.")
    fecha = str(fecha_vencimiento or "").strip()
    if fecha:
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
    productos, _ = cargar_inventario_limpio(guardar=False)
    if any(p.codigo.lower() == codigo.lower() for p in productos):
        raise ValueError(f"Ya existe un producto con el código '{codigo}'.")
    nuevo = Producto(codigo, nombre, categoria, stock, stock_minimo,
                     precio_compra, precio_venta, fecha)
    productos.append(nuevo)
    persistencia.guardar_inventario(productos)
    return nuevo


def actualizar_stock(codigo, cantidad):
    """Suma (o resta, si es negativa) unidades al stock. Devuelve el Producto."""
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero.")
    if cantidad == 0:
        raise ValueError("La cantidad no puede ser cero.")
    productos, _ = cargar_inventario_limpio(guardar=False)
    producto = buscar_producto(productos, codigo)
    if producto is None:
        raise ValueError(f"No existe un producto con el código '{codigo}'.")
    if producto.stock + cantidad < 0:
        raise ValueError("El stock no puede quedar negativo.")
    producto.stock += cantidad
    persistencia.guardar_inventario(productos)
    return producto
