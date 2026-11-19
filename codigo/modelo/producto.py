class Producto:
    def __init__(self, codigo, nombre, categoria, stock, stock_minimo, precio_compra, precio_venta, fecha_vencimiento=""):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.fecha_vencimiento = fecha_vencimiento
    def to_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
            "precio_compra": self.precio_compra,
            "precio_venta": self.precio_venta,
            "fecha_vencimiento": self.fecha_vencimiento
        }
    @classmethod
    def from_dict(cls, datos):
        return cls(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            categoria=datos["categoria"],
            stock=int(datos["stock"]),
            stock_minimo=int(datos["stock_minimo"]),
            precio_compra=float(datos["precio_compra"]),
            precio_venta=float(datos["precio_venta"]),
            fecha_vencimiento=datos.get("fecha_vencimiento", "")
        )
    def __repr__(self):
        return f"Producto({self.codigo}, {self.nombre}, stock={self.stock})"