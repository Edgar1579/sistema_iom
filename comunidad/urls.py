# comunidad/urls.py
from django.urls import path
from comunidad.views import (
       usuario_crear,
       usuario_eliminar,
       usuario_editar,
       registrar_horas,
       lista_registros,
       detalle_registro,
       verificar_tipo_dia,
       lista_solicitud_permiso,
       crear_solicitud_permiso,
       edit_group,
       panel_inicio
        # Asegúrate de que esta línea esté aquí
   )

urlpatterns = [
    path("usuarios/", usuario_crear, name='usuarios'),
    path("usuarios/eliminar/<int:pk>/", usuario_eliminar, name="usuario-eliminar"),
    path("usuarios/editar/<int:pk>/", usuario_editar, name="usuario-editar"),
    path('registro/crear/', registrar_horas, name='registrar'),
    path('horas/', lista_registros, name='lista_registros'),
    path('horas/<int:pk>/', detalle_registro, name='detalle_registro'),
    path('ajax/verificar-tipo-dia/', verificar_tipo_dia, name='verificar_tipo_dia'),
    path('panel/', panel_inicio, name='panel_inicio'),
    path("solicitud_permiso/", lista_solicitud_permiso, name='solicitud_permiso_list'),
    path("solicitud_permiso/nuevo/", crear_solicitud_permiso, name='solicitud_permiso_create'),
    path('usuarios/roles/', edit_group, name='create_group'),
    path('usuarios/roles/<int:group_id>/', edit_group, name='edit_group'),
   
    
]