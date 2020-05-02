import os

from django.apps import apps
from django.conf import settings

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bol.settings')

app = Celery('app', broker=settings.CELERY_BROKER_URL)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
