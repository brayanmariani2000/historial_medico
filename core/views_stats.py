from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from pacientes.models import Persona, PersonaAlergia, PersonaDiscapacidad
from medicos.models import Medico
from citas.models import Cita
from consultas.models import ConsultaDiagnostico, ConsultaMedica
from core.models import EspecialidadMedica, Parroquia
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import json
import csv
from datetime import date, timedelta, datetime


def _add_months(d, months):
    """Shift a date by N months safely, handling month-end edge cases."""
    import calendar
    m = d.month + months
    y = d.year + (m - 1) // 12
    m = ((m - 1) % 12) + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return d.replace(year=y, month=m, day=day)


def _parse_dates(request):
    """Extrae start_date y end_date del request. GET o POST"""
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_str:
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_str:
        try:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    return start_date, end_date


@login_required
def dashboard_estadisticas(request):
    start_date, end_date = _parse_dates(request)
    
    # Base queries with optional date filters
    qs_personas = Persona.objects.all()
    qs_citas = Cita.objects.all()
    qs_consultas = ConsultaMedica.objects.all()
    qs_diagnosticos = ConsultaDiagnostico.objects.all()
    
    if start_date:
        qs_personas = qs_personas.filter(fecha_registro__date__gte=start_date)
        qs_citas = qs_citas.filter(fecha_cita__date__gte=start_date)
        qs_consultas = qs_consultas.filter(fecha_consulta__gte=start_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__gte=start_date)
        
    if end_date:
        qs_personas = qs_personas.filter(fecha_registro__date__lte=end_date)
        qs_citas = qs_citas.filter(fecha_cita__date__lte=end_date)
        qs_consultas = qs_consultas.filter(fecha_consulta__lte=end_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__lte=end_date)

    # --- BASIC COUNTS ---
    total_pacientes = qs_personas.count()
    total_medicos = Medico.objects.count() # Médicos usually aren't filtered by date for KPI
    total_citas = qs_citas.count()
    total_consultas = qs_consultas.count()
    
    # --- AGE GROUPS ---
    today = date.today()
    age_groups = {
        '0-12 (Niños)': 0,
        '13-17 (Adolescentes)': 0,
        '18-59 (Adultos)': 0,
        '60+ (Mayores)': 0
    }
    for p in qs_personas:
        age = p.edad
        if age <= 12: age_groups['0-12 (Niños)'] += 1
        elif age <= 17: age_groups['13-17 (Adolescentes)'] += 1
        elif age <= 59: age_groups['18-59 (Adultos)'] += 1
        else: age_groups['60+ (Mayores)'] += 1
    
    age_labels = list(age_groups.keys())
    age_data = list(age_groups.values())

    # --- GEOGRAPHIC DISTRIBUTION (Parroquia) ---
    parroquia_stats = qs_personas.exclude(parroquia__isnull=True)\
        .values('parroquia__parroquia')\
        .annotate(total=Count('id_persona'))\
        .order_by('-total')[:10]
    loc_labels = [p['parroquia__parroquia'] or "Desconocida" for p in parroquia_stats]
    loc_data = [p['total'] for p in parroquia_stats]

    # --- PATHOLOGIES (Top 10 Diagnoses) ---
    top_diagnoses = qs_diagnosticos.values('enfermedad')\
        .annotate(total=Count('id_consulta'))\
        .order_by('-total')[:10]
    diag_labels = [d['enfermedad'] for d in top_diagnoses]
    diag_data = [d['total'] for d in top_diagnoses]

    # --- COMORBIDITIES AND RISKS ---
    alergias_count = PersonaAlergia.objects.filter(id_persona__in=qs_personas).count()
    discapacidades_count = PersonaDiscapacidad.objects.filter(id_persona__in=qs_personas).count()
    
    # Sex Distribution
    sexo_stats = qs_personas.values('sexo').annotate(total=Count('id_persona'))
    sexo_labels = [item['sexo'] for item in sexo_stats]
    sexo_data = [item['total'] for item in sexo_stats]

    # Citas by Specialty
    citas_por_especialidad = qs_citas.values('id_medico__especialidades__id_especialidad__nombre')\
        .annotate(total=Count('id_cita'))\
        .order_by('-total')[:8]
    espec_labels = [
        item['id_medico__especialidades__id_especialidad__nombre'] or "General"
        for item in citas_por_especialidad
    ]
    espec_data = [item['total'] for item in citas_por_especialidad]

    # --- MONTHLY TREND (last 12 months, unaffected by general date filter to preserve the line chart) ---
    trend_months = []
    trend_citas = []
    trend_consultas = []
    MONTH_ES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    
    for i in range(11, -1, -1):
        month_start = _add_months(today.replace(day=1), -i)
        month_end   = _add_months(month_start, 1)
        label = f"{MONTH_ES[month_start.month - 1]} {month_start.year}"
        c_citas = Cita.objects.filter(
            fecha_cita__date__gte=month_start,
            fecha_cita__date__lt=month_end
        ).count()
        c_consultas = ConsultaMedica.objects.filter(
            fecha_consulta__gte=month_start,
            fecha_consulta__lt=month_end
        ).count()
        trend_months.append(label)
        trend_citas.append(c_citas)
        trend_consultas.append(c_consultas)

    context = {
        'page_title': 'Analítica Médica Total',
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
        'total_pacientes': total_pacientes,
        'total_medicos': total_medicos,
        'total_citas': total_citas,
        'total_consultas': total_consultas,
        'alergias_count': alergias_count,
        'discapacidades_count': discapacidades_count,
        # JSON Data for Charts
        'age_json': json.dumps(age_labels),
        'age_data_json': json.dumps(age_data),
        'loc_json': json.dumps(loc_labels),
        'loc_data_json': json.dumps(loc_data),
        'diag_json': json.dumps(diag_labels),
        'diag_data_json': json.dumps(diag_data),
        'sexo_json': json.dumps(sexo_labels),
        'sexo_data_json': json.dumps(sexo_data),
        'espec_json': json.dumps(espec_labels),
        'espec_data_json': json.dumps(espec_data),
        'trend_months_json': json.dumps(trend_months),
        'trend_citas_json': json.dumps(trend_citas),
        'trend_consultas_json': json.dumps(trend_consultas),
    }
    
    return render(request, 'core/estadisticas.html', context)


