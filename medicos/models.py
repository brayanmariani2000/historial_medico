from django.db import models


class Medico(models.Model):
    persona = models.ForeignKey('core.Persona', models.CASCADE)
    especialidad = models.ForeignKey('core.Especialidad', models.DO_NOTHING)
    estado = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'medico'

    def __str__(self):
        return f'Dr(a). {self.persona}'

    @property
    def nombre_completo(self):
        return str(self.persona)
