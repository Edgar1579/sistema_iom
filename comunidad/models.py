from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import holidays
from django.templatetags.static import static
from datetime import datetime, time, timedelta

def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.documento}.{ext}"
    return f"comunidad/usuarios/{filename}"

class Usuario(models.Model):
    primer_nombre = models.CharField(max_length=45, verbose_name="Primer Nombre")
    segundo_nombre = models.CharField(max_length=45, verbose_name="Segundo Nombre", blank=True, null=True)
    primer_apellido = models.CharField(max_length=45, verbose_name="Primer Apellido")
    segundo_apellido = models.CharField(max_length=45, verbose_name="Segundo Apellido")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    imagen = models.ImageField(upload_to=get_image_filename, blank=True, null=True, default="comunidad/default-user.jpeg")
    correo = models.EmailField(max_length=50, verbose_name="Correo")

    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', _("Cédula")
        CEDULA_EXTRANJERIA = 'CE', _("Cédula de Extrangería")

    tipo_documento = models.CharField(max_length=2, choices=TipoDocumento.choices, verbose_name="Tipo de Documento")
    documento = models.PositiveIntegerField(verbose_name="Documento", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)
    departamento = models.CharField(max_length=50, verbose_name="Departamento", blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    cargo = models.CharField(max_length=50, verbose_name="Cargo", blank=True, null=True)

    def clean(self):
        self.primer_nombre = self.primer_nombre.title()

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    class Meta:
        verbose_name_plural = "Usuarios"

    @property
    def full_name(self):
        if self.segundo_nombre:
            return f"{self.primer_nombre} {self.segundo_nombre} {self.primer_apellido} {self.segundo_apellido}"
        else:
            return f"{self.primer_nombre} {self.primer_apellido} {self.segundo_apellido}"

class ConfiguracionGeneral(models.Model):
    año = models.PositiveIntegerField(unique=True)
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2)

    def valor_hora(self):
        return self.salario_minimo / Decimal('240')

    def __str__(self):
        return f"Configuración {self.año}"




class RegistroHoras(models.Model):
    # Valores constantes
    SALARIO_MINIMO = Decimal('1423500')
    AUXILIO_TRANSPORTE = Decimal('200000')
    HORAS_TRABAJADAS_MES = Decimal('220')
    JORNADA_NORMAL = Decimal('8')  # 8 horas diarias normales

    # Valores por hora
    HORA_NORMAL_DIURNA = Decimal('6189')         # 6:00-19:00
    HORA_NORMAL_NOCTURNA = Decimal('8355')       # 19:00-6:00 (35% recargo)
    HORA_EXTRA_DIURNA = Decimal('7736')          # 25% recargo
    HORA_EXTRA_NOCTURNA = Decimal('10831')       # 75% recargo
    HORA_DOMINICAL_DIURNA = Decimal('10831')     # 75% recargo
    HORA_DOMINICAL_NOCTURNA = Decimal('12997')   # 110% recargo
    HORA_FESTIVO_DIURNA = Decimal('10831')       # 75% recargo
    HORA_FESTIVO_NOCTURNA = Decimal('12997')     # 110% recargo

    # Campos del modelo
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    # Campos de cálculo
    horas_normales_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_normales_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_diurnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_extras_nocturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_nocturno = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_dominical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recargo_festivo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pago_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def es_domingo(self):
        return self.fecha.weekday() == 6  # 6 es domingo

    def es_festivo(self):
        festivos = holidays.Colombia(years=self.fecha.year)
        return self.fecha in festivos

    def es_noche(self, hora_time):
        """Determina si es horario nocturno (10pm-6am)"""
        return hora_time < time(6, 0) or hora_time >= time(22, 0)

    def calcular_horas(self):
        entrada = datetime.combine(self.fecha, self.hora_entrada)
        salida = datetime.combine(self.fecha, self.hora_salida)

        if salida < entrada:
            salida += timedelta(days=1)  # Para turnos que pasan la medianoche

        # Reiniciar contadores
        self.horas_normales_diurnas = Decimal('0')
        self.horas_normales_nocturnas = Decimal('0')
        self.horas_extras_diurnas = Decimal('0')
        self.horas_extras_nocturnas = Decimal('0')
        self.recargo_nocturno = Decimal('0')
        self.recargo_dominical = Decimal('0')
        self.recargo_festivo = Decimal('0')

        es_dominical = self.es_domingo()
        es_festivo = self.es_festivo()

        hora_actual = entrada
        while hora_actual < salida:
            siguiente = min(hora_actual + timedelta(hours=1), salida)
            duracion = Decimal((siguiente - hora_actual).total_seconds() / 3600)
            hora_time = hora_actual.time()
            es_nocturna = self.es_noche(hora_time)

            # Lógica de clasificación
            if es_festivo or es_dominical:
                if es_nocturna:
                    self.horas_normales_nocturnas += duracion
                else:
                    self.horas_normales_diurnas += duracion
                
                if es_festivo:
                    self.recargo_festivo += duracion
                else:
                    self.recargo_dominical += duracion
            else:  # Día normal
                if (hora_actual - entrada).total_seconds() / 3600 > 8:  # Horas extras
                    if es_nocturna:
                        self.horas_extras_nocturnas += duracion
                    else:
                        self.horas_extras_diurnas += duracion
                else:  # Horas normales
                    if es_nocturna:
                        self.horas_normales_nocturnas += duracion
                        self.recargo_nocturno += duracion
                    else:
                        self.horas_normales_diurnas += duracion

            hora_actual = siguiente

    def calcular_pago_total(self):
        total = Decimal('0')
        es_dominical = self.es_domingo()
        es_festivo = self.es_festivo()

        if es_festivo:
            # Todos los cálculos con valores festivos
            total += self.horas_normales_diurnas * self.HORA_FESTIVO_DIURNA
            total += self.horas_normales_nocturnas * self.HORA_FESTIVO_NOCTURNA
        elif es_dominical:
            # Todos los cálculos con valores dominicales
            total += self.horas_normales_diurnas * self.HORA_DOMINICAL_DIURNA
            total += self.horas_normales_nocturnas * self.HORA_DOMINICAL_NOCTURNA
        else:  # Día normal
            # Cálculos normales con horas extras
            total += self.horas_normales_diurnas * self.HORA_NORMAL_DIURNA
            total += self.horas_normales_nocturnas * self.HORA_NORMAL_NOCTURNA
            total += self.horas_extras_diurnas * self.HORA_EXTRA_DIURNA
            total += self.horas_extras_nocturnas * self.HORA_EXTRA_NOCTURNA
            total += self.recargo_nocturno * (self.HORA_NORMAL_NOCTURNA - self.HORA_NORMAL_DIURNA)

        self.pago_total = total.quantize(Decimal('0.01'))
        return self.pago_total

    def save(self, *args, **kwargs):
        self.calcular_horas()
        self.calcular_pago_total()
        super().save(*args, **kwargs)








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
