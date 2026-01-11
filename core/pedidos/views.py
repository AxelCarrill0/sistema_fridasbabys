"""
Vistas de la aplicación Pedidos.
Gestiona listado, edición, cancelación y confirmación de pedidos.
"""

import decimal

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.productos.decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from core.productos.facade.producto_facade import ProductoFacade
from core.pedidos.models import Pedido
from core.pagos.models import Pago


@login_required
def lista_pedidos(request):
    """
    Lista los pedidos del usuario.
    Si el usuario es staff, lista todos los pedidos.
    Calcula subtotal y precio final con decorador de descuento.
    """
    facade = ProductoFacade()

    if request.user.is_staff:
        pedidos = Pedido.objects.all()
    else:
        pedidos = Pedido.objects.filter(cliente=request.user)

    pedidos_pendientes_detalle = []
    pedidos_enviados_detalle = []
    total_pendientes = decimal.Decimal('0.00')

    for pedido in pedidos:
        producto = facade.obtener_producto(pedido.producto.id)
        componente = ProductoComponent(producto)
        descuento = decimal.Decimal('10')
        producto_decorado = DescuentoPorcentajeDecorator(componente, descuento)
        precio_final = producto_decorado.get_precio_final()
        subtotal = precio_final * pedido.cantidad

        detalle = {
            'pedido': pedido,
            'precio_final': precio_final,
            'subtotal': subtotal,
            'descuento': descuento
        }

        if pedido.estado == 'pendiente':
            pedidos_pendientes_detalle.append(detalle)
            total_pendientes += subtotal
        else:
            pedidos_enviados_detalle.append(detalle)

    context = {
        'pendientes': pedidos_pendientes_detalle,
        'enviados': pedidos_enviados_detalle,
        'total_pendientes': total_pendientes
    }

    return render(request, 'pedidos/lista_pedidos.html', context)


@login_required
def agregar_a_pedido(request):
    """
    Agrega un producto al pedido del usuario.
    Controla stock y cantidades existentes.
    """
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        try:
            cantidad_nueva = int(request.POST.get('cantidad', 1))
        except ValueError:
            messages.error(request, "La cantidad debe ser un número entero válido.")
            return redirect('productos:catalogo')

        user = request.user
        facade = ProductoFacade()
        producto = facade.obtener_producto(producto_id)

        if cantidad_nueva <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
            return redirect('productos:detalle', producto_id)

        pedido_existente = Pedido.objects.filter(
            cliente=user,
            producto=producto,
            estado='pendiente'
        ).first()

        if pedido_existente:
            cantidad_total = pedido_existente.cantidad + cantidad_nueva
            if cantidad_total > producto.stock:
                messages.error(
                    request,
                    f"No hay suficiente stock. Sólo quedan {producto.stock} disponibles en total "
                    f"(ya tienes {pedido_existente.cantidad} en tu carrito)."
                )
                return redirect('productos:detalle', producto.id)

            pedido_existente.cantidad = cantidad_total
            pedido_existente.save()
            messages.success(
                request,
                f"Se agregó {cantidad_nueva} x {producto.nombre}. "
                f"Cantidad total en el carrito: {cantidad_total}."
            )
        else:
            if cantidad_nueva > producto.stock:
                messages.error(
                    request,
                    f"No hay suficiente stock para {producto.nombre} ({producto.stock} disponibles)."
                )
                return redirect('productos:detalle', producto.id)

            Pedido.objects.create(
                cliente=user,
                producto=producto,
                cantidad=cantidad_nueva
            )
            messages.success(request, f"¡{cantidad_nueva} x {producto.nombre} agregado al carrito!")

        return redirect('pedidos:lista_pedidos')

    return redirect('productos:catalogo')


@login_required
def editar_pedido(request, pedido_id):
    """
    Edita la cantidad de un pedido pendiente.
    Controla stock y cantidad mínima.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    producto = pedido.producto

    if request.method == "POST":
        try:
            cantidad_nueva = int(request.POST.get("cantidad"))
        except ValueError:
            messages.error(request, "Cantidad inválida.")
            return redirect('pedidos:editar_pedido', pedido_id=pedido.id)

        if cantidad_nueva <= 0:
            messages.error(request, "La cantidad debe ser mayor a 0.")
            return redirect('pedidos:editar_pedido', pedido_id=pedido.id)

        if cantidad_nueva > producto.stock:
            messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
            return redirect('pedidos:editar_pedido', pedido_id=pedido.id)

        pedido.cantidad = cantidad_nueva
        pedido.save()
        messages.success(request, f"Cantidad del pedido #{pedido.id} actualizada a {cantidad_nueva}.")
        return redirect('pedidos:lista_pedidos')

    context = {
        "pedido": pedido,
        "producto": producto
    }
    return render(request, "pedidos/editar_pedido.html", context)


@login_required
def cancelar_pedido(request, pedido_id):
    """
    Cancela un pedido del usuario.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    pedido.delete()
    messages.success(request, f"Pedido #{pedido.id} cancelado correctamente.")
    return redirect('pedidos:lista_pedidos')


@login_required
@transaction.atomic
def confirmar_compra(request):
    if request.method != "POST":
        return redirect('pedidos:lista_pedidos')

    user = request.user

    # 1. Obtenemos TODOS los pedidos pendientes (nuevos y viejos)
    pedidos = Pedido.objects.filter(
        cliente=user,
        estado='pendiente'
    )

    if not pedidos.exists():
        messages.warning(request, "No tienes pedidos pendientes para confirmar.")
        return redirect('pedidos:lista_pedidos')

    # 2. Recalculamos el TOTAL de todo lo que hay en el carrito ahora mismo
    facade = ProductoFacade()
    total = decimal.Decimal('0.00')

    for pedido in pedidos:
        producto = facade.obtener_producto(pedido.producto.id)
        componente = ProductoComponent(producto)
        descuento = decimal.Decimal('10')
        producto_decorado = DescuentoPorcentajeDecorator(componente, descuento)
        precio_final = producto_decorado.get_precio_final()
        total += precio_final * pedido.cantidad

    # 3. Buscamos si ya existe un pago pendiente o creamos uno nuevo
    pago = Pago.objects.filter(usuario=user, estado='pendiente').first()

    if pago:
        # Si ya existe, actualizamos el total con los nuevos productos
        pago.total = total
        pago.save()
    else:
        # Si no existe, lo creamos
        pago = Pago.objects.create(
            usuario=user,
            total=total,
            estado='pendiente'
        )

    # 4. VINCULACIÓN CRÍTICA:
    # Asignamos este pago a TODOS los pedidos pendientes encontrados.
    # Esto arregla el problema de que no aparezcan.
    pedidos.update(pago=pago)

    messages.success(request, "Compra confirmada. Selecciona el método de pago.")
    return redirect('pagos:seleccionar_metodo', pago_id=pago.id)