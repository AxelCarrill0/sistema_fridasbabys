from django.db import models
from datetime import datetime

class Employes(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', default='Sin nombre')
    dni = models.CharField(max_length=10, unique=True, verbose_name='Cedula')
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro')
    date_creation = models.DateField(auto_now=True)
    date_updated = models.DateField(auto_now_add=True)
    age = models.PositiveIntegerField(default=0, verbose_name='Edad')
    salary = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Salario')
    state = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', null= True, blank=True, verbose_name='Imagen')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        db_table = 'empleado'
        ordering = ['id']