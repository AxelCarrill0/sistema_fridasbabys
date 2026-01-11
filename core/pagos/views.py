"""
Vistas de la aplicación Pagos ACTUALIZADAS Y CORREGIDAS.
"""

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

# ReportLab para PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

# Modelos
from core.pagos.models import Pago
from core.productos.decorator.producto_decorator import ProductoComponent, DescuentoPorcentajeDecorator
from core.productos.facade.producto_facade import ProductoFacade

# CONFIGURACIÓN DEL IVA (15%)
TASA_IVA = decimal.Decimal('0.15')

def calcular_desglose_pedido(pedido):
    """
    Función auxiliar para calcular precios, descuentos e IVA de un pedido.
    """
    facade = ProductoFacade()
    producto = facade.obtener_producto(pedido.producto.id)

    # --- CORRECCIÓN AQUÍ ---
    # Usamos 'precio_final' porque 'precio' no existe en tu modelo.
    # Este es el precio de lista antes de aplicar el descuento de la promoción actual.
    precio_base_unitario = producto.precio_final

    # 2. Aplicar Descuento (Patrón Decorator)
    componente = ProductoComponent(producto)
    descuento_porcentaje = decimal.Decimal('10') # 10% de descuento
    producto_decorado = DescuentoPorcentajeDecorator(componente, descuento_porcentaje)

    # El decorator nos devuelve el precio ya rebajado
    precio_con_descuento_unitario = producto_decorado.get_precio_final()

    # 3. Calcular Monto del Descuento (Diferencia entre base y rebajado)
    monto_descuento_unitario = precio_base_unitario - precio_con_descuento_unitario

    # 4. Calcular IVA sobre el precio con descuento (Base Imponible)
    monto_iva_unitario = precio_con_descuento_unitario * TASA_IVA

    # 5. Precio Final Unitario (Con IVA)
    precio_final_unitario = precio_con_descuento_unitario + monto_iva_unitario

    # 6. Calcular Subtotales por cantidad
    cantidad = pedido.cantidad

    # Intentamos obtener el usuario del producto, si no existe, ponemos None
    vendedor = getattr(producto, 'usuario', None)

    return {
        'pedido': pedido,
        'producto': producto,
        'vendedor': vendedor, # El usuario que subió el producto
        'cantidad': cantidad,
        'precio_base_unit': precio_base_unitario,
        'monto_desc_unit': monto_descuento_unitario,
        'precio_subtotal_unit': precio_con_descuento_unitario, # Precio antes de IVA
        'monto_iva_unit': monto_iva_unitario,
        'precio_final_unit': precio_final_unitario,
        'fila_subtotal_base': precio_con_descuento_unitario * cantidad, # Subtotal sin IVA
        'fila_monto_iva': monto_iva_unitario * cantidad, # Total IVA de esta fila
        'fila_total': precio_final_unitario * cantidad # Total final a pagar
    }


@login_required
def seleccionar_metodo(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos_raw = pago.pedidos.all()

    lista_detalles = []
    acumulado_subtotal = decimal.Decimal('0.00')
    acumulado_iva = decimal.Decimal('0.00')
    acumulado_total = decimal.Decimal('0.00')

    # Procesamos cada pedido con el desglose detallado
    for pedido in pedidos_raw:
        datos = calcular_desglose_pedido(pedido)
        lista_detalles.append(datos)

        acumulado_subtotal += datos['fila_subtotal_base']
        acumulado_iva += datos['fila_monto_iva']
        acumulado_total += datos['fila_total']

    # Actualizamos el total del pago en la BD
    if pago.total != acumulado_total:
        pago.total = acumulado_total
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
            'subtotal': acumulado_subtotal,
            'iva': acumulado_iva,
            'total': acumulado_total
        }
    }
    return render(request, 'pagos/seleccionar_metodo.html', context)


