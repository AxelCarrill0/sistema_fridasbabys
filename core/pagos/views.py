import decimal
import os
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.core.files.base import ContentFile

# Importaciones para ReportLab (PDF)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from core.pagos.models import Pago
from core.productos.decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from core.productos.facade.producto_facade import ProductoFacade

TASA_IVA = decimal.Decimal('0.15')


def calcular_desglose_pedido(pedido):
    """
    Calcula valores y extrae datos del vendedor (Staff) correctamente.
    """
    facade = ProductoFacade()
    # Asegúrate de que esto devuelva la instancia del Modelo, no un diccionario
    producto = facade.obtener_producto(pedido.producto.id)

    precio_base_unitario = producto.precio_final
    descuento_valor = getattr(producto, 'descuento', 0)

    if descuento_valor > 0:
        componente = ProductoComponent(producto)
        descuento_porcentaje = decimal.Decimal(str(descuento_valor))
        producto_decorado = DescuentoPorcentajeDecorator(componente, descuento_porcentaje)
        precio_con_descuento = producto_decorado.get_precio_final()
        monto_descuento_unitario = precio_base_unitario - precio_con_descuento
    else:
        precio_con_descuento = precio_base_unitario
        monto_descuento_unitario = decimal.Decimal('0.00')

    precio_neto_unitario = precio_con_descuento
    cantidad = pedido.cantidad
    fila_subtotal = precio_neto_unitario * cantidad

    # --- CORRECCIÓN NOMBRE VENDEDOR (STAFF) ---
    # Usamos la relación 'creado_por' directamente
    autor = getattr(producto, 'creado_por', None)

    if autor:
        # Intentamos obtener nombre y apellido
        nombre_completo = f"{autor.first_name} {autor.last_name}".strip()
        if nombre_completo:
            nombre_vendedor = nombre_completo
        else:
            # Si no tiene nombre configurado, usamos el usuario
            nombre_vendedor = autor.username
    else:
        nombre_vendedor = "Admin / Sistema"

    return {
        'pedido': pedido,
        'producto': producto,
        'nombre_vendedor': nombre_vendedor,  # <--- Dato corregido
        'cantidad': cantidad,
        'precio_base_unit': precio_base_unitario,
        'monto_desc_unit': monto_descuento_unitario,
        'precio_final_unit': precio_neto_unitario,
        'fila_subtotal': fila_subtotal,
    }


