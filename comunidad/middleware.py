from django.shortcuts import redirect

class AdminRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/adm/') or request.path.startswith('/admin/'):
            if not request.user.is_staff:
                return redirect('/')  # Redirige a la página de inicio
        response = self.get_response(request)
        return response
   