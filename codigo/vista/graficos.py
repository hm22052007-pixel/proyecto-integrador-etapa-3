"""VISTA - Gráficos con matplotlib."""

import os
import matplotlib.pyplot as plt

CARPETA_VISTA = os.path.dirname(os.path.abspath(__file__))
CARPETA_CODIGO = os.path.dirname(CARPETA_VISTA)
CARPETA_EVIDENCIAS = os.path.join(os.path.dirname(CARPETA_CODIGO), "evidencias")

# Paleta única para todo el reporte
PALETA_CATEGORIAS = [
    "#0072B2", "#E69F00", "#009E73", "#CC79A7",
    "#56B4E9", "#D55E00", "#F0E442", "#7F7F7F",
]
COLOR_STOCK_ACTUAL = "#0072B2"
COLOR_STOCK_MINIMO = "#D55E00"
COLOR_TEXTO = "#222222"
COLOR_CUADRICULA = "#DDDDDD"
MONEDA = "₡"


# Utilidades
def _colores_por_categoria(categorias):
    """Un color fijo por categoría, igual en todos los gráficos."""
    return {
        cat: PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)]
        for i, cat in enumerate(categorias)
    }


def _miles(valor):
    return f"{MONEDA}{valor:,.0f}"


def _color_de_texto_sobre(rgba):
    """Blanco sobre fondos oscuros y negro sobre fondos claros (contraste)."""
    r, g, b = rgba[:3]
    luminancia = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return COLOR_TEXTO if luminancia > 0.5 else "white"


def _estilo_ejes(ax, eje_cuadricula):
    ax.set_axisbelow(True)
    ax.grid(axis=eje_cuadricula, color=COLOR_CUADRICULA, linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def _guardar(fig, nombre_archivo, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre_archivo)
    fig.savefig(ruta, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def _figura_sin_datos(titulo, mensaje):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.text(0.5, 0.5, mensaje, ha="center", va="center",
            fontsize=12, color=COLOR_TEXTO, transform=ax.transAxes)
    ax.set_axis_off()
    return fig


# Gráfico 1: ventas totales por categoría
def grafico_ventas_por_categoria(totales, carpeta=CARPETA_EVIDENCIAS):
    """Barras verticales: suma del total de ventas de cada categoría."""
    titulo = "Ventas totales por categoría de producto"
    if not totales:
        fig = _figura_sin_datos(titulo, "No hay ventas válidas para graficar.")
        return _guardar(fig, "ventas_por_categoria.png", carpeta)

    categorias = list(totales)
    valores = [totales[c] for c in categorias]
    colores = _colores_por_categoria(categorias)

    fig, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(categorias, valores,
                    color=[colores[c] for c in categorias], width=0.6)
    ax.bar_label(barras, labels=[_miles(v) for v in valores],
                 padding=3, fontsize=10, color=COLOR_TEXTO)

    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Categoría de producto")
    ax.set_ylabel(f"Total de ventas ({MONEDA}, IVA incluido)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax.set_ylim(0, max(valores) * 1.15)
    _estilo_ejes(ax, "y")

    ax.legend(barras, categorias, title="Categoría", frameon=False,
              loc="upper right")
    return _guardar(fig, "ventas_por_categoria.png", carpeta)


# Gráfico 2: stock actual vs. stock mínimo (críticos)
def grafico_stock_critico(criticos, carpeta=CARPETA_EVIDENCIAS):
    """Barras horizontales: stock actual frente al mínimo en productos críticos."""
    titulo = "Stock actual vs. stock mínimo (productos con existencias críticas)"
    if not criticos:
        fig = _figura_sin_datos(titulo, "Ningún producto tiene existencias críticas.")
        return _guardar(fig, "stock_critico.png", carpeta)

    # barh dibuja de abajo hacia arriba: se invierte para que el más crítico quede arriba.
    criticos = criticos[::-1]
    etiquetas = [f"{d['nombre']}\n({d['codigo']})" for d in criticos]
    actual = [d["stock"] for d in criticos]
    minimo = [d["stock_minimo"] for d in criticos]
    posiciones = range(len(criticos))
    alto = 0.38

    fig, ax = plt.subplots(figsize=(9, max(3.5, 1.2 * len(criticos) + 2)))
    b1 = ax.barh([p + alto / 2 for p in posiciones], actual, height=alto,
                 color=COLOR_STOCK_ACTUAL, label="Stock actual")
    b2 = ax.barh([p - alto / 2 for p in posiciones], minimo, height=alto,
                 color=COLOR_STOCK_MINIMO, label="Stock mínimo")
    ax.bar_label(b1, padding=3, fontsize=10, color=COLOR_TEXTO)
    ax.bar_label(b2, padding=3, fontsize=10, color=COLOR_TEXTO)

    ax.set_yticks(list(posiciones))
    ax.set_yticklabels(etiquetas)
    ax.axvline(0, color=COLOR_TEXTO, linewidth=0.8)
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Unidades en inventario")
    ax.set_ylabel("Producto (código)")
    _estilo_ejes(ax, "x")
    ax.legend(frameon=False, loc="lower right")

    return _guardar(fig, "stock_critico.png", carpeta)


# Gráfico 3: distribución porcentual de las ventas
def grafico_distribucion_ventas(totales, carpeta=CARPETA_EVIDENCIAS):
    """Gráfico circular: participación de cada categoría en el total vendido."""
    titulo = "Distribución porcentual de las ventas por categoría"
    if not totales:
        fig = _figura_sin_datos(titulo, "No hay ventas válidas para graficar.")
        return _guardar(fig, "distribucion_ventas.png", carpeta)

    categorias = list(totales)
    valores = [totales[c] for c in categorias]
    colores = _colores_por_categoria(categorias)
    total = sum(valores)

    fig, ax = plt.subplots(figsize=(8, 6))
    porciones, textos, autotextos = ax.pie(
        valores,
        colors=[colores[c] for c in categorias],
        autopct=lambda p: f"{p:.1f}%",
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"color": COLOR_TEXTO, "fontsize": 10},
    )
    for autotexto, color in zip(autotextos, [colores[c] for c in categorias]):
        autotexto.set_color(_color_de_texto_sobre(
            plt.matplotlib.colors.to_rgb(color)))

    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
    ax.axis("equal")
    ax.legend(
        porciones,
        [f"{c}: {_miles(v)}" for c, v in zip(categorias, valores)],
        title=f"Total vendido: {_miles(total)}",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
    )

    return _guardar(fig, "distribucion_ventas.png", carpeta)


# Reporte completo
def generar_reportes_graficos(totales, criticos, carpeta=CARPETA_EVIDENCIAS,
                              mostrar=True):
    """Genera los tres gráficos del reporte y devuelve las rutas creadas."""
    rutas = [
        grafico_ventas_por_categoria(totales, carpeta),
        grafico_stock_critico(criticos, carpeta),
        grafico_distribucion_ventas(totales, carpeta),
    ]

    if mostrar:
        for ruta in rutas:
            imagen = plt.imread(ruta)
            alto, ancho = imagen.shape[0], imagen.shape[1]
            fig, ax = plt.subplots(figsize=(ancho / 100, alto / 100))
            ax.imshow(imagen)
            ax.set_axis_off()
        plt.show()

    return rutas
