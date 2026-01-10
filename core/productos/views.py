"""
Vistas de la aplicación Productos.
"""

from decimal import Decimal
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .facade.producto_facade import ProductoFacade
from .models import Producto
from .forms import ProductoForm
from .decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator

facade = ProductoFacade()


@login_required
def listar_productos(request):
    """
    Vista de administración para listar, buscar y filtrar productos.
    """
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    # El administrador ve todos (incluso los no activos si quieres, o puedes filtrar)
    productos = Producto.objects.all()

    # Filtro de búsqueda por texto
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    # Filtro por categoría
    if categoria:
        productos = productos.filter(categoria=categoria)

    contexto = {
        'productos': productos,
        'query': q,
        'categoria_actual': categoria,
        'categorias': Producto.CATEGORIAS,  # Usando el nombre exacto de tu modelo
    }
    return render(request, 'productos/listar.html', contexto)

@login_required
def crear_producto(request):
    """
    Permite crear un nuevo producto mediante un formulario.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            facade.crear_producto(**form.cleaned_data, creado_por=request.user)
            messages.success(request, "Producto creado exitosamente.")
            return redirect("productos:lista")
    else:
        form = ProductoForm()

    return render(request, "productos/crear.html", {'form': form})


@login_required
def editar_producto(request, pk):
    """
    Permite editar un producto existente.
    """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            datos_actualizacion = form.cleaned_data.copy()
            if 'imagen' in datos_actualizacion:
                del datos_actualizacion['imagen']

            facade.actualizar_producto(producto.id, **datos_actualizacion)

            if request.FILES:
                form.save()

            messages.success(request, "Producto actualizado exitosamente.")
            return redirect("productos:detalle", pk=producto.id)
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/editar.html", {'form': form, 'producto': producto})


@login_required
def eliminar_producto(request, pk):
    """
    Permite eliminar un producto.
    """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        try:
            facade.eliminar_producto(pk)
            messages.success(
                request,
                f"El producto '{producto.nombre}' ha sido eliminado exitosamente."
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect("productos:lista")

    return render(request, "productos/confirmar_eliminar.html", {"producto": producto})


def detalle_producto(request, pk):
    """
    Muestra la información detallada de un producto,
    incluyendo el precio con descuento promocional.
    """
    producto = get_object_or_404(Producto, pk=pk)
    descuento_aplicado = Decimal(15)
    precio_final = producto.precio_base

    if not precio_final and hasattr(producto, 'precio'):
        precio_final = producto.precio

    if hasattr(producto, 'precio_final') and producto.precio_final is not None:
        precio_final = producto.precio_final

    precio_promocional = (
        precio_final * (Decimal(1) - descuento_aplicado / Decimal(100))
    ).quantize(Decimal('0.01'))
    ahorro = (precio_final - precio_promocional).quantize(Decimal('0.01'))

    contexto = {
        'producto': producto,
        'descuento_aplicado': descuento_aplicado,
        'precio_promocional': precio_promocional,
        'ahorro': ahorro,
    }

    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'productos/detalle.html', contexto)

    return render(request, 'productos/detalle_cliente.html', contexto)


def catalogo_productos(request):
    """
    Vista pública del catálogo con búsqueda mejorada y filtro de categorías.
    """
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    # Base de productos activos
    productos = Producto.objects.filter(activo=True)

    # Filtro por búsqueda de texto (Nombre o Descripción)
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    # Filtro por categoría (Si tu modelo Producto tiene el campo 'categoria')
    if categoria:
        productos = productos.filter(categoria=categoria)

    # Aplicar decoradores de precio
    productos_decorados = []
    for p in productos:
        componente = ProductoComponent(p)
        descuento = Decimal(15)  # Puedes hacer esto dinámico si gustas
        decorado = DescuentoPorcentajeDecorator(componente, descuento)
        p.precio_final = decorado.get_precio_final()
        productos_decorados.append(p)

    # Obtener categorías únicas para el select del HTML
    # Esto asume que usas choices en el modelo o es un CharField
    categorias_disponibles = Producto.CATEGORIAS
    contexto = {
        'productos': productos_decorados,
        'q': q,
        'categoria_actual': categoria,
        'categorias': categorias_disponibles
    }
    return render(request, 'productos/catalogo.html', contexto)

@login_required
def subir_imagen(request, pk):
    """
    Permite subir o actualizar la imagen de un producto.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        imagen_subida = request.FILES.get('imagen')
        if imagen_subida:
            producto.imagen = imagen_subida
            producto.save()
            return redirect('productos:detalle', pk=producto.pk)

    return render(request, 'productos/subir_imagen.html', {'producto': producto})
