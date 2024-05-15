from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controle_vencimentos.settings')

app = Celery('controle_vencimentos')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()




app.conf.beat_schedule = {
    'verificar-e-enviar-notificacoes-diariamente': {
        'task': 'controle_vencimentos.tasks.verificar_e_enviar_notificacoes',
        'schedule': crontab(hour=0, minute=0),  # Executa meia-noite todos os dias
    },
}