@login_required
def procesar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos = pago.pedidos.all()

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
                    pago.save()
                    finalizar_pago(pago)
                    messages.success(request, "Pago procesado correctamente.")
                    return redirect('pagos:detalle_pago', pago_id=pago.id)
                except Exception as e:
                    messages.error(request, f"Error: {e}")
            else:
                messages.error(request, "Verificación facial requerida.")

        elif pago.metodo_pago == 'transferencia':
            codigo = request.POST.get('codigo_comprobante')
            imagen = request.FILES.get('foto_verificacion')
            if codigo and imagen:
                pago.codigo_comprobante = codigo
                pago.foto_verificacion = imagen
                pago.save()
                finalizar_pago(pago)
                messages.success(request, "Comprobante subido.")
                return redirect('pagos:detalle_pago', pago_id=pago.id)
            else:
                messages.error(request, "Faltan datos.")

    return render(request, f'pagos/pago_{pago.metodo_pago}.html', {'pago': pago, 'pedidos': pedidos})


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
    """
    Vista del recibo WEB con desglose completo.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos_raw = pago.pedidos.all()

    lista_detalles = []
    acumulado_iva = decimal.Decimal('0.00')
    acumulado_subtotal = decimal.Decimal('0.00')

    for pedido in pedidos_raw:
        datos = calcular_desglose_pedido(pedido)
        lista_detalles.append(datos)
        acumulado_iva += datos['fila_monto_iva']
        acumulado_subtotal += datos['fila_subtotal_base']

    return render(request, 'pagos/detalle_pago.html', {
        'pago': pago,
        'detalles': lista_detalles,
        'total_iva': acumulado_iva,
        'subtotal': acumulado_subtotal
    })


@login_required
def descargar_comprobante(request, pago_id):
    """
    Genera PDF con datos del cliente, vendedor y desglose de IVA.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    pedidos_raw = pago.pedidos.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{pago.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elementos = []

    # --- 1. ENCABEZADO Y DATOS DEL CLIENTE ---
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo.png')
    logo = Image(logo_path, width=60, height=60) if os.path.exists(logo_path) else Paragraph("", styles['Normal'])

    datos_cliente = f"""
    <b>CLIENTE:</b><br/>
    Nombre: {pago.usuario.first_name} {pago.usuario.last_name}<br/>
    Usuario: {pago.usuario.username}<br/>
    Email: {pago.usuario.email}<br/>
    Fecha: {pago.fecha_pago.strftime('%d/%m/%Y %H:%M') if pago.fecha_pago else timezone.now().strftime('%d/%m/%Y')}
    """

    tabla_header_data = [[logo, Paragraph("<b>FRIDA'S BABYS S.A.</b><br/>RUC: 0999999999001<br/>Matriz: Portoviejo, Ecuador", styles['Normal']), Paragraph(datos_cliente, styles['Normal'])]]
    tabla_header = Table(tabla_header_data, colWidths=[70, 200, 250])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
    ]))
    elementos.append(tabla_header)
    elementos.append(Spacer(1, 20))

    # --- 2. DETALLE DE PRODUCTOS ---
    data = [["Producto", "Vendedor", "Cant", "P. Base", "Desc.", "Subt.", "IVA", "Total"]]

    suma_subtotal = 0
    suma_iva = 0
    suma_total = 0

    for pedido in pedidos_raw:
        calc = calcular_desglose_pedido(pedido)

        # Obtenemos nombre del vendedor o "Sistema" si no tiene
        vendedor_obj = calc.get('vendedor')
        nombre_vendedor = vendedor_obj.username if vendedor_obj else "Sistema"

        data.append([
            Paragraph(calc['producto'].nombre, styles['Normal']),
            nombre_vendedor,
            str(calc['cantidad']),
            f"${calc['precio_base_unit']:.2f}",
            f"${calc['monto_desc_unit']:.2f}",
            f"${calc['fila_subtotal_base']:.2f}",
            f"${calc['fila_monto_iva']:.2f}",
            f"${calc['fila_total']:.2f}",
        ])

        suma_subtotal += calc['fila_subtotal_base']
        suma_iva += calc['fila_monto_iva']
        suma_total += calc['fila_total']

    # Filas de Totales
    data.append(["", "", "", "", "", "SUBTOTAL:", "", f"${suma_subtotal:.2f}"])
    data.append(["", "", "", "", "", "IVA (15%):", "", f"${suma_iva:.2f}"])
    data.append(["", "", "", "", "", "TOTAL:", "", f"${suma_total:.2f}"])

    tabla_detalle = Table(data, colWidths=[120, 60, 30, 50, 45, 50, 45, 60])
    tabla_detalle.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-3), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (-3,-3), (-1,-1), 1, colors.black),
    ]))
    elementos.append(tabla_detalle)

    elementos.append(Spacer(1, 30))
    texto_pie = Paragraph("Gracias por su compra. Documento generado electrónicamente.", styles['Italic'])
    elementos.append(texto_pie)

    doc.build(elementos)
    return response