# vencimentos/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from vencimento.views import transferencia_lotes_view

app_name = 'vencimento'

urlpatterns = [
    path('', login_required(views.lista_lotes), name='lista_lotes'),
    path('vencidos/', views.lotes_vencidos, name='lotes_vencidos'),
    path('adicionar/', views.adicionar_lote, name='adicionar_lote'),
    path('exportar-lotes/', views.exportar_lotes_excel, name='exportar_lotes_excel'),
    path('registrar-saida/', views.registrar_saida, name='registrar_saida'),  # URL para o registro de saída
    path('transferencia/', views.transferencia_lotes_view, name='transferencia_lotes_view'),
    path('deletar_lote/', views.deletar_lote_view, name='deletar_lote'),
    path('devolucao_view/', views.devolucao_view, name='devolucao_view'),

]

