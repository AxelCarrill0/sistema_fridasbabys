"""
Vistas de la aplicación Productos.
"""

from decimal import Decimal
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importamos el Modelo y el Formulario
from .models import Producto
from .forms import ProductoForm

# NOTA: Hemos eliminado Facade y Decorator para permitir
# que el cálculo del descuento manual del modelo funcione correctamente.

@login_required
def listar_productos(request):
    """
    Vista de administración para listar, buscar y filtrar productos.
    """
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    # Obtenemos todos los productos ordenados por id descendente (los nuevos primero)
    productos = Producto.objects.all().order_by('-id')

    # 1. Filtro de búsqueda por texto (Nombre o Descripción)
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    # 2. Filtro por categoría
    if categoria:
        productos = productos.filter(categoria=categoria)

    contexto = {
        'productos': productos,
        'query': q,
        'categoria_actual': categoria,
        'categorias': Producto.CATEGORIAS,
    }
    return render(request, 'productos/listar.html', contexto)


@login_required
def crear_producto(request):
    """
    Permite crear un nuevo producto.
    Al usar form.save(), se activa el cálculo automático de precios en models.py.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creado_por = request.user
            # Al guardar aquí, se ejecuta la matemática: (Base + Ganancia) - Descuento
            producto.save()
            messages.success(request, f"Producto '{producto.nombre}' creado exitosamente.")
            return redirect("productos:lista")
    else:
        form = ProductoForm()

    return render(request, "productos/crear.html", {'form': form})


@login_required
def editar_producto(request, pk):
    """
    Permite editar un producto. Si cambias el descuento aquí,
    el precio final se recalculará automáticamente.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            # El método save() del modelo recalcula todo basado en los nuevos inputs
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos:detalle", pk=producto.id)
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/editar.html", {'form': form, 'producto': producto})


@login_required
def eliminar_producto(request, pk):
    """
    Elimina un producto de la base de datos.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"El producto '{nombre}' fue eliminado correctamente.")
        return redirect("productos:lista")

    return render(
        request,
        "productos/confirmar_eliminar.html",
        {"producto": producto}
    )


def detalle_producto(request, pk):
    """
    Muestra la información detallada.
    Calcula el 'Ahorro' visualmente para el cliente.
    """
    producto = get_object_or_404(Producto, pk=pk)

    # Lógica para mostrar cuánto se ahorra el cliente si hay descuento
    ahorro = Decimal('0.00')
    precio_antes = producto.precio_final # Valor por defecto

    if producto.descuento > 0:
        # Reconstruimos el precio "Original" (Precio base + ganancia)
        # Esto es solo visual para mostrar el tachado
        precio_antes = producto.precio_base * (1 + (producto.ganancia / Decimal('100')))
        ahorro = precio_antes - producto.precio_final

    contexto = {
        'producto': producto,
        'ahorro': ahorro,
        # 'precio_antes' sirve para mostrar el precio tachado si quieres usarlo en el template
        'precio_antes': precio_antes.quantize(Decimal("0.01"))
    }

    # Si es administrador, ve la vista interna
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'productos/detalle.html', contexto)

    # Si es cliente, ve la vista pública
    return render(request, 'productos/detalle_cliente.html', contexto)


def catalogo_productos(request):
    """
    Vista pública del catálogo.
    Muestra los precios finales que YA tienen el descuento aplicado en la BD.
    """
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    # Solo mostramos productos activos
    productos = Producto.objects.filter(activo=True).order_by('nombre')

    # Filtro Búsqueda
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    # Filtro Categoría
    if categoria:
        productos = productos.filter(categoria=categoria)

    contexto = {
        'productos': productos,
        'q': q,
        'categoria_actual': categoria,
        'categorias': Producto.CATEGORIAS
    }
    return render(request, 'productos/catalogo.html', contexto)


@login_required
def subir_imagen(request, pk):
    """
    Vista dedicada para actualizar solo la imagen.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        imagen_subida = request.FILES.get('imagen')
        if imagen_subida:
            producto.imagen = imagen_subida
            producto.save() # Esto también recalcula el precio, pero es seguro.
            messages.success(request, "Imagen actualizada correctamente.")
            return redirect('productos:detalle', pk=producto.pk)
        else:
            messages.warning(request, "No seleccionaste ninguna imagen.")

    return render(request, 'productos/subir_imagen.html', {'producto': producto})