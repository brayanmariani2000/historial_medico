from django.db import models
from pacientes.models import Persona
from medicos.models import Medico
from core.models import EstadoCita, TipoConsulta, CatTriageEsi


class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(
        Persona, on_delete=models.PROTECT, db_column='id_persona',
        related_name='citas', verbose_name='Paciente'
    )
    id_medico = models.ForeignKey(
        Medico, on_delete=models.PROTECT, db_column='id_medico',
        related_name='citas', verbose_name='Médico'
    )
    id_estado_cita = models.ForeignKey(
        EstadoCita, on_delete=models.PROTECT, db_column='id_estado_cita',
        verbose_name='Estado'
    )
    id_tipo_consulta = models.ForeignKey(
        TipoConsulta, on_delete=models.PROTECT, db_column='id_tipo_consulta',
        verbose_name='Tipo de Consulta'
    )
    id_triage = models.ForeignKey(
        CatTriageEsi, on_delete=models.SET_NULL, db_column='id_triage',
        null=True, blank=True, verbose_name='Triage'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_cita = models.DateTimeField(verbose_name='Fecha y Hora de la Cita')
    motivo_consulta = models.TextField(blank=True, null=True, verbose_name='Motivo de Consulta')
    observaciones = models.TextField(blank=True, null=True)
    fecha_confirmacion = models.DateTimeField(blank=True, null=True)
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    motivo_cancelacion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'cita'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha_cita']

    def __str__(self):
        return f'Cita #{self.id_cita} - {self.id_persona} ({self.fecha_cita.strftime("%d/%m/%Y %H:%M")})'
