"""
Vistas de la aplicación Compras.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.pedidos.models import Pedido


@login_required
def listar_compras(request):
    """
    Muestra la lista de pedidos con estado 'enviado' a usuarios staff.
    """
    if not request.user.is_staff:
        return redirect('home:home')

    pedidos_enviados = Pedido.objects.filter(estado='enviado').order_by('-fecha_pedido')
    return render(request, 'compras/listar_compras.html', {'pedidos': pedidos_enviados})


@login_required
def confirmar_compra_staff(request, pk):
    """
    Permite al staff confirmar un pedido cambiando su estado a 'entregado'.
    """
    if not request.user.is_staff:
        return redirect('home:home')

    pedido = get_object_or_404(Pedido, pk=pk, estado='enviado')
    pedido.estado = 'entregado'
    pedido.save()
    return redirect('compras:lista')
