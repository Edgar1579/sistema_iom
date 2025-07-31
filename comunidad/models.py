from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model
from django.utils import timezone
import holidays

def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.documento}.{ext}"
    return f"comunidad/usuarios/{filename}"
# Create your models here.
class Usuario(models.Model):
    primer_nombre= models.CharField(max_length=45,verbose_name="Primer Nombre")
    segundo_nombre= models.CharField(max_length=45,verbose_name="Segundo Nombre", blank=True,null=True)

    primer_apellido= models.CharField(max_length=45,verbose_name="Primer Apellido")
    segundo_apellido= models.CharField(max_length=45,verbose_name="Segundo Apellido")
    
    fecha_nacimiento= models.DateField(verbose_name="Fecha de Nacimiento")
    imagen = models.ImageField(upload_to=get_image_filename, blank=True, null=True,default="comunidad\default-user.jpeg")
    correo = models.EmailField(max_length=50, verbose_name="Correo")
    
    class TipoDocumento(models.TextChoices):
        CEDULA='CC',_("Cédula")
        CEDULA_EXTRANJERIA='CE',_("Cédula de Extrangería")
    tipo_documento=models.CharField(max_length=2,choices=TipoDocumento.choices,verbose_name="Tipo de Documento")
    documento= models.PositiveIntegerField(verbose_name="Documento", unique=True)
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    estado=models.BooleanField(default=True)
    departamento = models.CharField(max_length=50, verbose_name="Departamento", blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    cargo = models.CharField(max_length=50, verbose_name="Cargo", blank=True, null=True)
    def clean(self):
        self.primer_nombre= self.primer_nombre.title()
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"
    class Meta:
        verbose_name_plural="Usuarios"
    @property
    def full_name(self):
        if self.segundo_nombre:
            return f"{self.primer_nombre} {self.segundo_nombre} {self.primer_apellido} {self.segundo_apellido}"
        else:
            return f"{self.primer_nombre} {self.primer_apellido} {self.segundo_apellido}"
    def usuario_activo(self):
        if self.estado:
            return Usuario.objects.filter(usuario=self, estado=True)
        else:
            return Usuario.objects.none()

class RegistroHoras(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    horas_normales_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_normales_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_nocturno = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_dominical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_festivo = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def es_domingo(self):
        return self.fecha.weekday() == 6  # domingo es el día 6

    def es_festivo(self):
        colombia_holidays = holidays.Colombia()
        return self.fecha in colombia_holidays  # Verifica si la fecha es festiva

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida <= entrada:
            raise ValidationError("La hora de salida debe ser posterior a la hora de entrada.")

        # Definir límites horarios
        inicio_diurno = time(6, 0)  # 6:00 AM
        fin_diurno = time(19, 0)    # 7:00 PM

        # Calcular horas trabajadas
        total_horas = (salida - entrada).total_seconds() / 3600

        if self.es_domingo() or self.es_festivo():
            self.calcular_horas_dominical_festivo(entrada, salida)
        else:
            self.calcular_horas_normales(entrada, salida)

    def calcular_pago_total(self):
        pago = 0
        # Horas normales
        pago += self.horas_normales_diurnas * 6.189  # Ejemplo: $10,000 por hora normal
        pago += self.horas_normales_nocturnas * 6.189 * 1.35  # 35% recargo nocturno

        # Horas extras
        if self.es_domingo() or self.es_festivo():
            recargo = 0.80 if self.es_domingo() else 0.80  # 80% recargo
            pago += self.horas_extras_diurnas * 6.189 * (1 + recargo)
            pago += self.horas_extras_nocturnas * 6.189 * (1 + recargo + 0.35)  # 35% recargo nocturno
        else:
            pago += self.horas_extras_diurnas * 6.189 * 1.25  # 25% recargo extra diurno
            pago += self.horas_extras_nocturnas * 6.189 * 1.75  # 75% recargo extra nocturno

        return pago

    def save(self, *args, **kwargs):
        if self.hora_salida <= self.hora_entrada:
            raise ValueError("La hora de salida debe ser posterior a la hora de entrada.")
        self.calcular_horas()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

    def calcular_horas_normales(self, entrada, salida):
        fin_diurno = entrada.replace(hour=19, minute=0)  # 7:00 PM

        if salida <= fin_diurno:
            self.horas_normales_diurnas = (salida - entrada).total_seconds() / 3600
        else:
            self.horas_normales_diurnas = (fin_diurno - entrada).total_seconds() / 3600
            self.horas_normales_nocturnas = (salida - fin_diurno).total_seconds() / 3600

    def calcular_horas_dominical_festivo(self, entrada, salida):
        fin_diurno = entrada.replace(hour=19, minute=0)  # 7:00 PM
        horas_totales = (salida - entrada).total_seconds() / 3600

        if salida <= fin_diurno:
            self.horas_normales_diurnas = horas_totales
        else:
            self.horas_normales_diurnas = (fin_diurno - entrada).total_seconds() / 3600
            self.horas_normales_nocturnas = (salida - fin_diurno).total_seconds() / 3600

class SolicitudPermiso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permisos')
    fecha = models.DateField(default=timezone.now)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    documento_identidad = models.CharField(max_length=20, blank=True, verbose_name="Documento de identidad")
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.get_estado_display()}"

class CalculoJornada:
    def __init__(self, fecha, hora_entrada, hora_salida):
        self.fecha = fecha
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
        self.horas_normales_diurnas = 0
        self.horas_normales_nocturnas = 0
        self.horas_extras_diurnas = 0
        self.horas_extras_nocturnas = 0
        self.recargo_dominical = 0
        self.recargo_festivo = 0
        self.recargo_nocturno = 0

    def es_festivo(self):
        festivos = [
            datetime(2023, 1, 1).date(),  # Año Nuevo
            datetime(2023, 12, 25).date(),  # Navidad
        ]
        return self.fecha in festivos

    def es_dominical(self):
        return self.fecha.weekday() == 6  # 6 es domingo

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida <= entrada:
            raise ValidationError("La hora de salida debe ser después de la hora de entrada.")

        # Definir límites horarios
        hora_limite_diurna = entrada.replace(hour=19, minute=0)  # 7 PM
        hora_limite_nocturna = entrada.replace(hour=6, minute=0) + timedelta(days=1)  # 6 AM del día siguiente

        # Calcular horas normales y extras
        if salida <= hora_limite_diurna:
            self.horas_normales_diurnas = (salida - entrada).total_seconds() / 3600
        else:
            self.horas_normales_diurnas = (hora_limite_diurna - entrada).total_seconds() / 3600
            if salida > hora_limite_diurna:
                self.horas_extras_diurnas = (min(salida, hora_limite_nocturna) - hora_limite_diurna).total_seconds() / 3600

        if salida > hora_limite_nocturna:
            self.horas_normales_nocturnas = (salida - max(hora_limite_nocturna, entrada)).total_seconds() / 3600

        # Aplicar recargos
        if self.es_festivo():
            self.recargo_festivo = (self.horas_normales_diurnas + self.horas_extras_diurnas) * 0.8  # 80%
            self.recargo_festivo += self.horas_extras_nocturnas * 1.5  # 150% para horas extras nocturnas
        elif self.es_dominical():
            self.recargo_dominical = (self.horas_normales_diurnas + self.horas_extras_diurnas) * 0.8  # 80%
            self.recargo_dominical += self.horas_extras_nocturnas * 1.5  # 150% para horas extras nocturnas
        else:
            self.recargo_nocturno = self.horas_normales_nocturnas * 0.35  # 35%

    def obtener_resultados(self):
        self.calcular_horas()
        return {
            'horas_normales_diurnas': self.horas_normales_diurnas,
            'horas_normales_nocturnas': self.horas_normales_nocturnas,
            'horas_extras_diurnas': self.horas_extras_diurnas,
            'horas_extras_nocturnas': self.horas_extras_nocturnas,
            'recargo_dominical': self.recargo_dominical,
            'recargo_festivo': self.recargo_festivo,
            'recargo_nocturno': self.recargo_nocturno,
        }
