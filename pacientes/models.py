from django.db import models


class Paciente(models.Model):
    persona = models.ForeignKey('core.Persona', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'paciente'

    def __str__(self):
        return str(self.persona)


class AntecedentesSalud(models.Model):
    descrip = models.CharField(max_length=20)
    antecedente_salud_id = models.IntegerField()
    valor = models.CharField(max_length=20)
    paciente = models.ForeignKey(Paciente, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'antecedentes_salud'

    def __str__(self):
        return f'{self.descrip}: {self.valor}'
