from django.contrib import admin
from .models import Persona, Nombre, PersonaAlergia, PersonaContacto


class PersonaAlergiaInline(admin.TabularInline):
    model = PersonaAlergia
    extra = 0


class PersonaContactoInline(admin.TabularInline):
    model = PersonaContacto
    extra = 0


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombre_completo', 'fecha_nacimiento', 'sexo', 'telefono')
    search_fields = ('numero_documento', 'id_nombre__nombre', 'id_apellido__nombre')
    inlines = [PersonaAlergiaInline, PersonaContactoInline]

admin.site.register(Nombre)
