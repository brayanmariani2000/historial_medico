from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Medico, MedicoEspecialidad
from .forms import MedicoForm, MedicoEspecialidadForm, EspecialidadMedicaForm
from core.models import EspecialidadMedica


@login_required
def lista_especialidades(request):
    especialidades = EspecialidadMedica.objects.all()
    return render(request, 'medicos/especialidades/lista.html', {
        'especialidades': especialidades, 'page_title': 'Áreas de Salud / Especialidades'
    })


@login_required
def crear_especialidad(request):
    if not request.user.is_superuser and request.user.rol != 'ADMINISTRADOR':
        messages.error(request, 'No tienes permiso.')
        return redirect('medicos:lista_especialidades')
    form = EspecialidadMedicaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        esp = form.save()
        messages.success(request, 'Especialidad registrada.')
        return redirect('medicos:lista_especialidades')
    return render(request, 'medicos/especialidades/form.html', {
        'form': form, 'page_title': 'Nueva Especialidad', 'action': 'Registrar'
    })


@login_required
def editar_especialidad(request, pk):
    if not request.user.is_superuser and request.user.rol != 'ADMINISTRADOR':
        messages.error(request, 'No tienes permiso.')
        return redirect('medicos:lista_especialidades')
    obj = get_object_or_404(EspecialidadMedica, pk=pk)
    form = EspecialidadMedicaForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Especialidad actualizada.')
        return redirect('medicos:lista_especialidades')
    return render(request, 'medicos/especialidades/form.html', {
        'form': form, 'page_title': 'Editar Especialidad', 'action': 'Guardar'
    })


@login_required
def lista_medicos(request):
    medicos = Medico.objects.select_related(
        'id_persona__id_nombre', 'id_persona__id_apellido'
    ).prefetch_related('especialidades__id_especialidad').all()
    return render(request, 'medicos/lista.html', {'medicos': medicos, 'page_title': 'Médicos'})


@login_required
def detalle_medico(request, pk):
    medico = get_object_or_404(
        Medico.objects.select_related(
            'id_persona__id_nombre', 'id_persona__id_apellido'
        ).prefetch_related('especialidades__id_especialidad'), pk=pk
    )
    from citas.models import Cita
    citas_recientes = Cita.objects.filter(id_medico=medico).select_related(
        'id_persona__id_nombre', 'id_persona__id_apellido', 'id_estado_cita'
    ).order_by('-fecha_cita')[:10]
    return render(request, 'medicos/detalle.html', {
        'medico': medico, 'citas': citas_recientes, 'page_title': 'Detalle Médico'
    })


@login_required
def crear_medico(request):
    if request.user.rol != 'ADMINISTRADOR' and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('medicos:lista')
    form = MedicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        medico = form.save()
        messages.success(request, f'Médico {medico.nombre_completo} registrado.')
        return redirect('medicos:detalle', pk=medico.pk)
    return render(request, 'medicos/form.html', {
        'form': form, 'page_title': 'Nuevo Médico', 'action': 'Registrar'
    })


from django.db import transaction
from pacientes.forms import PersonaForm

