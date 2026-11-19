import os
import matplotlib
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
    nombres = [p["nombre"] for p in productos]
    actuales = [max(p["stock"], 0) for p in productos]
    minimos = [max(p["stock_minimo"], 0) for p in productos]
    colores = [
        "red" if p["stock"] <= 0
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
        label="Stock minimo", color="gray",
    )
    eje.bar_label(barras, padding=2)
    eje.set_ylim(bottom=0)
    eje.set_title("Stock actual vs. stock minimo")
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
        eje.set_xlabel("Producto")
        eje.set_ylabel("Monto vendido")
        eje.tick_params(axis="x", rotation=20)
        eje.grid(axis="y", alpha=0.3)
    else:
        eje.text(0.5, 0.5, "No hay ventas registradas", ha="center", va="center")
        eje.set_axis_off()
    _guardar(figura, ruta)
    return figura
def mostrar_todos(figuras):
    plt.show()
def cerrar_todos(figuras):
    for figura in figuras:
        plt.close(figura)