from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ConsultaMedica, ConsultaSintoma, ConsultaDiagnostico
from .forms import ConsultaMedicaForm, ConsultaSintomaForm, ConsultaDiagnosticoForm
from citas.models import Cita


@login_required
def lista_consultas(request):
    consultas = ConsultaMedica.objects.select_related(
        'id_cita__id_persona__id_nombre', 'id_cita__id_persona__id_apellido',
        'id_cita__id_medico__id_persona__id_nombre', 'id_cita__id_medico__id_persona__id_apellido'
    ).order_by('-fecha_consulta')
    return render(request, 'consultas/lista.html', {'consultas': consultas, 'page_title': 'Consultas Médicas'})


@login_required
def detalle_consulta(request, pk):
    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            'id_cita__id_persona__id_nombre', 'id_cita__id_persona__id_apellido',
            'id_cita__id_medico__id_persona__id_nombre', 'id_cita__id_medico__id_persona__id_apellido'
        ).prefetch_related('sintomas__id_sintoma', 'diagnosticos'), pk=pk
    )
    return render(request, 'consultas/detalle.html', {'consulta': consulta, 'page_title': 'Detalle Consulta'})


@login_required
def crear_consulta(request, cita_id):
    if request.user.rol not in ['ADMINISTRADOR', 'MEDICO', 'ENFERMERA'] and not request.user.is_superuser:
        messages.error(request, 'Solo el personal médico, enfermeras o administradores pueden registrar consultas.')
        return redirect('citas:detalle', pk=cita_id)
    cita = get_object_or_404(Cita, pk=cita_id)
    if hasattr(cita, 'consulta'):
        messages.info(request, 'Esta cita ya tiene una consulta registrada.')
        return redirect('consultas:detalle', pk=cita.consulta.pk)
    form = ConsultaMedicaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        consulta = form.save(commit=False)
        consulta.id_cita = cita
        consulta.save()
        # Procesar síntomas
        sint_prin_ids = request.POST.getlist('sintomas_prin_list[]')
        for s_id in sint_prin_ids:
            if s_id.isdigit():
                ConsultaSintoma.objects.get_or_create(id_consulta=consulta, id_sintoma_id=s_id, defaults={'es_principal': True})
                
        sint_sec_ids = request.POST.getlist('sintomas_sec_list[]')
        for s_id in sint_sec_ids:
            if s_id.isdigit():
                ConsultaSintoma.objects.get_or_create(id_consulta=consulta, id_sintoma_id=s_id, defaults={'es_principal': False})
        
        # Procesar antecedentes
        from pacientes.models import PersonaAntecedente
        for cat in ['FAMILIAR', 'PERSONAL', 'QUIRURGICO']:
            ant_ids = request.POST.getlist(f'antecedentes_{cat.lower()}_list[]')
            for a_id in ant_ids:
                if a_id.isdigit():
                    PersonaAntecedente.objects.get_or_create(id_persona=cita.id_persona, id_antecedente_id=a_id)

        from core.models import EstadoCita
        try:
            cita.id_estado_cita = EstadoCita.objects.get(nombre='COMPLETADA')
            cita.save()
        except EstadoCita.DoesNotExist:
            pass
        messages.success(request, 'Consulta registrada exitosamente.')
        return redirect('consultas:detalle', pk=consulta.pk)
    from core.models import Sintoma, Antecedente
    return render(request, 'consultas/form.html', {
        'form': form, 'cita': cita, 'page_title': 'Nueva Consulta', 'action': 'Registrar',
        'sintomas_db': Sintoma.objects.all(),
        'antecedentes_familiares_db': Antecedente.objects.filter(categoria='FAMILIAR'),
        'antecedentes_personales_db': Antecedente.objects.filter(categoria='PERSONAL'),
        'antecedentes_quirurgicos_db': Antecedente.objects.filter(categoria='QUIRURGICO'),
    })


@login_required
def historial_paciente(request, persona_id):
    from pacientes.models import Persona
    paciente = get_object_or_404(Persona, pk=persona_id)
    consultas = ConsultaMedica.objects.filter(
        id_cita__id_persona=paciente
    ).select_related(
        'id_cita__id_medico__id_persona__id_nombre',
        'id_cita__id_medico__id_persona__id_apellido',
        'id_cita__id_tipo_consulta'
    ).prefetch_related('sintomas__id_sintoma', 'diagnosticos').order_by('-fecha_consulta')
    return render(request, 'consultas/historial.html', {
        'paciente': paciente, 'consultas': consultas, 'page_title': 'Historial Médico'
    })


@login_required
def crear_sintoma_ajax(request):
    if request.method == 'POST':
        from core.models import Sintoma
        nombre = request.POST.get('nombre', '').strip().upper()
        if nombre:
            sintoma, created = Sintoma.objects.get_or_create(nombre=nombre)
            return JsonResponse({'success': True, 'id': sintoma.pk, 'nombre': sintoma.nombre})
    return JsonResponse({'success': False})


@login_required
def crear_antecedente_ajax(request):
    if request.method == 'POST':
        from core.models import Antecedente
        nombre = request.POST.get('nombre', '').strip().upper()
        categoria = request.POST.get('categoria', '').strip().upper()
        if nombre and categoria in ['FAMILIAR', 'PERSONAL', 'QUIRURGICO']:
            antecedente, created = Antecedente.objects.get_or_create(nombre=nombre, categoria=categoria)
            return JsonResponse({'success': True, 'id': antecedente.pk, 'nombre': antecedente.nombre, 'categoria': antecedente.categoria})
    return JsonResponse({'success': False})
