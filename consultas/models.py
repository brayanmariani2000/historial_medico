from django.db import models
from citas.models import Cita
from core.models import Sintoma


class ConsultaMedica(models.Model):
    ESTADO_CHOICES = [
        ('COMPLETADA', 'Completada'),
        ('PENDIENTE', 'Pendiente'),
        ('CANCELADA', 'Cancelada'),
        ('DERIVADA', 'Derivada'),
    ]
    id_consulta = models.AutoField(primary_key=True)
    id_cita = models.OneToOneField(
        Cita, on_delete=models.CASCADE, db_column='id_cita',
        related_name='consulta', verbose_name='Cita'
    )
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    presion_arterial = models.CharField(max_length=20, blank=True, null=True, verbose_name='Presión Arterial')
    frecuencia_cardiaca = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Frecuencia Cardíaca (lpm)')
    frecuencia_respiratoria = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Frecuencia Respiratoria')
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name='Temperatura (°C)')
    saturacion_oxigeno = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Saturación O₂ (%)')
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Peso (kg)')
    talla = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Talla (cm)')
    examen_fisico = models.TextField(blank=True, null=True, verbose_name='Examen Físico')
    tratamiento_prescrito = models.TextField(blank=True, null=True, verbose_name='Tratamiento Prescrito')
    recomendaciones = models.TextField(blank=True, null=True, verbose_name='Recomendaciones')
    proxima_cita = models.DateField(blank=True, null=True, verbose_name='Próxima Cita')
    duracion_minutos = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Duración (min)')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='COMPLETADA')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consulta_medica'
        verbose_name = 'Consulta Médica'
        ordering = ['-fecha_consulta']

    def __str__(self):
        return f'Consulta #{self.id_consulta} - {self.id_cita.id_persona}'

    @property
    def imc(self):
        if self.peso and self.talla and self.talla > 0:
            talla_m = self.talla / 100
            return round(float(self.peso) / (float(talla_m) ** 2), 2)
        return None


class ConsultaSintoma(models.Model):
    id_consulta = models.ForeignKey(
        ConsultaMedica, on_delete=models.CASCADE, db_column='id_consulta',
        related_name='sintomas'
    )
    id_sintoma = models.ForeignKey(
        Sintoma, on_delete=models.PROTECT, db_column='id_sintoma'
    )
    intensidad = models.PositiveSmallIntegerField(blank=True, null=True, help_text='1-10')
    duracion_dias = models.PositiveSmallIntegerField(blank=True, null=True)
    es_principal = models.BooleanField(default=False, verbose_name='Es Principal')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'consulta_sintoma'
        unique_together = ('id_consulta', 'id_sintoma')
        verbose_name = 'Síntoma de Consulta'

    def __str__(self):
        return f'{self.id_sintoma} - Consulta #{self.id_consulta_id}'


class ConsultaDiagnostico(models.Model):
    TIPO_CHOICES = [
        ('PRESUNTIVO', 'Presuntivo'),
        ('DEFINITIVO', 'Definitivo'),
        ('DIFERENCIAL', 'Diferencial'),
    ]
    id_consulta = models.ForeignKey(
        ConsultaMedica, on_delete=models.CASCADE, db_column='id_consulta',
        related_name='diagnosticos'
    )
    enfermedad = models.CharField(max_length=200, verbose_name='Enfermedad / Diagnóstico')
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES, default='DEFINITIVO')
    es_principal = models.CharField(max_length=2, choices=[('SI', 'SI'), ('NO', 'NO')], default='NO')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'consulta_diagnostico'
        verbose_name = 'Diagnóstico'

    def __str__(self):
        return f'{self.enfermedad} ({self.tipo})'
