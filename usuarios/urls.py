from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('crear-integral/', views.crear_integral_usuario, name='crear_integral'),
    path('<int:pk>/', views.detalle_usuario, name='detalle'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/cambiar-password/', views.cambiar_password_usuario, name='cambiar_password'),
    path('<int:pk>/toggle/', views.toggle_usuario, name='toggle_usuario'),
]
