"MODELO - Clase del producto"
# Nos va a ayudar a representar un producto en el catálogo de la tienda. Cada producto tendrá un código, un nombre, una categoria, un stock y un stock minimo, un precio de compra y uno de venta y una fecha de vencimiento.

class Producto:
    def __init__(self, codigo, nombre, categoria, stock, stock_minimo, precio_compra, precio_venta, fecha_vencimiento=""):
        # Se guardan los valores ya convertidos.
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        # Si el producto no vence, la fecha queda como un texto vacío.
        self.fecha_vencimiento = fecha_vencimiento

    def to_dict(self):
        """Devuelve el archivo como diccionario"""
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
        """Crea un producto a partir de un diccionario ya limpio (Este se limpia en la siguiente parte.)"""
        return cls(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            categoria=datos["categoria"],
            # int() convierte el texto del CSV a entero, si el texto esta vacio o no es número entonces lanza ValueError.
            stock=int(datos["stock"]),
            stock_minimo=int(datos["stock_minimo"]),
            precio_compra=float(datos["precio_compra"]),
            precio_venta=float(datos["precio_venta"]),
            fecha_vencimiento=datos.get("fecha_vencimiento", "")
        )
    def __repr__(self):
        # Representación corta para depurar en consola.
        return f"Producto({self.codigo}, {self.nombre}, stock={self.stock})"