@login_required
def seleccionar_metodo(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos_raw = pago.pedidos.all()

    lista_detalles = []
    suma_subtotales = decimal.Decimal('0.00')

    for pedido in pedidos_raw:
        datos = calcular_desglose_pedido(pedido)
        lista_detalles.append(datos)
        suma_subtotales += datos['fila_subtotal']

    monto_iva_total = suma_subtotales * TASA_IVA
    total_a_pagar = suma_subtotales + monto_iva_total

    if pago.total != total_a_pagar:
        pago.total = total_a_pagar
        pago.save()

    if request.method == 'POST':
        metodo = request.POST.get('metodo')
        if metodo in ['tarjeta', 'transferencia']:
            pago.metodo_pago = metodo
            pago.save()
            return redirect('pagos:procesar_pago', pago_id=pago.id)

    context = {
        'pago': pago,
        'pedidos_detalle': lista_detalles,
        'resumen': {
            'subtotal': suma_subtotales,
            'iva': monto_iva_total,
            'total': total_a_pagar
        }
    }
    return render(request, 'pagos/seleccionar_metodo.html', context)


@login_required
def procesar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos = pago.pedidos.all()

    suma_subtotal = decimal.Decimal('0.00')
    for pedido in pedidos:
        datos = calcular_desglose_pedido(pedido)
        suma_subtotal += datos['fila_subtotal']

    total_iva = suma_subtotal * TASA_IVA
    total_final = suma_subtotal + total_iva

    if request.method == 'POST':
        if pago.metodo_pago == 'tarjeta':
            rostro_b64 = request.POST.get('rostro_verificacion')
            if rostro_b64:
                try:
                    format, imgstr = rostro_b64.split(';base64,')
                    ext = format.split('/')[-1]
                    nombre_archivo = f"pago_{pago.id}_verificacion.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=nombre_archivo)

                    pago.foto_verificacion = data
                    # Guardamos ID de transacción automático para tarjeta si deseas
                    pago.codigo_comprobante = f"CARD-{pago.id}-{timezone.now().strftime('%H%M%S')}"
                    pago.save()
                    finalizar_pago(pago)
                    messages.success(request, "Pago procesado con éxito.")
                    return redirect('pagos:detalle_pago', pago_id=pago.id)
                except Exception as e:
                    messages.error(request, "Error en la verificación facial.")
            else:
                messages.error(request, "Verificación facial requerida.")

        elif pago.metodo_pago == 'transferencia':
            codigo = request.POST.get('codigo_comprobante')
            imagen = request.FILES.get('foto_verificacion')

            if codigo and imagen:
                pago.codigo_comprobante = codigo  # <--- AQUÍ SE GUARDA EL ID TRANSACCION
                pago.foto_verificacion = imagen
                pago.save()
                finalizar_pago(pago)
                messages.success(request, "Comprobante subido correctamente.")
                return redirect('pagos:detalle_pago', pago_id=pago.id)
            else:
                messages.error(request, "Faltan datos del comprobante.")

    return render(request, f'pagos/pago_{pago.metodo_pago}.html', {
        'pago': pago,
        'pedidos': pedidos,
        'total_mostrar': total_final
    })


def finalizar_pago(pago):
    pedidos = pago.pedidos.all()
    for pedido in pedidos:
        producto = pedido.producto
        if producto.stock >= pedido.cantidad:
            producto.stock -= pedido.cantidad
            producto.save()
        pedido.estado = 'enviado'
        pedido.save()

    pago.estado = 'pagado'
    pago.fecha_pago = timezone.now()
    pago.save()


@login_required
def detalle_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos_raw = pago.pedidos.all()

    lista_detalles = []
    suma_subtotales = decimal.Decimal('0.00')

    for pedido in pedidos_raw:
        datos = calcular_desglose_pedido(pedido)
        lista_detalles.append(datos)
        suma_subtotales += datos['fila_subtotal']

    monto_iva_total = suma_subtotales * TASA_IVA

    return render(request, 'pagos/detalle_pago.html', {
        'pago': pago,
        'detalles': lista_detalles,
        'subtotal': suma_subtotales,
        'total_iva': monto_iva_total
    })


@login_required
def descargar_comprobante(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    usuario = pago.usuario
    pedidos_raw = pago.pedidos.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante_FridasBabys_{pago.id}.pdf"'

    ANCHO_UTIL = 535

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elementos = []

    # ======================
    # COLORES & ESTILOS
    # ======================
    COLOR_PRIMARIO = colors.HexColor("#1d3557")
    COLOR_GRIS = colors.HexColor("#6c757d")
    COLOR_LINEA = colors.HexColor("#e5e5e5")

    normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=9, leading=12)
    bold = ParagraphStyle('bold', parent=normal, fontName='Helvetica-Bold')
    small = ParagraphStyle('small', parent=normal, fontSize=8, textColor=COLOR_GRIS)
    right = ParagraphStyle('right', parent=normal, alignment=TA_RIGHT)
    title = ParagraphStyle('title', parent=styles['Heading1'], fontSize=15, textColor=COLOR_PRIMARIO,
                           alignment=TA_RIGHT)

    # ======================
    # HEADER
    # ======================
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo.png')
    logo = Image(logo_path, 48, 48) if os.path.exists(logo_path) else Spacer(1, 48)

    header = Table(
        [[logo, Paragraph("<b>COMPROBANTE DE PAGO</b><br/><font size='9'>Frida's Babys S.A.</font>", title)]],
        colWidths=[60, ANCHO_UTIL - 60]
    )
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_LINEA),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
    ]))
    elementos.append(header)
    elementos.append(Spacer(1, 20))

    # ======================
    # INFO CLIENTE
    # ======================
    nombre_cliente = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username

    info = [
        [Paragraph("<b>DATOS DEL CLIENTE</b>", bold), "", Paragraph("<b>DETALLE DE TRANSACCIÓN</b>", bold), ""],
        ["Cliente:", nombre_cliente, "Orden:", str(pago.id)],
        ["Email:", usuario.email, "Fecha:", pago.fecha_pago.strftime('%d/%m/%Y %H:%M') if pago.fecha_pago else "-"],
        ["Teléfono:", usuario.telefono or "-", "Método:", pago.get_metodo_pago_display()],
        ["Dirección:", usuario.direccion or "-", "Referencia:", pago.codigo_comprobante or "-"]
    ]

    t_info = Table(info, colWidths=[70, 195, 70, 200])
    t_info.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_PRIMARIO),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Etiquetas col 1 negrita
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),  # Etiquetas col 3 negrita
        ('TEXTCOLOR', (0, 1), (0, -1), COLOR_GRIS),
        ('TEXTCOLOR', (2, 1), (2, -1), COLOR_GRIS),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_info)
    elementos.append(Spacer(1, 26))

    # ======================
    # 1. DEFINICIÓN DE ANCHOS (CLAVE PARA LA ALINEACIÓN)
    # ======================
    # Anchos: [Prod, Vend, Cant, Unit, Desc, Total]
    anchos_cols = [150, 95, 40, 75, 75, 100]

    # ======================
    # 2. TABLA DE PRODUCTOS
    # ======================
    headers = ["Producto", "Vendedor", "Cant", "P. Unit", "Desc", "Subtotal"]
    data = [[Paragraph(h, bold) for h in headers]]

    subtotal = decimal.Decimal('0.00')

    for pedido in pedidos_raw:
        d = calcular_desglose_pedido(pedido)
        data.append([
            Paragraph(d['producto'].nombre, normal),
            Paragraph(d['nombre_vendedor'], small),
            str(d['cantidad']),
            f"${d['precio_base_unit']:.2f}",
            f"-${d['monto_desc_unit']:.2f}" if d['monto_desc_unit'] > 0 else "-",
            f"${d['fila_subtotal']:.2f}",
        ])
        subtotal += d['fila_subtotal']

    t_prod = Table(data, colWidths=anchos_cols, repeatRows=1)
    t_prod.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_PRIMARIO),  # Línea header
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Cantidad Centrada
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Precios a la derecha
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, COLOR_LINEA),  # Líneas sutiles entre items
    ]))

    elementos.append(t_prod)

    # NOTA: No ponemos Spacer aquí o ponemos uno muy pequeño para que parezca la misma tabla
    # elementos.append(Spacer(1, 0))

    # ======================
    # 3. TABLA DE TOTALES (ALINEADA PERFECTAMENTE)
    # ======================
    iva = subtotal * TASA_IVA
    total = subtotal + iva

    # Truco Matemático:
    # Sumamos el ancho de las primeras 4 columnas para dejar ese espacio vacío a la izquierda
    # 150 + 95 + 40 + 75 = 360
    ancho_vacio = sum(anchos_cols[:4])
    ancho_etiqueta = anchos_cols[4]  # Corresponde a la columna 'Desc' (75)
    ancho_valor = anchos_cols[5]  # Corresponde a la columna 'Subtotal' (100)

    data_totales = [
        ["", "Subtotal:", f"${subtotal:.2f}"],
        ["", "IVA (15%):", f"${iva:.2f}"],
        ["", Paragraph("<b>TOTAL</b>", right), Paragraph(f"<b>${total:.2f}</b>", right)],
    ]

    t_totales = Table(data_totales, colWidths=[ancho_vacio, ancho_etiqueta, ancho_valor])

    t_totales.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Alinear etiquetas y valores a la derecha
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # Línea decorativa sobre el TOTAL FINAL (solo en las ultimas 2 columnas)
        ('LINEABOVE', (1, 2), (-1, 2), 1, COLOR_PRIMARIO),
        ('TEXTCOLOR', (2, 2), (2, 2), COLOR_PRIMARIO),  # Color azul para el monto total
    ]))

    elementos.append(t_totales)

    # ======================
    # FOOTER
    # ======================
    elementos.append(Spacer(1, 40))
    elementos.append(Paragraph(
        "Gracias por comprar en Frida's Babys. Documento generado automáticamente por el sistema.",
        ParagraphStyle('cen', parent=normal, alignment=TA_CENTER)
    ))

    doc.build(elementos)
    return response