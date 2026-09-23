from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Decorator to restrict views by user role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles and not request.user.is_superuser:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class RoleRequiredMixin:
    """Mixin for class-based views to restrict by role."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol not in self.allowed_roles and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
