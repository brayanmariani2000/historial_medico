from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Persona, PersonaAlergia, PersonaContacto, PersonaDiscapacidad, Nombre
from .forms import PersonaForm, PersonaAlergiaForm, PersonaContactoForm


@login_required
def lista_pacientes(request):
    q = request.GET.get('q', '')
    pacientes = Persona.objects.select_related(
        'id_nombre', 'id_apellido', 'id_tipo_sangre', 'id_tipo_documento'
    ).filter(activo=True)
    if q:
        pacientes = pacientes.filter(
            Q(numero_documento__icontains=q) |
            Q(id_nombre__nombre__icontains=q) |
            Q(id_apellido__nombre__icontains=q)
        )
    return render(request, 'pacientes/lista.html', {
        'pacientes': pacientes, 'q': q, 'page_title': 'Pacientes'
    })


@login_required
def detalle_paciente(request, pk):
    paciente = get_object_or_404(
        Persona.objects.select_related(
            'id_nombre', 'id_apellido', 'id_tipo_sangre', 'id_tipo_documento'
        ).prefetch_related('alergias', 'contactos', 'discapacidades'), pk=pk
    )
    from citas.models import Cita
    citas = Cita.objects.filter(id_persona=paciente).select_related(
        'id_medico__id_persona__id_nombre', 'id_medico__id_persona__id_apellido',
        'id_estado_cita', 'id_tipo_consulta'
    ).order_by('-fecha_cita')[:10]
    return render(request, 'pacientes/detalle.html', {
        'paciente': paciente, 'citas': citas, 'page_title': 'Detalle Paciente'
    })


from django.db import transaction
from citas.forms import CitaForm

@login_required
def crear_paciente(request):
    if request.user.rol not in ['ADMINISTRADOR', 'SECRETARIA'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('pacientes:lista')
        
    form = PersonaForm(request.POST or None, prefix='persona')
    cita_form = CitaForm(request.POST or None, prefix='cita')
    
    # We assign id_persona manually after creating the patient, so we ignore it in Cita validation
    cita_form.fields.pop('id_persona', None)

    if request.method == 'POST':
        if form.is_valid() and cita_form.is_valid():
            try:
                with transaction.atomic():
                    paciente = form.save()
                    cita = cita_form.save(commit=False)
                    cita.id_persona = paciente
                    from core.models import EstadoCita
                    cita.id_estado_cita = EstadoCita.objects.get(nombre='AGENDADA')
                    cita.save()
                    messages.success(request, f'Paciente {paciente.nombre_completo} registrado y cita agendada con éxito.')
                    return redirect('pacientes:detalle', pk=paciente.pk)
            except Exception as e:
                messages.error(request, f'Error al registrar: {str(e)}')
        else:
            messages.error(request, 'Por favor verifica los errores en el formulario.')

    return render(request, 'pacientes/form.html', {
        'form': form, 'cita_form': cita_form, 'page_title': 'Nuevo Paciente', 'action': 'Registrar'
    })

@login_required
def editar_paciente(request, pk):
    if request.user.rol not in ['ADMINISTRADOR', 'SECRETARIA'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('pacientes:lista')
    paciente = get_object_or_404(Persona, pk=pk)
    form = PersonaForm(request.POST or None, instance=paciente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Datos del paciente actualizados.')
        return redirect('pacientes:detalle', pk=pk)
    return render(request, 'pacientes/form.html', {
        'form': form, 'page_title': 'Editar Paciente', 'action': 'Guardar', 'paciente': paciente
    })

@login_required
def buscar_pacientes_ajax(request):
    """Endpoint AJAX para búsqueda en tiempo real de pacientes (máx. 8 resultados)."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'pacientes': [], 'total': 0})

    qs = Persona.objects.select_related(
        'id_nombre', 'id_apellido', 'id_tipo_documento', 'id_tipo_sangre'
    ).filter(activo=True).filter(
        Q(numero_documento__icontains=q) |
        Q(id_nombre__nombre__icontains=q) |
        Q(id_apellido__nombre__icontains=q)
    )[:8]

    data = []
    for p in qs:
        data.append({
            'id': p.pk,
            'nombre': p.nombre_completo,
            'documento': p.numero_documento,
            'tipo_doc': p.id_tipo_documento.codigo if p.id_tipo_documento else 'CI',
            'edad': p.edad,
            'sexo': p.sexo,
            'telefono': p.telefono or '—',
            'tipo_sangre': p.id_tipo_sangre.codigo if p.id_tipo_sangre else '—',
            'url_detalle': f'/pacientes/{p.pk}/',
        })
    return JsonResponse({'pacientes': data, 'total': len(data)})
