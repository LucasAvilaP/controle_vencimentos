from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from vencimento.views import lista_lotes

class CustomLoginView(LoginView):
    template_name = 'autenticacao/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('vencimento:lista_lotes')  # Ajuste conforme necessário

