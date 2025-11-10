from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .facade.producto_facade import ProductoFacade
from .models import Producto
from .forms import ProductoForm
from .decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from decimal import Decimal
from django.db.models import Q


facade = ProductoFacade()

@staff_member_required
def listar_productos(request):
    query = request.GET.get('q', '')
    productos = facade.listar_productos(query=query)
    return render(request, "productos/listar.html", {'productos': productos, 'query': query})

@login_required
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            facade.crear_producto(**form.cleaned_data, creado_por=request.user)
            return redirect("productos:lista")
    else:
        form = ProductoForm()
    return render(request, "productos/crear.html", {'form': form})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect("productos:lista")
    else:
        form = ProductoForm(instance=producto)
    return render(request, "productos/editar.html", {"form": form, "producto": producto})

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        facade.eliminar_producto(pk)
        return redirect("productos:lista")
    return render(request, "productos/confirmar_eliminar.html", {"producto": producto})

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    descuento_aplicado = Decimal(15)
    componente = ProductoComponent(producto)
    decorado = DescuentoPorcentajeDecorator(componente, descuento_aplicado)
    precio_promocional = decorado.get_precio_final()

    contexto = {
        'producto': producto,
        'descuento_aplicado': descuento_aplicado,
        'precio_promocional': precio_promocional,
    }
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'productos/detalle.html', contexto)
    return render(request, 'productos/detalle_cliente.html', contexto)


def catalogo_productos(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(activo=True)

    if q:
        # Buscar productos que contengan cualquiera de las letras que escribes
        q_filter = Q()
        for letra in q:
            q_filter |= Q(nombre__icontains=letra)
        productos = productos.filter(q_filter)

    # Aplicar decorador de descuento
    productos_decorados = []
    for p in productos:
        componente = ProductoComponent(p)
        decorado = DescuentoPorcentajeDecorator(componente, Decimal(10))
        p.precio_final = decorado.get_precio_final()
        productos_decorados.append(p)

    return render(request, 'productos/catalogo.html', {'productos': productos_decorados, 'q': q})

@login_required
def subir_imagen(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        imagen = request.FILES.get('imagen')
        if imagen:
            producto.imagen = imagen
            producto.save()
            return redirect('productos:detalle', pk=pk)
    return render(request, 'productos/subir_imagen.html', {'producto': producto})
