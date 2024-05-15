from django.contrib import admin
from .models import Produto, Lote, Categoria, ConfiguracaoGlobal, Casa



@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome',)  # Aqui você pode adicionar mais campos do modelo Produto se desejar


admin.site.register(Categoria)


@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    list_display = ['email_notificacoes']


@admin.register(Casa)
class CasaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'endereco']
    search_fields = ['nome', 'endereco']



@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['identificacao', 'produto', 'quantidade', 'categoria', 'data_chegada', 'data_validade']
    search_fields = ['identificacao', 'produto__nome', 'categoria__nome']
    list_filter = ['categoria', 'data_validade'] 

    # Método para mostrar se o lote está vencido
    def esta_vencido(self, obj):
        return obj.esta_vencido()
    esta_vencido.boolean = True  # Isto fará com que apareça um ícone em vez de True/False
