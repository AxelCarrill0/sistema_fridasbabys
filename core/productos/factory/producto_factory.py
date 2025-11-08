from core.productos.models import Producto

class ProductoFactory:
    """
    Patrón Factory.

    Gestiona la creación de instancias de Producto.
    """

    @staticmethod
    def crear_producto(**datos):


        producto = Producto.objects.create(**datos)

        return producto