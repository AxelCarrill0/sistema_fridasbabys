from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .facade.producto_facade import ProductoFacade
from .models import Producto
from .forms import ProductoForm
from .decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
import decimal

facade = ProductoFacade()


# 1. VISTA DE LISTADO

@login_required
def listar_productos(request):
    query = request.GET.get('q')
    productos = facade.listar_productos(query=query)
    contexto = {'productos': productos, 'query': query}
    return render(request, "productos/listar.html", contexto)

# 2. VISTA DE CREACIÓN
@login_required
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            facade.crear_producto(**form.cleaned_data)
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
@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    # Implementación del Decorator (DDSG-43)
    producto_base = ProductoComponent(producto)
    descuento_porcentaje = decimal.Decimal("15.00")

    producto_con_descuento = DescuentoPorcentajeDecorator(
        producto_base,
        descuento_porcentaje
    )

    precio_promocional = producto_con_descuento.get_precio_final()

    contexto = {
        "producto": producto,
        "descuento_aplicado": descuento_porcentaje,
        "precio_promocional": precio_promocional,
    }

    return render(request, "productos/detalle.html", contexto)