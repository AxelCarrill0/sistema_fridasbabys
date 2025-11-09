from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido

@login_required
def lista_pedidos(request):
    # Si el staff envía un POST, actualiza el estado del pedido
    if request.method == 'POST' and request.user.is_staff:
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')

        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()

        return redirect('pedidos:lista_pedidos')

    # Si no hay POST, mostramos los pedidos según el rol
    if request.user.is_staff:
        pedidos = Pedido.objects.all()  # Staff ve todos los pedidos
        base_template = 'home/base.html'
    else:
        pedidos = Pedido.objects.filter(cliente=request.user)  # Cliente ve solo los suyos
        base_template = 'home/base_cliente.html'

    context = {
        'pedidos': pedidos,
        'base_template': base_template
    }

    return render(request, 'pedidos/lista_pedidos.html', context)
