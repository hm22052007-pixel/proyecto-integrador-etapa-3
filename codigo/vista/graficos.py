import os
import matplotlib.pyplot as plt
def _preparar_carpeta(ruta):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
def _guardar(figura, ruta):
    _preparar_carpeta(ruta)
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
def grafico_stock(productos, ruta):
    nombres = [p.nombre for p in productos]
    actuales = [p.stock for p in productos]
    minimos = [p.stock_minimo for p in productos]
    colores = [
        "red" if p.stock == 0
        else "orange" if p.stock <= p.stock_minimo
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
    _guardar(figura, ruta)
    return figura
def grafico_ventas_por_producto(totales, ruta):
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
    _guardar(figura, ruta)
    return figura
def grafico_ventas_por_factura(clasificadas, ruta):
    facturas = []
    montos = []
    for item in clasificadas:
        if item["estado"] == "ilegible":
            continue
        try:
            facturas.append(str(item["fila"].get("numero_factura", "?")))
            montos.append(float(item["fila"].get("total", 0)))
        except (TypeError, ValueError):
            continue
    figura, eje = plt.subplots(figsize=(8, 5))
    if montos:
        eje.plot(facturas, montos, marker="o", color="darkgreen")
        eje.set_title("Monto por factura")
        eje.set_xlabel("Número de factura")
        eje.set_ylabel("Total (₡)")
        eje.grid(alpha=0.3)
    else:
        eje.text(0.5, 0.5, "No hay facturas para graficar", ha="center", va="center")
        eje.set_axis_off()
    _guardar(figura, ruta)
    return figura
def grafico_alertas(reporte, ruta):
    etiquetas = ["Disponibles", "Stock bajo", "Agotados"]
    valores = [
        reporte["productos_disponibles"],
        reporte["productos_stock_bajo"],
        reporte["productos_agotados"],
    ]
    figura, eje = plt.subplots(figsize=(6, 5))
    eje.bar(etiquetas, valores, color=["green", "orange", "red"])
    eje.set_title("Estado del inventario")
    eje.set_ylabel("Cantidad de productos")
    eje.grid(axis="y", alpha=0.3)
    _guardar(figura, ruta)
    return figura
def mostrar_todos(figuras):
    plt.show()
def cerrar_todos(figuras):
    for figura in figuras:
        plt.close(figura)