from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from datetime import date
from .models import Cita
from .forms import CitaForm, CitaEstadoForm
from core.models import EstadoCita


@login_required
def lista_citas(request):
    q      = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    fecha  = request.GET.get('fecha', '')
    citas  = Cita.objects.select_related(
        'id_persona__id_nombre', 'id_persona__id_apellido',
        'id_medico__id_persona__id_nombre', 'id_medico__id_persona__id_apellido',
        'id_estado_cita', 'id_tipo_consulta'
    ).order_by('-fecha_cita')
    if q:
        citas = citas.filter(
            Q(id_persona__numero_documento__icontains=q) |
            Q(id_persona__id_nombre__nombre__icontains=q) |
            Q(id_persona__id_apellido__nombre__icontains=q)
        )
    if estado:
        citas = citas.filter(id_estado_cita__nombre=estado)
    if fecha:
        citas = citas.filter(fecha_cita__date=fecha)
    estados = EstadoCita.objects.all()
    return render(request, 'citas/lista.html', {
        'citas': citas, 'estados': estados, 'q': q,
        'estado_sel': estado, 'fecha_sel': fecha, 'page_title': 'Citas'
    })


@login_required
def detalle_cita(request, pk):
    cita = get_object_or_404(
        Cita.objects.select_related(
            'id_persona__id_nombre', 'id_persona__id_apellido',
            'id_medico__id_persona__id_nombre', 'id_medico__id_persona__id_apellido',
            'id_estado_cita', 'id_tipo_consulta'
        ), pk=pk
    )
    tiene_consulta = hasattr(cita, 'consulta')
    estados = EstadoCita.objects.all()
    return render(request, 'citas/detalle.html', {
        'cita': cita, 'tiene_consulta': tiene_consulta,
        'estados': estados, 'page_title': 'Detalle Cita'
    })


