from django.urls import path
from . import views_ajax, views_stats

app_name = 'core'

urlpatterns = [
    path('estadisticas/', views_stats.dashboard_estadisticas, name='estadisticas'),
    path('estadisticas/drilldown/', views_stats.drilldown_api, name='stats_drilldown'),
    path('estadisticas/exportar/', views_stats.exportar_excel_api, name='exportar_estadisticas'),

    path('ajax/parroquias/', views_ajax.get_parroquias, name='get_parroquias'),
    path('ajax/sectores/', views_ajax.get_sectores, name='get_sectores'),
    path('ajax/calles/', views_ajax.get_calles, name='get_calles'),
    path('ajax/crear-sector/', views_ajax.crear_sector, name='crear_sector'),
    path('ajax/crear-calle/', views_ajax.crear_calle, name='crear_calle'),
    path('ajax/medicos-por-especialidad/', views_ajax.get_medicos_por_especialidad, name='get_medicos_por_especialidad'),
    path('ajax/disponibilidad-fecha/', views_ajax.get_disponibilidad_fecha, name='get_disponibilidad_fecha'),
]
