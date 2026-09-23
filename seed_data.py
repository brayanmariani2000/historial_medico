import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'historial_medico.settings')
django.setup()

from core.models import (
    TipoSangre, TipoAlergia, TipoConsulta, EstadoCita, Etnia, 
    EspecialidadMedica, TipoDiscapacidad, Sintoma, TipoDocumento, CatTriageEsi
)
from usuarios.models import Usuario

def seed_data():
    print("Seeding catalog data...")
    
    # Tipo Sangre
    sangres = [
        ('A+', 'A', 'POSITIVO'), ('A-', 'A', 'NEGATIVO'),
        ('B+', 'B', 'POSITIVO'), ('B-', 'B', 'NEGATIVO'),
        ('AB+', 'AB', 'POSITIVO'), ('AB-', 'AB', 'NEGATIVO'),
        ('O+', 'O', 'POSITIVO'), ('O-', 'O', 'NEGATIVO'),
    ]
    for cod, grp, rh in sangres:
        TipoSangre.objects.get_or_create(codigo=cod, defaults={'grupo': grp, 'rh': rh})

    # Tipo Alergia
    alergias = ['MEDICAMENTO', 'ALIMENTO', 'AMBIENTAL', 'OTRO']
    for a in alergias:
        TipoAlergia.objects.get_or_create(nombre=a)

    # Tipo Consulta
    consultas = [
        ('PRIMERA_VEZ', 40), ('CONTROL', 20), ('URGENCIA', 30),
        ('EXAMEN', 15), ('TELEMEDICINA', 20)
    ]
    for nom, dur in consultas:
        TipoConsulta.objects.get_or_create(nombre=nom, defaults={'duracion_estimada_min': dur})

    # Estado Cita
    estados = [
        ('AGENDADA', 'azul', 'NO'), ('CONFIRMADA', 'verde', 'NO'),
        ('EN_CURSO', 'amarillo', 'NO'), ('COMPLETADA', 'gris', 'SI'),
        ('CANCELADA', 'rojo', 'SI'), ('NO_ASISTIO', 'naranja', 'SI'),
    ]
    for nom, col, fin in estados:
        EstadoCita.objects.get_or_create(nombre=nom, defaults={'color': col, 'es_final': fin})

    # Etnia
    etnias = ['Mestizo', 'Indígena', 'Afrodescendiente', 'Blanco', 'Otro']
    for e in etnias:
        Etnia.objects.get_or_create(nombre=e)

    # Especialidad
    especialidades = [
        ('MED-001', 'Medicina Interna', 'MEDICA'),
        ('MED-002', 'Cardiología', 'MEDICA'),
        ('PED-001', 'Pediatría', 'MEDICA'),
        ('CIR-001', 'Cirugía General', 'QUIRURGICA'),
        ('URG-001', 'Medicina de Urgencias', 'MEDICA'),
    ]
    for cod, nom, ram in especialidades:
        EspecialidadMedica.objects.get_or_create(codigo=cod, defaults={'nombre': nom, 'rama': ram})

    # Discapacidad
    discapacidades = ['FÍSICA', 'AUDITIVA', 'VISUAL', 'COGNITIVA', 'MÚLTIPLE']
    for d in discapacidades:
        TipoDiscapacidad.objects.get_or_create(nombre=d)

    # Sintoma
    sintomas = [
        ('Cefalea', 'Neurológico'), ('Fiebre', 'General'),
        ('Disnea', 'Respiratorio'), ('Dolor torácico', 'Cardiovascular'),
        ('Náuseas', 'Gastrointestinal'),
    ]
    for nom, cat in sintomas:
        Sintoma.objects.get_or_create(nombre=nom, defaults={'categoria': cat})

    # Tipo Documento
    documentos = [('V', 'VENEZOLANO'), ('E', 'EXTRANJERO'), ('P', 'PASAPORTE')]
    for cod, nom in documentos:
        TipoDocumento.objects.get_or_create(codigo=cod, defaults={'nombre': nom})

    # Triage
    triages = [
        (1, 'Nivel 1 (Emergencia)', 'Atención inmediata', 'danger'),
        (2, 'Nivel 2 (Muy Urgente)', 'Atención en 10-15 min', 'warning'),
        (3, 'Nivel 3 (Urgente)', 'Atención en 60 min', 'primary'),
        (4, 'Nivel 4 (Semi Urgente)', 'Atención en 120 min', 'success'),
        (5, 'Nivel 5 (No Urgente)', 'Atención en 240 min', 'info'),
    ]
    for niv, nom, desc, col in triages:
        CatTriageEsi.objects.get_or_create(nivel=niv, defaults={'nombre': nom, 'descripcion': desc, 'color': col})

    # Administrative User
    if not Usuario.objects.filter(username='admin').exists():
        Usuario.objects.create_superuser('admin', 'admin@example.com', 'admin123', rol='ADMINISTRADOR', first_name='Admin', last_name='Principal')
        print("Created superuser: admin / admin123")

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
