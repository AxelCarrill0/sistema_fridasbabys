from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .facade.producto_facade import ProductoFacade
from .models import Producto
from .forms import ProductoForm
from .decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from decimal import Decimal

from django.db.models import Q
from core.pedidos.models import Pedido

facade = ProductoFacade()


# 1. VISTA DE LISTADO

@staff_member_required
def listar_productos(request):
    query = request.GET.get('q', '')
    productos = facade.listar_productos(query=query)
    contexto = {'productos': productos, 'query': query}
    return render(request, "productos/listar.html", contexto)

# 2. VISTA DE CREACIÓN
@login_required
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            facade.crear_producto(**form.cleaned_data, creado_por=request.user)
            return redirect("productos:lista")
    else:
        form = ProductoForm()

    return render(request, "productos/crear.html", {'form': form})

# 3. VISTA DE EDICIÓN
@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect("productos:lista")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/editar.html", {"form": form, "producto": producto})

# 4. VISTA DE ELIMINACIÓN
@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        facade.eliminar_producto(pk)
        return redirect("productos:lista")

    return render(request, "productos/confirmar_eliminar.html", {"producto": producto})

# 5. VISTA DE DETALLE
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    # Descuento simulado (puedes hacerlo dinámico)
    descuento_aplicado = Decimal(15)

    # ✅ Convertimos todo a Decimal para evitar errores
    precio_promocional = producto.precio * (Decimal(1) - descuento_aplicado / Decimal(100))
    precio_promocional = precio_promocional.quantize(Decimal('0.01'))  # redondear a 2 decimales

    contexto = {
        'producto': producto,
        'descuento_aplicado': descuento_aplicado,
        'precio_promocional': precio_promocional,
    }

    # ✅ Detectar tipo de usuario para mostrar interfaz adecuada
    if request.user.is_authenticated and request.user.is_staff:
        # Vista para administradores o vendedores (con botones de gestión)
        return render(request, 'productos/detalle.html', contexto)
    else:
        # Vista para clientes (solo información)
        return render(request, 'productos/detalle_cliente.html', contexto)

def catalogo_productos(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.all()

    if q:
        # Filtrar productos que comienzan con la letra o palabra ingresada (insensible a mayúsculas)
        productos = productos.filter(nombre__istartswith=q)

    return render(request, 'productos/catalogo.html', {'productos': productos, 'q': q})