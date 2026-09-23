from django.urls import path
from . import views

app_name = 'consultas'

urlpatterns = [
    path('', views.lista_consultas, name='lista'),
    path('<int:pk>/', views.detalle_consulta, name='detalle'),
    path('cita/<int:cita_id>/nueva/', views.crear_consulta, name='crear'),
    path('paciente/<int:persona_id>/historial/', views.historial_paciente, name='historial'),
    path('ajax/crear-sintoma/', views.crear_sintoma_ajax, name='crear_sintoma_ajax'),
    path('ajax/crear-antecedente/', views.crear_antecedente_ajax, name='crear_antecedente_ajax'),
]
