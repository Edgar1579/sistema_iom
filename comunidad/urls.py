# comunidad/urls.py
from django.urls import path
from comunidad.views import (
       usuario_crear,
       usuario_eliminar,
       usuario_editar,
       registrar_horas,
       lista_registros,
       lista_solicitud_permiso,
       crear_solicitud_permiso,
       dashboard_empleado,
       dashboard_administrador,
       actualizar_datos,
       edit_group
        # Asegúrate de que esta línea esté aquí
   )

urlpatterns = [
    path("usuarios/", usuario_crear, name='usuarios'),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario-eliminar"),
    path("usuarios/editar/<int:pk>/", usuario_editar, name="usuario-editar"),
    path('registrar/', registrar_horas, name='registrar_horas'),
    path('mis-registros/', lista_registros, name='lista_registros'),
    path("solicitud_permiso/", lista_solicitud_permiso, name='solicitud_permiso_list'),
    path("solicitud_permiso/nuevo/", crear_solicitud_permiso, name='solicitud_permiso_create'),
    path('dashboard/empleado/', dashboard_empleado, name='dashboard_empleado'),
    path('dashboard/administrador/', dashboard_administrador, name='dashboard_administrador'),
    path("actualizar_datos/", actualizar_datos, name='actualizar_datos'),
    path('usuarios/roles/', edit_group, name='create_group'),
    path('usuarios/roles/<int:group_id>/', edit_group, name='edit_group'),
   
    
]