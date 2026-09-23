from django.urls import path
from . import views

app_name = 'medicos'

urlpatterns = [
    path('', views.lista_medicos, name='lista'),
    path('<int:pk>/', views.detalle_medico, name='detalle'),
    path('nuevo/', views.crear_medico, name='crear'),
    path('crear-integral/', views.registro_integral_medico, name='crear_integral'),
    path('<int:pk>/editar/', views.editar_medico, name='editar'),
    path('especialidades/', views.lista_especialidades, name='lista_especialidades'),
    path('especialidades/nueva/', views.crear_especialidad, name='crear_especialidad'),
    path('especialidades/<int:pk>/editar/', views.editar_especialidad, name='editar_especialidad'),
    path('especialidades/<int:pk>/toggle/', views.toggle_especialidad, name='toggle_especialidad'),
]
