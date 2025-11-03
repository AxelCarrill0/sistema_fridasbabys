from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class UsuarioCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('nombre', 'email', 'telefono', 'direccion', 'rol')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'})
        }


class UsuarioChangeForm(UserChangeForm):
    password = forms.CharField(
        label='Nueva Contraseña (Dejar vacío para no cambiar)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'nombre', 'telefono', 'direccion', 'rol', 'is_active', 'is_staff',
                  'is_superuser')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rol': forms.Select(attrs={'class': 'form-control'})
        }


class ClienteRegistrationForm(UserCreationForm):
    """
    Formulario para el registro público de nuevos usuarios con rol fijo 'cliente'.
    Se excluye el campo 'password' del modelo base para evitar duplicidad.
    """

    # Se mantiene el email como requerido (ya que AbstractUser no lo requiere por defecto)
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'nombre', 'email', 'telefono', 'direccion')
        exclude = ('rol', 'password',)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # En esta parte reescribimos el rol a cliente
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'
        if commit:
            user.save()
        return user