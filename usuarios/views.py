from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Usuario
from .forms import LoginForm, UsuarioForm, UsuarioEditForm, UsuarioPasswordForm
from .mixins import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Bienvenido(a), {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    from citas.models import Cita
    from pacientes.models import Persona
    from medicos.models import Medico
    from django.utils import timezone
    from datetime import date

    today = date.today()
    citas_hoy_lista = Cita.objects.filter(fecha_cita__date=today).select_related(
        'id_persona__id_nombre', 'id_persona__id_apellido',
        'id_medico__id_persona__id_nombre', 'id_medico__id_persona__id_apellido',
        'id_estado_cita'
    ).order_by('fecha_cita')

    # Si es Medico, solo ve sus citas de hoy
    if request.user.rol == 'MEDICO':
        try:
            medico = request.user.medico_perfil
            citas_hoy_lista = citas_hoy_lista.filter(id_medico=medico)
        except Exception:
            citas_hoy_lista = citas_hoy_lista.none()

    context = {
        'total_pacientes': Persona.objects.filter(activo=True).count(),
        'total_medicos': Medico.objects.filter(estado='ACTIVO').count(),
        'citas_hoy_count': Cita.objects.filter(fecha_cita__date=today).count(),
        'citas_pendientes_global': Cita.objects.filter(
            id_estado_cita__nombre__in=['AGENDADA', 'CONFIRMADA']
        ).count(),
        'citas_hoy_lista': citas_hoy_lista,
        'page_title': 'Dashboard',
    }

    # Para SECRETARIA: áreas médicas (Especialidades) con conteo de pacientes pendientes hoy
    if request.user.rol == 'SECRETARIA':
        from core.models import EspecialidadMedica
        COLORES = [
            {'bg': 'linear-gradient(135deg,#1a6db0,#2563eb)', 'badge': '#dbeafe', 'badge_text': '#1e40af', 'icon_color': '#3b82f6'},
            {'bg': 'linear-gradient(135deg,#0d9488,#059669)', 'badge': '#d1fae5', 'badge_text': '#065f46', 'icon_color': '#10b981'},
            {'bg': 'linear-gradient(135deg,#7c3aed,#9333ea)', 'badge': '#ede9fe', 'badge_text': '#5b21b6', 'icon_color': '#8b5cf6'},
            {'bg': 'linear-gradient(135deg,#dc2626,#ea580c)', 'badge': '#fee2e2', 'badge_text': '#991b1b', 'icon_color': '#ef4444'},
            {'bg': 'linear-gradient(135deg,#b45309,#d97706)', 'badge': '#fef3c7', 'badge_text': '#92400e', 'icon_color': '#f59e0b'},
            {'bg': 'linear-gradient(135deg,#0e7490,#0284c7)', 'badge': '#e0f2fe', 'badge_text': '#0c4a6e', 'icon_color': '#0ea5e9'},
        ]
        from django.utils import timezone
        import datetime
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + datetime.timedelta(days=1)

        areas_raw = EspecialidadMedica.objects.filter(activo='SI').order_by('nombre')
        areas_consulta = []
        for i, area in enumerate(areas_raw):
            count = Cita.objects.filter(
                fecha_cita__gte=start_of_day,
                fecha_cita__lt=end_of_day,
                id_medico__especialidades__id_especialidad=area,
                id_estado_cita__nombre__in=['AGENDADA', 'CONFIRMADA'],
            ).count()
            color = COLORES[i % len(COLORES)]
            areas_consulta.append({
                'id':     area.pk,
                'nombre': area.nombre,
                'count':  count,
                'color':  color,
            })
        context['areas_consulta'] = areas_consulta

    return render(request, 'dashboard.html', context)


# ── Gestión de Usuarios ────────────────────────────────────────────────────────

@login_required
@role_required('ADMINISTRADOR')
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios, 'page_title': 'Usuarios del Sistema'})


@login_required
@role_required('ADMINISTRADOR')
def detalle_usuario(request, pk):
    """Vista de detalle de un usuario con toda su información."""
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detalle.html', {
        'usuario': usuario,
        'page_title': f'Perfil — {usuario.get_full_name() or usuario.username}',
    })


@login_required
@role_required('ADMINISTRADOR')
def crear_usuario(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('usuarios:lista')
    return render(request, 'usuarios/form.html', {'form': form, 'page_title': 'Crear Usuario', 'action': 'Crear'})


@login_required
@role_required('ADMINISTRADOR')
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioEditForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('usuarios:detalle', pk=pk)
    return render(request, 'usuarios/form_editar.html', {
        'form': form,
        'usuario': usuario,
        'page_title': f'Editar — {usuario.get_full_name() or usuario.username}',
        'action': 'Guardar Cambios',
    })


@login_required
@role_required('ADMINISTRADOR')
def cambiar_password_usuario(request, pk):
    """Cambia la contraseña de un usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario.set_password(form.cleaned_data['password1'])
        usuario.save()
        messages.success(request, f'Contraseña de {usuario.username} actualizada correctamente.')
        return redirect('usuarios:detalle', pk=pk)
    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
        'usuario': usuario,
        'page_title': f'Cambiar Contraseña — {usuario.get_full_name() or usuario.username}',
    })


@login_required
@require_POST
def toggle_usuario(request, pk):
    """AJAX: activa o desactiva un usuario. Solo ADMINISTRADOR."""
    from django.http import JsonResponse
    if not request.user.is_superuser and request.user.rol != 'ADMINISTRADOR':
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    user_obj = get_object_or_404(Usuario, pk=pk)
    
    # Prevenir que un admin se desactive a sí mismo
    if user_obj.pk == request.user.pk:
         return JsonResponse({'error': 'No puedes desactivar tu propia cuenta.'}, status=400)

    nuevo_estado = not user_obj.activo
    user_obj.activo = nuevo_estado
    user_obj.save()
    accion = 'activado' if nuevo_estado else 'desactivado'

    return JsonResponse({
        'ok': True,
        'activo': nuevo_estado,
        'username': user_obj.username,
    })


# ── Registro Integral ─────────────────────────────────────────────────────────

from pacientes.forms import PersonaForm
from django.db import transaction


@login_required
@role_required('ADMINISTRADOR')
def crear_integral_usuario(request):
    persona_form = PersonaForm(request.POST or None, prefix='persona')
    usuario_form = UsuarioForm(request.POST or None, prefix='usuario')

    if request.method == 'POST':
        if persona_form.is_valid() and usuario_form.is_valid():
            try:
                with transaction.atomic():
                    persona = persona_form.save()
                    user = usuario_form.save(commit=False)
                    user.first_name = persona.id_nombre.nombre
                    user.last_name = persona.id_apellido.nombre
                    user.save()
                    messages.success(request, f'Personal {user.get_full_name()} registrado y cuenta creada.')
                    return redirect('usuarios:lista')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            errors = []
            for field, errs in list(persona_form.errors.items()) + list(usuario_form.errors.items()):
                errors.append(f"{field}: {', '.join(errs)}")
            if errors:
                messages.error(request, f"Errores: {' | '.join(errors)}")

    return render(request, 'usuarios/registrar_integral.html', {
        'persona_form': persona_form,
        'usuario_form': usuario_form,
        'page_title': 'Registro Integral de Personal',
        'action': 'Registrar'
    })
