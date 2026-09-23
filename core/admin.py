from django.contrib import admin
from .models import (
    TipoDocumento, TipoSangre, TipoAlergia, TipoDiscapacidad, TipoContacto,
    TipoConsulta, EstadoCita, Etnia, EspecialidadMedica, Sintoma, CatTriageEsi,
    Municipio, Parroquia, Sector
)

admin.site.register(TipoDocumento)
admin.site.register(TipoSangre)
admin.site.register(TipoAlergia)
admin.site.register(TipoDiscapacidad)
admin.site.register(TipoContacto)
admin.site.register(TipoConsulta)
admin.site.register(EstadoCita)
admin.site.register(Etnia)
admin.site.register(EspecialidadMedica)
admin.site.register(Sintoma)
admin.site.register(CatTriageEsi)
admin.site.register(Municipio)
admin.site.register(Parroquia)
admin.site.register(Sector)
