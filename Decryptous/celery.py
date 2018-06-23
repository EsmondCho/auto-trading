from __future__ import absolute_import
import os
from celery import Celery
from datetime import timedelta
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Decryptous.settings')

app = Celery('Decryptous')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    BROKER_URL='pyamqp://guest@localhost//',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_RESULT_BACKEND="django-db",
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE={
        'tube_process_manage': {
            'task': 'tube.tasks.tube_process_manage',
            'schedule': timedelta(seconds=10),
            'args': ()
        },
        'check_orderbook': {
            'task': 'exchange.tasks.check_orderbook',
            'schedule': timedelta(seconds=10),
            'args': ()
        },
        'check_account': {
            'task': 'exchange.tasks.check_account',
            'schedule': timedelta(seconds=10),
            'args': ()
        }
    }
)
