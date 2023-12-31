import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'v1_bill.settings')

app = Celery('v1_bill')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.conf.beat_schedule = {
    'zoho-token-refresh': {
        'task': 'settings.tasks.zohoTokenRefresh',  # Task name
        'schedule': crontab(minute='*/50'),  # Run every 50 minutes
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
