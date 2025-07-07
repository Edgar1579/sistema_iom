from django.shortcuts import render
from configuracion.models import Slider
def principal(request):
    titulo="Bienvenido"
    sliders= Slider.objects.filter(estado=True)
    context={
        "titulo": titulo,
        "sliders": sliders,
    }
    return render(request, "index.html", context)
   
    def home_view(request):
       return render(request, 'partials/home.html')