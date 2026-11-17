"""MODELO - Clase de la venta"""
# Nos va a ayudar a representar una venta en el sistema.


class Venta:
    def __init__(self, numero_factura, fecha, lineas, subtotal, impuestos, total):
        # numero_factura es un entero consecutivo (1, 2, 3...)
        self.numero_factura = numero_factura
        # La fecha se guarda como texto "AAAA-MM-DD HH:MM:SS".
        self.fecha = fecha
        self.lineas = lineas
        self.subtotal = subtotal
        self.impuestos = impuestos
        self.total = total

    @property
    def cantidad(self):
        """Total de unidades de la factura (suma de todas las líneas)."""
        return sum(linea["cantidad"] for linea in self.lineas)

    @property
    def codigo_producto(self):
        """Códigos de la factura separados por coma, para mostrarlos juntos."""
        return ", ".join(linea["codigo"] for linea in self.lineas)

    def to_dict(self):
        return self.a_filas()[0]

    def a_filas(self):
        return [
            {
                "numero_factura": self.numero_factura,
                "fecha": self.fecha,
                "codigo_producto": linea["codigo"],
                "cantidad": linea["cantidad"],
                "subtotal": f"{linea['subtotal']:.2f}",
                "impuestos": f"{linea['impuestos']:.2f}",
                "total": f"{linea['total']:.2f}",
            }
            for linea in self.lineas
        ]

    @classmethod
    def from_dict(cls, datos):
        """Crea una venta a partir de un diccionario ya limpio."""
        return cls(
            numero_factura=int(datos["numero_factura"]),
            fecha=datos["fecha"],
            lineas=[{
                "codigo": datos["codigo_producto"],
                "nombre": datos["codigo_producto"],
                "precio_unitario": 0.0,
                "cantidad": int(datos["cantidad"]),
                "subtotal": float(datos["subtotal"]),
                "impuestos": float(datos["impuestos"]),
                "total": float(datos["total"]),
            }],
            subtotal=float(datos["subtotal"]),
            impuestos=float(datos["impuestos"]),
            total=float(datos["total"]),
        )

    def __repr__(self):
        return (f"Venta(factura={self.numero_factura}, "
                f"productos={self.codigo_producto}, cantidad={self.cantidad})")
