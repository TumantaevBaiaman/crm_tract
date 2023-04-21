import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_tract.settings")

app = Celery("crm_tract")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "sample_task": {
        "task": "apps.account.tasks.sample_task",
        # "task": "apps.account.tasks.send_monthly_invoice",
        "schedule": crontab(minute="*/1"),
        # 'schedule': time(hour=9, minute=0),
    },
}
app.autodiscover_tasks()
