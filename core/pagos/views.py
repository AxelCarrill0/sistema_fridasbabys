"""
Vistas de la aplicación Pagos.
"""
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image

from core.pagos.models import Pago


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


import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def verificar_identidad_facial(user_foto_path, captura_b64):
    try:
        # Cargar el detector de rostros preentrenado de OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # --- PROCESAR FOTO DE PERFIL ---
        img_perfil = cv2.imread(user_foto_path)
        gris_perfil = cv2.cvtColor(img_perfil, cv2.COLOR_BGR2GRAY)
        rostros_p = face_cascade.detectMultiScale(gris_perfil, 1.1, 4)

        # --- PROCESAR CAPTURA DE CÁMARA ---
        format, imgstr = captura_b64.split(';base64,')
        data = base64.b64decode(imgstr)
        img_captura = Image.open(BytesIO(data)).convert('RGB')
        img_captura_cv = cv2.cvtColor(np.array(img_captura), cv2.COLOR_RGB2BGR)
        gris_captura = cv2.cvtColor(img_captura_cv, cv2.COLOR_BGR2GRAY)
        rostros_c = face_cascade.detectMultiScale(gris_captura, 1.1, 4)

        if len(rostros_p) == 0 or len(rostros_c) == 0:
            return False, "No se detectó un rostro claro en la cámara o en tu perfil."

        # Extraer y normalizar rostros
        (x, y, w, h) = rostros_p[0]
        roi_perfil = cv2.resize(gris_perfil[y:y + h, x:x + w], (200, 200))

        (x, y, w, h) = rostros_c[0]
        roi_captura = cv2.resize(gris_captura[y:y + h, x:x + w], (200, 200))

        # Comparar usando LBPH
        reconocedor = cv2.face.LBPHFaceRecognizer_create()
        reconocedor.train([roi_perfil], np.array([1]))
        etiqueta, distancia = reconocedor.predict(roi_captura)

        # Umbral sugerido: < 70 significa coincidencia aceptable
        if distancia < 70:
            return True, "Identidad confirmada."
        else:
            return False, "El rostro no coincide lo suficiente con la foto de perfil."

    except Exception as e:
        return False, f"Error en el escaneo: {str(e)}"


@login_required
def procesar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)

    if request.method == 'POST':
        # Caso de pago con Tarjeta
        if pago.metodo_pago == 'tarjeta':
            rostro_data = request.POST.get('rostro_verificacion')

            # 1. Validar que exista la imagen de la cámara
            if not rostro_data:
                messages.error(request, "Error: No se recibió la captura del rostro.")
                return render(request, 'pagos/pago_tarjeta.html', {'pago': pago})

            # 2. Validar que el usuario tenga foto de perfil
            if not request.user.foto_perfil:
                messages.error(request, "Debe tener una foto de perfil para verificar su identidad.")
                return redirect('usuarios:perfil')

            # 3. Llamar a la función de comparación (OpenCV)
            es_valido, mensaje = verificar_identidad_facial(request.user.foto_perfil.path, rostro_data)

            if es_valido:
                finalizar_pago(pago)
                messages.success(request, "Identidad verificada exitosamente. Compra realizada.")
                return redirect('pagos:detalle_pago', pago_id=pago.id)
            else:
                # Si no coincide, mostramos el error que devuelve la función
                messages.error(request, f"Fallo de verificación: {mensaje}")
                return render(request, 'pagos/pago_tarjeta.html', {'pago': pago})

        # Caso de Transferencia
        elif pago.metodo_pago == 'transferencia':
            finalizar_pago(pago)
            messages.success(request, "Pago por transferencia registrado.")
            return redirect('pagos:detalle_pago', pago_id=pago.id)

    # Si es GET, simplemente mostramos el formulario
    return render(request, 'pagos/pago_tarjeta.html', {'pago': pago})

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
