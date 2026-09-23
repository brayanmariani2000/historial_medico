from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('SECRETARIA', 'Secretaria'),
        ('ANALISTA', 'Analista'),
        ('MEDICO', 'Médico'),
        ('ENFERMERA', 'Enfermera'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='SECRETARIA')
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_rol_display()})'

    @property
    def is_admin(self):
        return self.rol == 'ADMINISTRADOR'

    @property
    def is_secretaria(self):
        return self.rol == 'SECRETARIA'

    @property
    def is_analista(self):
        return self.rol == 'ANALISTA'

    @property
    def is_medico(self):
        return self.rol == 'MEDICO'

    @property
    def is_enfermera(self):
        return self.rol == 'ENFERMERA'
