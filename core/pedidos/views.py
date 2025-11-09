# core/pedidos/views.py
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from core.productos.decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
import decimal
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from core.pedidos.models import Pedido
from core.productos.facade.producto_facade import ProductoFacade
from django.contrib import messages

@login_required
def lista_pedidos(request):
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
        descuento = decimal.Decimal('10')  # ejemplo de descuento
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
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        user = request.user

        facade = ProductoFacade()
        producto = facade.obtener_producto(producto_id)

        if cantidad > producto.stock:
            messages.error(request, f"No hay suficiente stock para {producto.nombre}.")
            return redirect('productos:detalle', producto.id)

        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=user,
            producto=producto,
            cantidad=cantidad
        )

        messages.success(request, f"Se agregó {cantidad} x {producto.nombre} a tus pedidos.")
        return redirect('pedidos:lista_pedidos')
    return redirect('productos:catalogo')

@login_required
def editar_pedido(request, pedido_id):
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

        # Actualizar cantidad
        pedido.cantidad = cantidad_nueva
        pedido.save()
        messages.success(request, f"Cantidad del pedido #{pedido.id} actualizada a {cantidad_nueva}.")
        return redirect('pedidos:lista_pedidos')

    # GET: mostrar formulario
    context = {
        "pedido": pedido,
        "producto": producto
    }
    return render(request, "pedidos/editar_pedido.html", context)

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    pedido.delete()
    messages.success(request, f"Pedido #{pedido.id} cancelado correctamente.")
    return redirect('pedidos:lista_pedidos')

@login_required
def confirmar_compra(request):
    if request.method == "POST":
        user = request.user
        pedidos = Pedido.objects.filter(cliente=user, estado='pendiente')

        with transaction.atomic():
            for pedido in pedidos:
                producto = pedido.producto
                if pedido.cantidad > producto.stock:
                    messages.error(request, f"No hay stock suficiente para {producto.nombre}.")
                    return redirect('pedidos:lista_pedidos')
                producto.stock -= pedido.cantidad
                producto.save()
                pedido.estado = 'enviado'  # o 'confirmado', según tu modelo
                pedido.save()

        messages.success(request, "¡Compra confirmada con éxito!")
        return redirect('pedidos:lista_pedidos')
    return redirect('pedidos:lista_pedidos')