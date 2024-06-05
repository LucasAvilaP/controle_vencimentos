from django.contrib import admin
from .models import Produto, Lote, Categoria, ConfiguracaoGlobal, Casa, HistoricoLog
from autenticacao.models import AcessoCasa



@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome',)  # Aqui você pode adicionar mais campos do modelo Produto se desejar


admin.site.register(Categoria)


@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    list_display = ['email_notificacoes']





@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['identificacao', 'produto', 'quantidade', 'categoria', 'data_chegada', 'data_validade', 'esta_vencido']
    search_fields = ['identificacao', 'produto__nome', 'categoria__nome']
    list_filter = ['categoria', 'data_validade'] 

    def esta_vencido(self, obj):
        return obj.esta_vencido()
    esta_vencido.boolean = True
    esta_vencido.short_description = 'Vencido?'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        casa_id = request.session.get('casa_id')  # Obter ID da casa da sessão
        if casa_id:
            return qs.filter(casa__id=casa_id)  # Filtra lotes com base na casa na sessão
        else:
            if request.user.is_superuser:
                return qs  # Superusuários veem todos os lotes se não houver casa na sessão
            else:
                # Usuários regulares veem apenas lotes das casas às quais têm acesso
                return qs.filter(casa__in=AcessoCasa.objects.filter(usuario=request.user, pode_acessar=True).values_list('casa_id', flat=True))
        return qs.none()  # Caso de backup, não mostra nada

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "casa":
            if request.user.is_superuser:
                kwargs["queryset"] = Casa.objects.all()
            else:
                kwargs["queryset"] = Casa.objects.filter(
                    id__in=AcessoCasa.objects.filter(usuario=request.user, pode_acessar=True).values_list('casa_id', flat=True)
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(HistoricoLog)
class HistoricoLogAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'acao', 'descricao', 'data_hora']
    search_fields = ['usuario__username', 'descricao', 'lote__identificacao']
    list_filter = ['acao', 'data_hora', 'casa']

    def has_add_permission(self, request):
        # Desabilitar a adição de logs manualmente
        return False

    def has_change_permission(self, request, obj=None):
        # Desabilitar a modificação de logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Desabilitar a exclusão de logs
        return False