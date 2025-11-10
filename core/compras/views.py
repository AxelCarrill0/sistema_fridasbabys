from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.pedidos.models import Pedido


@login_required
def listar_compras(request):
    if not request.user.is_staff:
        return redirect('home:home')

    # Solo pedidos que están "enviado"
    pedidos_enviados = Pedido.objects.filter(estado='enviado').order_by('-fecha_pedido')

    return render(request, 'compras/listar_compras.html', {'pedidos': pedidos_enviados})


@login_required
def confirmar_compra_staff(request, pk):
    if not request.user.is_staff:
        return redirect('home:home')

    pedido = get_object_or_404(Pedido, pk=pk, estado='enviado')
    pedido.estado = 'entregado'
    pedido.save()
    return redirect('compras:lista')
