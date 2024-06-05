from celery import shared_task
from django.core.mail import send_mail
from .models import Lote
from django.utils import timezone
from datetime import timedelta

@shared_task
def check_lotes_proximos_vencimento():
    data_limite = timezone.now().date() + timedelta(days=30)
    # Selecionar lotes cuja data de validade é menor ou igual a 30 dias no futuro e que não tenham enviado notificação
    lotes = Lote.objects.filter(data_validade__lte=data_limite, notificacao_enviada=False).select_related('casa')

    for lote in lotes:
        if lote.casa and lote.casa.email_contato:  # Verifica se a casa tem um e-mail definido
            send_mail(
                'Lote Próximo do Vencimento',
                f'O lote {lote.identificacao} do produto {lote.produto.nome} está próximo de vencer.',
                'servicedesk@rioscenarium.com.br',
                [lote.casa.email_contato],  # Enviar e-mail para o contato da casa atual
                fail_silently=False,
            )
            lote.notificacao_enviada = True  # Marcar o lote como notificado
            lote.save()
