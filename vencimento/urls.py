# vencimentos/urls.py

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.lista_lotes), name='lista_lotes'),
    path('vencidos/', views.lotes_vencidos, name='lotes_vencidos'),
    path('adicionar/', views.adicionar_lote, name='adicionar_lote'),
    path('exportar-lotes/', views.exportar_lotes_excel, name='exportar_lotes_excel'),
    path('deletar_lote/', views.deletar_lote, name='deletar_lote'),

]

