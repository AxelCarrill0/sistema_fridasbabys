from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Agregamos 'descuento' a los campos
        fields = [
            'nombre', 'descripcion', 'precio_base', 'ganancia', 
            'descuento', 'stock', 'categoria', 'activo', 'imagen'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ganancia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'Ej: 10 para 10% OFF'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }