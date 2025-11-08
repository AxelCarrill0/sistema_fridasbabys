import logging
from .producto_observador import ProductoObserver

logger = logging.getLogger(__name__)

class InventarioObserver(ProductoObserver):

    def actualizar(self, producto, cambio):

        # 1. Reacción a cambios en STOCK
        if 'stock' in cambio:
            stock_anterior = cambio['stock']['anterior']
            stock_nuevo = producto.stock

            if stock_nuevo <= 5 and stock_anterior > 5:
                # Dispara una alerta si el stock cae por debajo de 5
                logger.warning(
                    f"[ALERTA CRÍTICA DE INVENTARIO] El producto '{producto.nombre}' "
                    f"ha caído a un stock de {stock_nuevo}. Se necesita reorden."
                )
            elif stock_nuevo > stock_anterior:
                logger.info(
                    f"[MOVIMIENTO INVENTARIO] El stock de '{producto.nombre}' "
                    f"aumentó de {stock_anterior} a {stock_nuevo}."
                )

        # 2. Reacción a cambios en PRECIO (Auditoría)
        if 'precio' in cambio:
            precio_anterior = cambio['precio']['anterior']
            precio_nuevo = producto.precio
            logger.info(
                f"[AUDITORÍA PRECIO] El precio de '{producto.nombre}' "
                f"cambió de ${precio_anterior} a ${precio_nuevo}."
            )