@login_required
def drilldown_api(request):
    """API for fetching drilldown details."""
    type_req = request.GET.get('type')
    value = request.GET.get('value')
    start_date, end_date = _parse_dates(request)
    
    # Base queries
    qs_personas = Persona.objects.all().select_related('id_tipo_documento', 'id_nombre', 'id_apellido')
    qs_citas = Cita.objects.all().select_related('id_persona', 'id_persona__id_nombre', 'id_persona__id_apellido', 'id_medico', 'id_estado_cita')
    qs_diagnosticos = ConsultaDiagnostico.objects.all().select_related('id_consulta', 'id_consulta__id_cita__id_persona', 'id_consulta__id_cita__id_persona__id_nombre', 'id_consulta__id_cita__id_persona__id_apellido')
    
    if start_date:
        qs_personas = qs_personas.filter(fecha_registro__date__gte=start_date)
        qs_citas = qs_citas.filter(fecha_cita__date__gte=start_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__gte=start_date)
    if end_date:
        qs_personas = qs_personas.filter(fecha_registro__date__lte=end_date)
        qs_citas = qs_citas.filter(fecha_cita__date__lte=end_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__lte=end_date)

    data = []
    headers = []
    title = ""

    if type_req == 'diagnostico':
        title = f"Pacientes con {value}"
        headers = ['Paciente', 'Cédula', 'Fecha Consulta', 'Observaciones']
        items = qs_diagnosticos.filter(enfermedad=value)
        for item in items:
            persona = item.id_consulta.id_cita.id_persona
            data.append([
                persona.nombre_completo,
                persona.numero_documento,
                item.id_consulta.fecha_consulta.strftime('%d/%m/%Y'),
                item.observaciones or '-'
            ])
            
    elif type_req == 'sexo':
        title = f"Pacientes (Sexo: {value})"
        headers = ['Paciente', 'Cédula', 'Edad', 'Fecha Registro']
        items = qs_personas.filter(sexo=value)
        for p in items:
            data.append([p.nombre_completo, p.numero_documento, p.edad, p.fecha_registro.strftime('%d/%m/%Y') if p.fecha_registro else '-'])
            
    elif type_req == 'especialidad':
        title = f"Citas de Especialidad: {value}"
        headers = ['Fecha', 'Paciente', 'Médico', 'Estado']
        # If value is General, maybe it's unassigned or we use icontains
        if value == 'General':
            items = qs_citas.filter(id_medico__especialidades__isnull=True)
        else:
            items = qs_citas.filter(id_medico__especialidades__id_especialidad__nombre=value)
            
        for c in items:
            data.append([
                c.fecha_cita.strftime('%d/%m/%Y %I:%M %p'),
                c.id_persona.nombre_completo,
                str(c.id_medico),
                c.id_estado_cita.nombre if c.id_estado_cita else '-'
            ])
            
    elif type_req == 'loc':
        title = f"Pacientes de la parroquia: {value}"
        headers = ['Paciente', 'Cédula', 'Teléfono', 'Edad']
        if value == 'Desconocida':
            items = qs_personas.filter(parroquia__isnull=True)
        else:
            items = qs_personas.filter(parroquia__parroquia=value)
        for p in items:
            data.append([p.nombre_completo, p.numero_documento, p.telefono or '-', p.edad])
            
    elif type_req == 'edad':
        title = f"Pacientes en rango de edad: {value}"
        headers = ['Paciente', 'Cédula', 'Edad', 'Sexo']
        items = []
        for p in qs_personas:
            age = p.edad
            if value == '0-12 (Niños)' and age <= 12: items.append(p)
            elif value == '13-17 (Adolescentes)' and 13 <= age <= 17: items.append(p)
            elif value == '18-59 (Adultos)' and 18 <= age <= 59: items.append(p)
            elif value == '60+ (Mayores)' and age >= 60: items.append(p)
            
        for p in items:
            data.append([p.nombre_completo, p.numero_documento, p.edad, p.sexo])

    context = {
        'title': title,
        'headers': headers,
        'data': data
    }
    
    html = render_to_string('core/partials/drilldown_table.html', context)
    return JsonResponse({'html': html})


