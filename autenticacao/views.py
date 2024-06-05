from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from vencimento.views import lista_lotes
from .models import AcessoCasa
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

    def form_valid(self, form):
        # Login do usuário
        login(self.request, form.get_user())

        # Verificar se o usuário tem acesso à casa selecionada
        casa = form.cleaned_data['casa']
        if AcessoCasa.objects.filter(usuario=self.request.user, casa=casa, pode_acessar=True).exists():
            self.request.session['casa_id'] = casa.id
            return redirect(self.get_success_url())
        else:
            # Limpar a sessão aqui para remover qualquer estado anterior potencialmente problemático
            logout(self.request)  # Isto também limpará a sessão
            form.add_error(None, "Você não tem acesso a esta casa.")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('vencimento:lista_lotes')



