import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jpgtopdf.settings')

app = Celery('jpgtopdf')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'cleanup-stuck-uploads': {
        'task': 'converter.tasks.cleanup_stuck_uploads',
        'schedule': 10.0,  # Run every 10 seconds
    },
} 