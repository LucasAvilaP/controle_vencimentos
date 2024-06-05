

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class ConfiguracaoGlobal(models.Model):
    email_notificacoes = models.EmailField(verbose_name="E-mail para Notificações")
    dias_para_vencimento_proximo = models.PositiveIntegerField(default=30, help_text="Número de dias para considerar um lote próximo do vencimento.")
    
    def __str__(self):
        return "Configurações Globais"


class Casa(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=100)
    email_contato = models.EmailField(null=True)


    class Meta:
        permissions = [
            ('can_transfer', 'Can perform lot transfers'),  # Permissão para transferir lotes
        ]

    def __str__(self):
        return self.nome



class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='lotes')
    identificacao = models.CharField(max_length=50, verbose_name="Identificação do Lote")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    data_chegada = models.DateField()
    data_validade = models.DateField()
    casa = models.ForeignKey(Casa, on_delete=models.CASCADE, related_name='lotes', null=True)
    casa_destinada = models.ForeignKey(Casa, on_delete=models.CASCADE, related_name='lotes_destined', verbose_name="Casa Destinada", null=True)  # Casa para a qual o lote é destinado
    notificacao_enviada = models.BooleanField(default=False)

    def registrar_saida(self, quantidade):
        """Registra a saída de uma quantidade de produtos do lote."""
        if quantidade <= self.quantidade:
            self.quantidade -= quantidade
            self.save()
            return True
        return False

    def esta_vencido(self):
        return self.data_validade < timezone.now().date()

    def esta_proximo_vencimento(self):
        configuracao = ConfiguracaoGlobal.objects.first()
        if configuracao:
            dias_para_vencimento_proximo = configuracao.dias_para_vencimento_proximo
            limite_proximo = timezone.now().date() + timedelta(days=dias_para_vencimento_proximo)
            return self.data_validade <= limite_proximo
        return False

    def esta_urgente(self):
        configuracao = ConfiguracaoGlobal.objects.first()
        dias_para_urgencia = 30  # Definindo 30 dias para a urgência
        data_urgencia = timezone.now().date() + timedelta(days=dias_para_urgencia)
        return self.data_validade <= data_urgencia and not self.esta_vencido()

    def __str__(self):
        casa_destinada_nome = self.casa_destinada.nome if self.casa_destinada else "Nenhuma"
        return f'{self.identificacao.upper()} - Lote de {self.produto.nome} - Quantidade: {self.quantidade} - Validade: {self.data_validade} - Destinado a {casa_destinada_nome}'
    

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"


    
class HistoricoLog(models.Model):
    TIPO_ACAO = (
        ('AD', 'Adicionar'),
        ('TR', 'Transferir'),
        ('DE', 'Deletar'),
        ('RS', 'Registrar Saída'),
    )

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    lote = models.ForeignKey('Lote', on_delete=models.SET_NULL, null=True, blank=True)
    casa = models.ForeignKey('Casa', on_delete=models.SET_NULL, null=True, verbose_name="Casa Relacionada")  # Adicionando relação com Casa
    acao = models.CharField(max_length=2, choices=TIPO_ACAO)
    descricao = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} realizou {self.get_acao_display()} em {self.data_hora.strftime("%d/%m/%Y %H:%M")}'