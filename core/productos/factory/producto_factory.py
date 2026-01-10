from decimal import Decimal
from core.productos.models import Producto


class ProductoFactory:

    @staticmethod
    def crear_producto(creado_por=None, **datos):
        precio_base = Decimal(datos.get("precio_base"))
        ganancia = Decimal(datos.get("ganancia", 40))
        precio_final = precio_base * (Decimal(1) + ganancia / Decimal(100))

        datos["precio_final"] = precio_final.quantize(Decimal("0.01"))
        datos["creado_por"] = creado_por

        return Producto.objects.create(**datos)
