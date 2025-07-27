from django import template

register = template.Library()

@register.filter
def get_tipo_badge(tipo_hora):
    badge_classes = {
        'DI': 'primary',    # Diurno ordinario
        'NO': 'dark',       # Nocturno ordinario
        'DO': 'info',       # Dominical
        'FE': 'warning',    # Festivo
        'EXTRA_DI': 'success',  # Extra diurno
        'EXTRA_NO': 'danger'    # Extra nocturno
    }
    return badge_classes.get(tipo_hora, 'secondary')
