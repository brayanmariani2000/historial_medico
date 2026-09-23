from django.db import models


class Nombres(models.Model):
    TIPO_CHOICES = [('NOMBRE', 'Nombre'), ('APELLIDO', 'Apellido')]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'nombres'

    def __str__(self):
        return self.descripcion


class Etnia(models.Model):
    tipo_etnia = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'etnia'

    def __str__(self):
        return self.tipo_etnia


class Sangre(models.Model):
    tipo_sangre = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'sangre'

    def __str__(self):
        return self.tipo_sangre


class Direccion(models.Model):
    division_politica = models.CharField(max_length=50)
    divicion_politica = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    valor = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'direccion'

    def __str__(self):
        return f'{self.division_politica}: {self.valor}'


class Especialidad(models.Model):
    descripcion = models.CharField(max_length=30)
    estado = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'especialidad'

    def __str__(self):
        return self.descripcion


class Persona(models.Model):
    nombre = models.ForeignKey(Nombres, models.DO_NOTHING, related_name='personas_nombre')
    apellido = models.ForeignKey(Nombres, models.DO_NOTHING, related_name='personas_apellido')
    fecha_nacimiento = models.DateField()
    direccion = models.ForeignKey(Direccion, models.DO_NOTHING)
    sexo = models.CharField(max_length=5, blank=True, null=True)
    etnia = models.ForeignKey(Etnia, models.DO_NOTHING, blank=True, null=True)
    sangre = models.ForeignKey(Sangre, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'persona'

    def __str__(self):
        return f'{self.nombre.descripcion} {self.apellido.descripcion}'

    @property
    def nombre_completo(self):
        return f'{self.nombre.descripcion} {self.apellido.descripcion}'


class Identificacion(models.Model):
    persona = models.ForeignKey(Persona, models.CASCADE)
    descripcion = models.CharField(max_length=50)
    descripcion_padre = models.ForeignKey('self', models.DO_NOTHING, db_column='descripcion_id', blank=True, null=True)
    valor = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'identificacion'

    def __str__(self):
        return f'{self.descripcion}: {self.valor}'
