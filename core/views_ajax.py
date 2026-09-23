from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Parroquia, Municipio, EspecialidadMedica, Sector, Calle
from medicos.models import Medico
from citas.models import Cita
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
import json

@login_required
def get_parroquias(request):
    municipio_id = request.GET.get('municipio_id')
    parroquias = Parroquia.objects.filter(municipio_id=municipio_id).values('parroquia_id', 'parroquia')
    return JsonResponse(list(parroquias), safe=False)

@login_required
def get_sectores(request):
    parroquia_id = request.GET.get('parroquia_id')
    sectores = Sector.objects.filter(parroquia_id=parroquia_id).values('id_sector', 'sector')
    return JsonResponse(list(sectores), safe=False)

@login_required
def get_calles(request):
    sector_id = request.GET.get('sector_id')
    calles = Calle.objects.filter(sector_id=sector_id).values('id_calle', 'calle')
    return JsonResponse(list(calles), safe=False)

@login_required
@require_POST
def crear_sector(request):
    try:
        data = json.loads(request.body)
        parroquia_id = data.get('parroquia_id')
        nombre = data.get('nombre')
        if not parroquia_id or not nombre:
            return JsonResponse({'error': 'Faltan datos'}, status=400)
        
        parroquia = Parroquia.objects.get(pk=parroquia_id)
        sector = Sector.objects.create(sector=nombre, parroquia=parroquia)
        return JsonResponse({'id': sector.pk, 'nombre': sector.sector})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def crear_calle(request):
    try:
        data = json.loads(request.body)
        sector_id = data.get('sector_id')
        nombre = data.get('nombre')
        if not sector_id or not nombre:
            return JsonResponse({'error': 'Faltan datos'}, status=400)
        
        sector = Sector.objects.get(pk=sector_id)
        calle = Calle.objects.create(calle=nombre, sector=sector)
        return JsonResponse({'id': calle.pk, 'nombre': calle.calle})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_medicos_por_especialidad(request):
    especialidad_id = request.GET.get('especialidad_id')
    medicos = Medico.objects.filter(
        especialidades__id_especialidad_id=especialidad_id,
        estado='ACTIVO'
    ).select_related('id_persona__id_nombre', 'id_persona__id_apellido')
    
    data = [
        {
            'id': m.pk,
            'nombre': f"{m.id_persona.id_nombre.nombre} {m.id_persona.id_apellido.nombre}"
        } for m in medicos
    ]
    return JsonResponse(data, safe=False)

@login_required
def get_disponibilidad_fecha(request):
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    fecha = parse_date(fecha_str)
    if not fecha:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    count = Cita.objects.filter(fecha_cita__date=fecha).exclude(id_estado_cita__nombre='CANCELADA').count()
    return JsonResponse({'count': count})
