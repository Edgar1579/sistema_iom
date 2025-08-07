from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base.views import principal, principal_admin, logout_user
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URLs principales
    path('admin/', admin.site.urls),
    path('', principal, name='index'),
    path('base/', principal, name='base'),
    path('adm/', principal_admin, name='index-admin'),
    
    # URLs de aplicaciones
    path('comunidad/', include('comunidad.urls')),
    path('operaciones/', include('operaciones.urls')),
    path('configuracion/', include('configuracion.urls')),
    
    # URLs de autenticación personalizadas
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    
    
# URLs de restablecimiento de contraseña con nombres personalizados
path('reiniciar/', auth_views.PasswordResetView.as_view(), name='pass_reset'),
path('reiniciar/enviado/', auth_views.PasswordResetDoneView.as_view(), name='pass_reset_done'),
path('reiniciar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='pass_reset_confirm'),
path('reiniciar/completado/', auth_views.PasswordResetCompleteView.as_view(), name='pass_reset_complete'),
]

# Solo para desarrollo: sirve archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)