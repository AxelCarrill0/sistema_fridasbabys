"""
Formularios de la aplicación Productos.
"""

from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos.
    """
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'precio_base', 'ganancia',
            'stock', 'categoria', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ganancia': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
