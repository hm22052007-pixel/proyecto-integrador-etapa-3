import os
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
from modelo import persistencia
from controlador import inventario_ctrl, ventas_ctrl
CARPETA_GRAFICOS = os.path.join(persistencia.CARPETA_CODIGO, "graficos")
def generar_reporte_stock(productos):
    alertas = []
    disponibles = 0
    bajos = 0
    agotados = 0
    for producto in productos:
        if producto["stock"] == 0:
            agotados += 1
            alertas.append({
                "tipo_alerta": "agotado",
                "codigo": producto["codigo"],
                "mensaje": f"{producto['nombre']} ({producto['codigo']}) está agotado.",
            })
        elif producto["stock"] <= producto["stock_minimo"]:
            bajos += 1
            alertas.append({
                "tipo_alerta": "stock_bajo",
                "codigo": producto["codigo"],
                "mensaje": (
                    f"{producto['nombre']} ({producto['codigo']}): "
                    f"quedan {producto['stock']} y el mínimo es {producto['stock_minimo']}."
                ),
            })
        else:
            disponibles += 1
    return {
        "total_productos": len(productos),
        "productos_disponibles": disponibles,
        "productos_stock_bajo": bajos,
        "productos_agotados": agotados,
        "alertas": alertas,
    }
def _grafico_stock(productos, ruta):
    nombres = [p["nombre"] for p in productos]
    actuales = [p["stock"] for p in productos]
    minimos = [p["stock_minimo"] for p in productos]
    colores = [
        "red" if p["stock"] == 0
        else "orange" if p["stock"] <= p["stock_minimo"]
        else "green"
        for p in productos
    ]
    posiciones = range(len(nombres))
    ancho = 0.4
    figura, eje = plt.subplots(figsize=(10, 5))
    barras = eje.bar(
        [x - ancho / 2 for x in posiciones], actuales, ancho,
        label="Stock actual", color=colores,
    )
    eje.bar(
        [x + ancho / 2 for x in posiciones], minimos, ancho,
        label="Stock mínimo", color="gray",
    )
    eje.bar_label(barras, padding=2)
    eje.set_title("Stock actual vs. stock mínimo")
    eje.set_xlabel("Producto")
    eje.set_ylabel("Unidades")
    eje.set_xticks(list(posiciones))
    eje.set_xticklabels(nombres, rotation=20, ha="right")
    eje.legend()
    eje.grid(axis="y", alpha=0.3)
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
    return figura
def _grafico_ventas(clasificadas, ruta):
    totales = {}
    for item in clasificadas:
        if item["estado"] == "ilegible":
            continue
        codigo = item["fila"].get("codigo_producto", "?")
        try:
            totales[codigo] = totales.get(codigo, 0) + float(item["fila"].get("total", 0))
        except (TypeError, ValueError):
            continue
    figura, eje = plt.subplots(figsize=(8, 5))
    if totales:
        eje.bar(list(totales.keys()), list(totales.values()), color="steelblue")
        eje.set_title("Total vendido por producto")
        eje.set_xlabel("Código de producto")
        eje.set_ylabel("Monto vendido (₡)")
        eje.tick_params(axis="x", rotation=20)
        eje.grid(axis="y", alpha=0.3)
    else:
        eje.text(0.5, 0.5, "No hay ventas registradas", ha="center", va="center")
        eje.set_axis_off()
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
    return figura
def generar_reporte_grafico(mostrar=False):
    productos, _ = inventario_ctrl.cargar_inventario_limpio(guardar=False)
    clasificadas = ventas_ctrl.clasificar_ventas()
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    ruta_stock = os.path.join(CARPETA_GRAFICOS, "stock_vs_minimo.png")
    ruta_ventas = os.path.join(CARPETA_GRAFICOS, "ventas_por_producto.png")
    figuras = [
        _grafico_stock(productos, ruta_stock),
        _grafico_ventas(clasificadas, ruta_ventas),
    ]
    if mostrar:
        plt.show()
    for figura in figuras:
        plt.close(figura)
    return [ruta_stock, ruta_ventas]