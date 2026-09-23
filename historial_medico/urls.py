from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('', auth_views.dashboard, name='dashboard'),
    path('usuarios/', include('usuarios.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('medicos/', include('medicos.urls')),
    path('citas/', include('citas.urls')),
    path('consultas/', include('consultas.urls')),
    path('core/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Sistema Médico - Admin'
admin.site.site_title = 'Sistema Médico'
admin.site.index_title = 'Panel de Administración'
