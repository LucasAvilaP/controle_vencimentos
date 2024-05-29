from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from vencimento.views import lista_lotes
from vencimento.models import Casa
from django.utils.deprecation import MiddlewareMixin
from .forms import CustomLoginForm


class CasaMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_anonymous:
            if hasattr(request.user, 'profile') and request.user.profile.casa:
                request.session['casa_id'] = request.user.profile.casa.id

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'autenticacao/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('vencimento:lista_lotes')

    def form_valid(self, form):
        # Armazenar a casa escolhida na sessão após login bem-sucedido
        casa = form.cleaned_data['casa']
        self.request.session['casa_id'] = casa.id
        return super().form_valid(form)



