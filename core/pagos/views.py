"""
Vistas de la aplicación Pagos.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.pagos.models import Pago
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from django.conf import settings
import os
import base64
from django.core.files.base import ContentFile

@login_required
def seleccionar_metodo(request, pago_id):
    """
    Permite al usuario seleccionar el método de pago para un Pago específico.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)

    if request.method == 'POST':
        metodo = request.POST.get('metodo')

        if metodo in ['tarjeta', 'transferencia']:
            pago.metodo_pago = metodo
            pago.save()
            return redirect('pagos:procesar_pago', pago_id=pago.id)

    return render(request, 'pagos/seleccionar_metodo.html', {'pago': pago})


@login_required
def procesar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)

    if request.method == 'POST':

        # 🔹 PAGO CON TARJETA
        if pago.metodo_pago == 'tarjeta':
            rostro_b64 = request.POST.get('rostro_verificacion')

            if rostro_b64:
                try:
                    format, imgstr = rostro_b64.split(';base64,')
                    ext = format.split('/')[-1]
                    nombre_archivo = f"pago_{pago.id}_verificacion.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

                    pago.foto_verificacion = data
                    pago.save()

                    finalizar_pago(pago)
                    messages.success(request, "Identidad capturada y pago procesado.")
                    return redirect('pagos:detalle_pago', pago_id=pago.id)

                except Exception:
                    messages.error(request, "Error al guardar la captura facial.")
            else:
                messages.error(request, "Debe capturar su rostro para continuar.")

        # 🔹 PAGO POR TRANSFERENCIA
        elif pago.metodo_pago == 'transferencia':
            finalizar_pago(pago)
            messages.success(request, "Pago por transferencia confirmado.")
            return redirect('pagos:detalle_pago', pago_id=pago.id)

    return render(request, f'pagos/pago_{pago.metodo_pago}.html', {'pago': pago})


def finalizar_pago(pago):
    """
    Marca un Pago como pagado y actualiza el estado de los pedidos y stock de productos.
    """
    pedidos = pago.pedidos.all()

    for pedido in pedidos:
        producto = pedido.producto
        producto.stock -= pedido.cantidad
        producto.save()

        pedido.estado = 'enviado'
        pedido.save()

    pago.estado = 'pagado'
    pago.fecha_pago = timezone.now()
    pago.save()


@login_required
def detalle_pago(request, pago_id):
    """
    Muestra los detalles de un Pago específico.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos = pago.pedidos.all()

    return render(
        request,
        'pagos/detalle_pago.html',
        {
            'pago': pago,
            'pedidos': pedidos
        }
    )


@login_required
def descargar_comprobante(request, pago_id):
    """
    Genera y descarga un comprobante PDF de un Pago.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos = pago.pedidos.all()
    usuario = pago.usuario

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_pago_{pago.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        'titulo',
        parent=styles['Heading2'],
        alignment=1
    )

    elementos = []

    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo.png')
    logo = Image(logo_path, width=80, height=80)

    encabezado = Table([
        [
            logo,
            Paragraph(
                "<b>Frida’s Babys</b><br/>"
                "Recibo de Pago",
                styles['Title']
            )
        ]
    ], colWidths=[100, 380])

    encabezado.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))

    elementos.append(encabezado)
    elementos.append(Spacer(1, 15))

    info_pago = Table([
        ["N° de Pago", pago.id],
        ["Fecha", pago.fecha_pago.strftime('%d/%m/%Y')],
        ["Método de Pago", pago.metodo_pago.capitalize()],
    ], colWidths=[150, 330])

    info_pago.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(info_pago)
    elementos.append(Spacer(1, 15))

    cliente = Table([
        ["Datos del Cliente", ""],
        ["Nombre", usuario.nombre],
        ["Correo", usuario.email],
        ["Teléfono", usuario.telefono],
        ["Dirección", usuario.direccion],
    ], colWidths=[150, 330])


    cliente.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(cliente)
    elementos.append(Spacer(1, 15))

    data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
    total = 0

    for pedido in pedidos:
        subtotal = pedido.cantidad * pedido.producto.precio_final
        total += subtotal
        data.append([
            pedido.producto.nombre,
            pedido.cantidad,
            f"${pedido.producto.precio_final:.2f}",
            f"${subtotal:.2f}",
        ])

    tabla_productos = Table(data, colWidths=[200, 80, 100, 100])
    tabla_productos.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(tabla_productos)
    elementos.append(Spacer(1, 15))

    total_tabla = Table([
        ["TOTAL PAGADO", f"${total:.2f}"]
    ], colWidths=[380, 100])

    total_tabla.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))

    elementos.append(total_tabla)
    elementos.append(Spacer(1, 20))

    elementos.append(
        Paragraph(
            "Gracias por su compra.<br/>",
            styles['Normal']
        )
    )

    doc.build(elementos)
    return response