@login_required
def exportar_excel_api(request):
    """Exporta las métricas a CSV"""
    start_date, end_date = _parse_dates(request)
    
    response = HttpResponse(content_type='text/csv')
    response.write('\ufeff'.encode('utf8')) # BOM for Excel
    filename = f"Reporte_Consolidado_{timezone.now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Titulo y Fechas
    writer.writerow(['REPORTE CONSOLIDADO DE ESTADÍSTICAS MÉDICAS'])
    if start_date or end_date:
        writer.writerow(['Filtro:', f'Desde {start_date or "Inicio"} hasta {end_date or "Hoy"}'])
    else:
        writer.writerow(['Filtro:', 'Histórico completo'])
    
    writer.writerow([])
    
    # Base queries
    qs_personas = Persona.objects.all()
    qs_citas = Cita.objects.all()
    qs_consultas = ConsultaMedica.objects.all()
    qs_diagnosticos = ConsultaDiagnostico.objects.all()
    
    if start_date:
        qs_personas = qs_personas.filter(fecha_registro__date__gte=start_date)
        qs_citas = qs_citas.filter(fecha_cita__date__gte=start_date)
        qs_consultas = qs_consultas.filter(fecha_consulta__gte=start_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__gte=start_date)
    if end_date:
        qs_personas = qs_personas.filter(fecha_registro__date__lte=end_date)
        qs_citas = qs_citas.filter(fecha_cita__date__lte=end_date)
        qs_consultas = qs_consultas.filter(fecha_consulta__lte=end_date)
        qs_diagnosticos = qs_diagnosticos.filter(id_consulta__fecha_consulta__lte=end_date)

    # 1. KPIs
    writer.writerow(['--- INDICADORES PRINCIPALES ---'])
    writer.writerow(['Total Pacientes', qs_personas.count()])
    writer.writerow(['Total Médicos Activos', Medico.objects.filter(estado='ACTIVO').count()])
    writer.writerow(['Total Citas Registradas', qs_citas.count()])
    writer.writerow(['Total Consultas Realizadas', qs_consultas.count()])
    writer.writerow([])
    
    # 2. Top Diagnósticos
    writer.writerow(['--- TOP ENFERMEDADES / DIAGNÓSTICOS ---'])
    writer.writerow(['Enfermedad', 'Cantidad de Casos'])
    top_diagnoses = qs_diagnosticos.values('enfermedad').annotate(total=Count('id_consulta')).order_by('-total')[:20]
    for d in top_diagnoses:
        writer.writerow([d['enfermedad'], d['total']])
    writer.writerow([])
    
    # 3. Citas por Especialidad
    writer.writerow(['--- CITAS POR ESPECIALIDAD ---'])
    writer.writerow(['Especialidad', 'Cantidad'])
    citas_por_especialidad = qs_citas.values('id_medico__especialidades__id_especialidad__nombre').annotate(total=Count('id_cita')).order_by('-total')
    for c in citas_por_especialidad:
        writer.writerow([c['id_medico__especialidades__id_especialidad__nombre'] or 'General', c['total']])

    return response
