from celery import shared_task
from django.core.mail import send_mail
from .models import Lote, ConfiguracaoGlobal
from django.utils import timezone
from datetime import timedelta

@shared_task
def verificar_e_enviar_notificacoes():
    config = ConfiguracaoGlobal.objects.first()
    if config:
        dias_para_vencimento_proximo = config.dias_para_vencimento_proximo
        email_notificacoes = config.email_notificacoes
        data_proximo = timezone.now().date() + timedelta(days=dias_para_vencimento_proximo)

        lotes_proximos = Lote.objects.filter(
            data_validade__lte=data_proximo,
            notificacao_enviada=False
        )

        for lote in lotes_proximos:
            send_mail(
                'Notificação de Vencimento Iminente',
                f'O lote {lote.identificacao} está próximo de vencer em {lote.data_validade}.',
                'servicedesk@rioscenarium.com.br',  # O e-mail do remetente
                [email_notificacoes],  # Usando o e-mail global de notificações
                fail_silently=False,
            )
            lote.notificacao_enviada = True  # Marcar a notificação como enviada
            lote.save()
