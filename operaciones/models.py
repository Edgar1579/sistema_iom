# operaciones/models.py
from django.db import models

def get_image_filename(instance, filename):
    return f'anuncios/{instance.titulo}/{filename}'

class Anuncio(models.Model):
    ACCION_CHOICES = [
        ('publicado', 'Publicado'),
        ('borrador', 'Borrador'),
    ]

    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to=get_image_filename, blank=True, null=True, default="operaciones/anuncios/anuncio.jpg")
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    anuncio = models.ForeignKey('self', verbose_name="Anuncio", on_delete=models.CASCADE, null=True, blank=True, related_name='subanuncios')
    estado = models.BooleanField(default=True)
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES, default='borrador')  # Nuevo campo

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ['-fecha_publicacion']
