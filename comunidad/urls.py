# comunidad/urls.py
from django.urls import path
from comunidad.views import usuario_crear, usuario_eliminar, usuario_editar, lista_registro_horario, crear_registro_horario, lista_solicitud_permiso, crear_solicitud_permiso, dashboard_empleado, dashboard_administrador, actualizar_datos


urlpatterns = [
    path("usuarios/", usuario_crear, name='usuarios'),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario-eliminar"),
    path("usuarios/editar/<int:pk>/", usuario_editar, name="usuario-editar"),
    path("registro_horario/", lista_registro_horario, name='registro_horario_list'),
    path("registro_horario/nuevo/", crear_registro_horario, name='registro_horario_create'),
    path("solicitud_permiso/", lista_solicitud_permiso, name='solicitud_permiso_list'),
    path("solicitud_permiso/nuevo/", crear_solicitud_permiso, name='solicitud_permiso_create'),
    path('dashboard/empleado/', dashboard_empleado, name='dashboard_empleado'),
    path('dashboard/administrador/', dashboard_administrador, name='dashboard_administrador'),
    path("actualizar_datos/", actualizar_datos, name='actualizar_datos'),
    
]