@login_required
def crear_cita(request):
    if request.user.rol not in ['ADMINISTRADOR', 'SECRETARIA'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('citas:lista')
    form = CitaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cita = form.save(commit=False)
        cita.id_estado_cita = EstadoCita.objects.get(nombre='AGENDADA')
        cita.save()
        messages.success(request, 'Cita agendada correctamente.')
        return redirect('citas:detalle', pk=cita.pk)
    return render(request, 'citas/form.html', {
        'form': form, 'page_title': 'Nueva Cita', 'action': 'Agendar'
    })


@login_required
def editar_cita(request, pk):
    if request.user.rol not in ['ADMINISTRADOR', 'SECRETARIA'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('citas:lista')
    cita = get_object_or_404(Cita, pk=pk)
    form = CitaForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cita actualizada.')
        return redirect('citas:detalle', pk=pk)
    return render(request, 'citas/form.html', {
        'form': form, 'page_title': 'Editar Cita', 'action': 'Guardar', 'cita': cita
    })


@login_required
def cambiar_estado_cita(request, pk):
    if request.user.rol not in ['ADMINISTRADOR', 'SECRETARIA', 'MEDICO'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('citas:lista')
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        nuevo_estado_id = request.POST.get('id_estado_cita')
        motivo = request.POST.get('motivo_cancelacion', '')
        try:
            estado = EstadoCita.objects.get(pk=nuevo_estado_id)
            cita.id_estado_cita = estado
            if estado.nombre == 'CANCELADA':
                cita.fecha_cancelacion = timezone.now()
                cita.motivo_cancelacion = motivo
            elif estado.nombre == 'CONFIRMADA':
                cita.fecha_confirmacion = timezone.now()
            cita.save()
            messages.success(request, f'Estado de cita actualizado a: {estado.nombre}')
        except EstadoCita.DoesNotExist:
            messages.error(request, 'Estado inválido.')
    return redirect('citas:detalle', pk=pk)


@login_required
def pacientes_por_area_ajax(request):
    """AJAX — pacientes con cita HOY en un área de consulta (solo SECRETARIA)."""
    if request.user.rol not in ['SECRETARIA'] and not request.user.is_superuser:
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    area_id = request.GET.get('area_id')
    if not area_id:
        return JsonResponse({'error': 'Falta area_id'}, status=400)

    hoy = date.today()
    estados_activos = ['AGENDADA', 'CONFIRMADA']

    citas = Cita.objects.filter(
        fecha_cita__date=hoy,
        id_medico__especialidades__id_especialidad=area_id,
        id_estado_cita__nombre__in=estados_activos,
    ).select_related(
        'id_persona__id_nombre',
        'id_persona__id_apellido',
        'id_medico__id_persona__id_nombre',
        'id_medico__id_persona__id_apellido',
        'id_estado_cita',
    ).order_by('fecha_cita')

    data = []
    for c in citas:
        p = c.id_persona
        data.append({
            'cita_id':              c.pk,
            'hora':                 c.fecha_cita.strftime('%H:%M'),
            'nombre':               f'{p.id_nombre.nombre} {p.id_apellido.nombre}',
            'documento':            p.numero_documento,
            'sexo':                 p.sexo,
            'edad':                 p.edad,
            'telefono':             p.telefono or '—',
            'estado':               c.id_estado_cita.nombre,
            'medico':               str(c.id_medico),
            'url_detalle_paciente': f'/pacientes/{p.pk}/',
            'url_detalle_cita':     f'/citas/{c.pk}/',
        })

    return JsonResponse({'pacientes': data, 'total': len(data)})


import csv
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import datetime
from core.models import EspecialidadMedica, EstadoCita
from fpdf import FPDF
import io

@login_required
def atencion_area(request, area_id):
    if request.user.rol not in ['SECRETARIA', 'ADMINISTRADOR'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para ver esta área.')
        return redirect('dashboard')
        
    area = get_object_or_404(EspecialidadMedica, pk=area_id)
    
    # Rango de fecha para SQLite timezone fix
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    
    citas = Cita.objects.filter(
        fecha_cita__gte=start_of_day,
        fecha_cita__lt=end_of_day,
        id_medico__especialidades__id_especialidad=area,
    ).select_related(
        'id_persona__id_nombre',
        'id_persona__id_apellido',
        'id_estado_cita'
    ).order_by('fecha_cita')
    
    return render(request, 'citas/atencion_area.html', {
        'page_title': f'Atención del Día: {area.nombre}',
        'area': area,
        'citas': citas,
        'hoy': timezone.now()
    })

@login_required
def reporte_area_csv(request, area_id):
    area = get_object_or_404(EspecialidadMedica, pk=area_id)
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    
    citas = Cita.objects.filter(
        fecha_cita__gte=start_of_day, fecha_cita__lt=end_of_day,
        id_medico__especialidades__id_especialidad=area
    ).order_by('fecha_cita')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Reporte_{area.nombre}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Hora', 'Paciente', 'Cedula', 'Telefono', 'Estado'])
    
    for c in citas:
        p = c.id_persona
        writer.writerow([
            c.fecha_cita.strftime('%H:%M'),
            f"{p.id_nombre.nombre} {p.id_apellido.nombre}",
            p.numero_documento,
            p.telefono or 'N/A',
            c.id_estado_cita.nombre
        ])
    return response

@login_required
def reporte_area_pdf(request, area_id):
    area = get_object_or_404(EspecialidadMedica, pk=area_id)
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    
    citas = Cita.objects.filter(
        fecha_cita__gte=start_of_day, fecha_cita__lt=end_of_day,
        id_medico__especialidades__id_especialidad=area
    ).order_by('fecha_cita')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Reporte de Citas Diarias - {area.nombre}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Fecha: {timezone.now().strftime("%d/%m/%Y")}', ln=True, align='C')
    pdf.ln(10)
    
    # Headers
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(20, 10, 'Hora', border=1)
    pdf.cell(70, 10, 'Paciente', border=1)
    pdf.cell(30, 10, 'Cedula', border=1)
    pdf.cell(30, 10, 'Telefono', border=1)
    pdf.cell(40, 10, 'Estado', border=1, ln=True)
    
    pdf.set_font('Arial', '', 10)
    for c in citas:
        p = c.id_persona
        # encode to latin-1 avoiding unicode err in basic FPDF fonts
        paciente = f"{p.id_nombre.nombre} {p.id_apellido.nombre}".encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(20, 10, c.fecha_cita.strftime('%H:%M'), border=1)
        pdf.cell(70, 10, paciente[:30], border=1)
        pdf.cell(30, 10, p.numero_documento, border=1)
        pdf.cell(30, 10, (p.telefono or 'N/A')[:15], border=1)
        pdf.cell(40, 10, c.id_estado_cita.nombre, border=1, ln=True)
        
    output_string = pdf.output(dest='S')
    # Depending on fpdf version, output() might return bytes directly or a latin-1 string.
    pdf_bytes = output_string.encode('latin-1') if isinstance(output_string, str) else bytes(output_string)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Reporte_{area.nombre}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response

@login_required
def actualizar_estado_cita(request, cita_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    cita = get_object_or_404(Cita, pk=cita_id)
    nuevo_estado = request.POST.get('estado')
    motivo = request.POST.get('motivo', '').strip()
    
    if nuevo_estado == 'COMPLETADA':
        st, created = EstadoCita.objects.get_or_create(nombre='COMPLETADA')
        cita.id_estado_cita = st
        cita.save()
        return JsonResponse({'success': True, 'msg': 'Cita confirmada (Completada)'})
        
    elif nuevo_estado == 'CANCELADA':
        st = EstadoCita.objects.get(nombre='CANCELADA')
        cita.id_estado_cita = st
        cita.fecha_cancelacion = timezone.now()
        cita.motivo_cancelacion = motivo
        cita.save()
        return JsonResponse({'success': True, 'msg': 'Cita cancelada correctamente'})
        
    return JsonResponse({'error': 'Estado inválido'}, status=400)
