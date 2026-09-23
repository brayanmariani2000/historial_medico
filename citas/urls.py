from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.lista_citas, name='lista'),
    path('<int:pk>/', views.detalle_cita, name='detalle'),
    path('nueva/', views.crear_cita, name='crear'),
    path('<int:pk>/editar/', views.editar_cita, name='editar'),
    path('<int:pk>/estado/', views.cambiar_estado_cita, name='cambiar_estado'),
    path('ajax/pacientes-area/', views.pacientes_por_area_ajax, name='pacientes_por_area'),
    
    # Nuevas rutas para Secretaria / Atención por Área
    path('area/<int:area_id>/', views.atencion_area, name='atencion_area'),
    path('area/<int:area_id>/pdf/', views.reporte_area_pdf, name='reporte_area_pdf'),
    path('area/<int:area_id>/csv/', views.reporte_area_csv, name='reporte_area_csv'),
    path('area/actualizar-estado/<int:cita_id>/', views.actualizar_estado_cita, name='actualizar_estado'),
]
