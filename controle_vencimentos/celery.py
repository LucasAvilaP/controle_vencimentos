from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

app = Celery('projeto')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()




app.conf.beat_schedule = {
    'check_lotes_proximos_vencimento_every_day': {
        'task': 'projeto.tasks.check_lotes_proximos_vencimento',
        'schedule': crontab(hour=0, minute=0),  # Executa à meia-noite todos os dias
    },
}