@login_required
def registro_integral_medico(request):
    if not request.user.is_superuser and request.user.rol != 'ADMINISTRADOR':
        messages.error(request, 'No tienes permiso.')
        return redirect('medicos:lista')

    all_especialidades = EspecialidadMedica.objects.filter(activo='SI').order_by('nombre')
    nivel_choices = MedicoEspecialidad.NIVEL_CHOICES

    from usuarios.forms import UsuarioForm
    persona_form = PersonaForm(request.POST or None, prefix='persona')
    medico_form  = MedicoForm(request.POST or None, prefix='medico')
    
    # Pre-configure user form for MEDICO role
    initial_user = {'rol': 'MEDICO'}
    usuario_form = UsuarioForm(request.POST or None, prefix='usuario', initial=initial_user, hide_medico=False)
    # Bloquear el campo rol para que siempre sea médico
    usuario_form.fields['rol'].widget.attrs['disabled'] = True

    if request.method == 'POST':
        # Bypass validation for disabled field
        usuario_form_data = usuario_form.data.copy()
        usuario_form_data['usuario-rol'] = 'MEDICO'
        usuario_form.data = usuario_form_data

        if persona_form.is_valid() and medico_form.is_valid() and usuario_form.is_valid():
            try:
                with transaction.atomic():
                    persona = persona_form.save()
                    
                    # Create User
                    user = usuario_form.save(commit=False)
                    user.first_name = persona.id_nombre.nombre
                    user.last_name = persona.id_apellido.nombre
                    user.rol = 'MEDICO'
                    user.save()
                    
                    # Create Medico profile
                    medico = medico_form.save(commit=False)
                    medico.id_persona = persona
                    medico.usuario = user
                    medico.save()

                    # Guardar especialidades dinámicas enviadas
                    i = 0
                    while True:
                        esp_id   = request.POST.get(f'esp_especialidad_{i}')
                        esp_niv  = request.POST.get(f'esp_nivel_{i}')
                        esp_fech = request.POST.get(f'esp_fecha_{i}') or None
                        esp_inst = request.POST.get(f'esp_inst_{i}', '')
                        if not esp_id:
                            break
                        try:
                            especialidad = EspecialidadMedica.objects.get(pk=esp_id)
                            MedicoEspecialidad.objects.create(
                                id_medico=medico,
                                id_especialidad=especialidad,
                                nivel=esp_niv or 'ESPECIALISTA',
                                fecha_certificacion=esp_fech,
                                institucion=esp_inst,
                            )
                        except EspecialidadMedica.DoesNotExist:
                            pass
                        i += 1

                    messages.success(request, f'Médico {persona.nombre_completo} registrado con éxito y cuenta de usuario creada.')
                    return redirect('medicos:detalle', pk=medico.pk)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            error_details = []
            for field, errors in persona_form.errors.items():
                label = persona_form.fields[field].label if field in persona_form.fields else field
                error_details.append(f"{label}: {', '.join(errors)}")
            for field, errors in medico_form.errors.items():
                label = medico_form.fields[field].label if field in medico_form.fields else field
                error_details.append(f"{label}: {', '.join(errors)}")
            for field, errors in usuario_form.errors.items():
                label = usuario_form.fields[field].label if field in usuario_form.fields else field
                error_details.append(f"{label}: {', '.join(errors)}")
            
            if error_details:
                messages.error(request, f"Errores de validación: {' | '.join(error_details)}")
            else:
                messages.error(request, 'Por favor verifica los errores en el formulario.')

    return render(request, 'medicos/registro_integral.html', {
        'persona_form': persona_form,
        'medico_form': medico_form,
        'usuario_form': usuario_form,
        'all_especialidades': all_especialidades,
        'nivel_choices': nivel_choices,
        'page_title': 'Registro Integral de Médico',
    })


@login_required
def editar_medico(request, pk):
    if request.user.rol != 'ADMINISTRADOR' and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('medicos:lista')
    medico = get_object_or_404(Medico, pk=pk)
    form = MedicoForm(request.POST or None, instance=medico)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Datos del médico actualizados.')
        return redirect('medicos:detalle', pk=pk)
    return render(request, 'medicos/form.html', {
        'form': form, 'page_title': 'Editar Médico', 'action': 'Guardar', 'medico': medico
    })


@login_required
@require_POST
def toggle_especialidad(request, pk):
    """AJAX: activa o desactiva una especialidad médica. Solo ADMINISTRADOR."""
    if not request.user.is_superuser and request.user.rol != 'ADMINISTRADOR':
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    esp = get_object_or_404(EspecialidadMedica, pk=pk)
    nuevo_estado = 'NO' if esp.activo == 'SI' else 'SI'
    esp.activo = nuevo_estado
    esp.save()

    accion = 'activada' if nuevo_estado == 'SI' else 'desactivada'

    return JsonResponse({
        'ok': True,
        'activo': nuevo_estado,
        'nombre': esp.nombre,
    })
