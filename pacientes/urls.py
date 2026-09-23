from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista_pacientes, name='lista'),
    path('<int:pk>/', views.detalle_paciente, name='detalle'),
    path('nuevo/', views.crear_paciente, name='crear'),
    path('buscar/', views.buscar_pacientes_ajax, name='buscar_ajax'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar'),
]
