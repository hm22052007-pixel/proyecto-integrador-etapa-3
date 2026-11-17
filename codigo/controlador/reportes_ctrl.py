"""CONTROLADOR - Reportes y alertas de inventario."""

from vista import graficos
from controlador import inventario_ctrl, ventas_ctrl
from modelo import persistencia


def generar_reporte_grafico(productos=None, ventas=None, mostrar=True):
    """Prepara los datos y genera los gráficos. Devuelve la lista de rutas .png.
    Si no se le pasan los datos, los carga desde el disco."""
    if productos is None:
        productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    if ventas is None:
        ventas = persistencia.cargar_ventas()
    totales, _ = ventas_ctrl.obtener_ventas_por_categoria(productos, ventas)
    criticos = ventas_ctrl.obtener_stock_critico(productos)
    return graficos.generar_reportes_graficos(totales, criticos, mostrar=mostrar)


def generar_alertas_stock(productos):
    """Genera avisos para los productos con stock bajo o agotado."""
    alertas = []

    for producto in productos:
        if producto.stock <= 0:
            alertas.append({
                "codigo_producto": producto.codigo,
                "tipo_alerta": "agotado",
                "mensaje": (
                    f"Producto agotado: '{producto.nombre}' "
                    f"(código {producto.codigo})."
                )
            })
        elif producto.stock <= producto.stock_minimo:
            alertas.append({
                "codigo_producto": producto.codigo,
                "tipo_alerta": "stock_bajo",
                "mensaje": (
                    f"Stock bajo: '{producto.nombre}' tiene {producto.stock} "
                    f"unidades (mínimo {producto.stock_minimo})."
                )
            })

    return alertas


def generar_reporte_stock(productos):
    """Resume cuántos productos están disponibles, bajos o agotados."""
    alertas = generar_alertas_stock(productos)

    return {
        "total_productos": len(productos),
        "productos_disponibles": sum(
            p.stock > p.stock_minimo for p in productos
        ),
        "productos_stock_bajo": sum(
            0 < p.stock <= p.stock_minimo for p in productos
        ),
        "productos_agotados": sum(p.stock <= 0 for p in productos),
        "alertas": alertas,
    }
